"""
Ορίζει το μοντέλο των ραντεβού και το API διαχείρισης των δεδομένων.

Πιθανές βελτιώσεις:
1. Ασύγχρονη λειτουργία ενημέρωσης της βάσης δεδομένων
2. Ενημέρωση του cache και των συνδρομητών με πιο αποτελεσματικό τρόπο
3. Οι συναρτήσεις συνήθους περίπτωσης να δίνουν δυνατότητα αναζήτησης στο cache
   (πιθανώς με δυαδική αναζήτηση στην περίπτωση της ημερομηνίας)
"""

from __future__ import annotations
from datetime import datetime, timedelta
from typing import Any, Generator

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, func

from .session import Base, session
from ..controller.logging import Logger

from typing import Protocol

logger = Logger("appointment-model")
PERIOD = timedelta(hours=2)


class Subscriber(Protocol):
    """
    Interface για όλα τα στοιχεία που κάνουν subscribe για να
    ενημερώνονται όταν γίνονται σημαντικές αλλαγές στην  βάση
    δεδομένων
    """

    def subscriber_update(self):
        pass


class Cache:

    def __init__(self, model: AppointmentModel):
        self.data: dict[int, list[Appointment]] = {}
        self.id_index: dict[int, int] = {}
        self.start: int
        self.end: int
        self.now = datetime.now().replace(
            hour=9, minute=0, second=0, microsecond=0
        )  # TODO Config setting
        self.min_index: int
        self.max_index: int
        self.model = model

    def add(self, appointment: Appointment) -> bool:
        hit = True
        index = self.hash(appointment.date)
        value = self.data.get(index)
        if value is None:
            hit = False
            self.data.setdefault(index, [])
        self.data[index].append(appointment)
        self.id_index[appointment.id] = index
        return hit

    def update(self, appointment, old_date: datetime | None = None) -> bool:
        if old_date:
            period = self.data[self.hash(old_date)]
        else:
            period = self.data[self.id_index[appointment.id]]

        for i, existing_appointment in enumerate(period):
            if existing_appointment.id == appointment.id:
                period[i] = appointment
                return True
        return False

    def delete(self, appointment: Appointment) -> bool:
        date_index = self.hash(appointment.date)
        try:
            self.data[date_index].remove(appointment)
            self.id_index.pop(appointment.id)
            return True
        except ValueError:
            return False

    def lookup(self, date_index: int) -> list[Appointment]:
        values = self.data.get(date_index)
        if values is None:
            self.query_by_date(self.unhash(date_index), self.unhash(date_index + 1))
            return self.lookup(date_index)
        return values

    def lookup_date(self, date: datetime) -> list[Appointment]:
        return self.lookup(self.hash(date))

    def lookup_id(self, id: int) -> Appointment | None:
        appointments = self.data.get(self.id_index[id])

        if appointments is None:
            return None

        for appointment in appointments:
            if appointment.id == id:
                return appointment

        return None

    def hash(self, date: datetime) -> int:
        return (date - self.now) // PERIOD

    def unhash(self, index: int) -> datetime:
        return self.now + index * PERIOD

    def iter_date_range(
        self, start: datetime, end: datetime | None
    ) -> Generator[Appointment, None, None]:
        if end is None:
            end = start
        self.start = self.hash(start)
        self.end = self.hash(end)
        return self.__next__()

    def __iter__(self) -> Generator[Appointment, None, None]:
        raise Exception("Use Cache.iter_date_range instead")

    def __next__(self) -> Generator[Appointment, None, None]:
        for i in range(self.start, self.end + 1):
            for appointment in self.lookup(i):
                yield appointment

    def query_by_date(self, start: datetime, end: datetime):
        result = self.model.get_appointments_from_to_date(start, end)
        if len(result) == 0:
            for i in range(self.hash(start), self.hash(end) + 1):
                self.data.setdefault(self.hash(start), [])
        for appointment in result:
            self.add(appointment)

    def query_by_id(self, id: int):
        appointment = self.model.get_appointment_by_id(id)
        if appointment is None:
            return
        self.query_by_date(appointment.date, appointment.end_date)


class Appointment(Base):
    """
    Ορισμός της οντότητας "ραντεβού"
        id: Εσωτερικός μοναδικός αριθμός, παράγεται από την βάση δεδομένων
        date: Ημερομηνία του ραντεβού, μικρότερες μονάδες από τα λεπτά αγνοούνται
        is_alerted: Εάν ο πελάτης έχει ενημερωθεί με email
        customer_id: Εξωτερικό κλειδί, id του πελάτη που σχετίζεται με το ραντεβού

        customer: Ο πελάτης που έχει σχέση με το ραντεβού, ορίζεται από το customer_id
    """

    __tablename__ = "appointment"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    date: Mapped[datetime] = mapped_column(nullable=False, unique=True, index=True)
    is_alerted: Mapped[bool] = mapped_column(default=False)
    duration: Mapped[timedelta] = mapped_column(default=timedelta(minutes=20))
    customer_id: Mapped[int | None] = mapped_column(
        ForeignKey("customer.id"), nullable=True
    )
    employee_id: Mapped[int] = mapped_column(default=0)

    customer = relationship(
        "Customer",
        back_populates="appointments",
        foreign_keys="[Appointment.customer_id]",
    )

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return (
            f"Appointment(id={self.id}, date={self.date}, "
            f"customer_id={self.customer_id}, duration=({self.duration}))"
        )

    @property
    def values(self) -> tuple[int, datetime, bool, timedelta, int | None]:
        return (self.id, self.date, self.is_alerted, self.duration, self.customer_id)

    @property
    def end_date(self) -> datetime:
        """
        Υπολογίζει την ακριβή ημερομηνία που θα πρέπει να έχει
        ολοκληρωθεί το ραντεβού
        """
        return self.date + self.duration

    @property
    def time_to_appointment(self) -> timedelta:
        """
        Υπολογίζει τον χρόνο που απομένει μέχρι το ραντεβού
        """
        return self.date - datetime.now()

    def overlap(self, other: Appointment):
        if self.id == other.id:
            return False
        return not (self.date >= other.end_date or self.end_date <= other.date)

    def time_between_appointments(self, appointment: Appointment) -> timedelta:
        """
        Υπολογίζει τον χρόνο μεταξύ 2 ραντεβού λαμβάνοντας υπόψην
        τον χρόνο ολοκλήρωσης αυτών
        """
        if self.date > appointment.date:
            return self.date - appointment.end_date
        return appointment.date - self.end_date

    def time_between_dates(self, date: datetime) -> timedelta:
        """
        Βοηθητική συνάρτηση υπολογισμού χρόνου με αγνωστικό
        χαρακτήρα
        """
        return abs(self.date - date)

    def to_dict(self):
        """
        Μετατροπή του τύπου Appointment σε τύπο dict
        """
        dict_: dict[str, Any] = {}
        dict_.update(self.__dict__)
        for k in dict_.keys():
            if k.startswith("_"):
                dict_.pop(k)


class AppointmentModel:
    """
    Ορίζει το μοντέλο των δεδομένων και διαχειρίζεται την αναζήτηση και
    ανάκτηση πληροφορίας.

        appointments: Το cache με όλα τα ραντεβού που διατηρείται στην μνήμη για γρήγορη ανάκτηση
        subscribers: Όλα τα στοιχεία του view που ενημερώνονται όταν αλλάζουν τα δεδομένα στην βάση
        session: Η σύνδεση με την βάση δεδομένων. Το πρόγραμμα χρησιμοποιεί μόνο μια σύνδεση που ορίζεται στο sessions.py

    """

    _instance = None
    session = session
    # appointments: list[Appointment] = []
    subscribers: list[Subscriber] = []
    max_id = 0
    cache: Cache

    def __new__(cls, *args, **kwargs) -> AppointmentModel:
        if cls._instance is None:
            cls._instance = super(AppointmentModel, cls).__new__(cls, *args, **kwargs)
            cls.max_id = session.query(func.max(Appointment.id)).scalar()
            if cls.max_id is None:
                cls.max_id = 0

            cls.cache = Cache(cls._instance)

            cls.now = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
            cls.min_date = cls.now - timedelta(days=10)
            cls.max_date = cls.now + timedelta(days=10)

            appointments = (
                session.query(Appointment)
                .filter(
                    Appointment.date >= cls.min_date, Appointment.date <= cls.max_date
                )
                .order_by(Appointment.date)
                .all()
            )

            while appointments:
                appointment = appointments.pop()
                cls.cache.add(appointment)

        return cls._instance

    def has_overlap(self, appointment: Appointment) -> bool:
        for existing_appointment in self.cache.iter_date_range(
            appointment.date, appointment.end_date
        ):
            if existing_appointment.overlap(appointment):
                return True
        return False

    def add_appointment(self, appointment: Appointment) -> int | None:
        """
        Προσθήκη νέου ραντεβού στην βάση δεδομένων και ενημέρωση του cache
        """
        logger.log_info(f"Excecuting creation of new {appointment=}")

        # TODO Έλεγχος για overlap στις ημερομηνίες. Πρέπει η καινούρια
        # ημερομηνία και η διάρκεια να μην είναι μεταξύ date, end_date

        if self.has_overlap(appointment):
            logger.log_warn(f"{appointment} overlaps with existing")
            return None

        # Προσθήκη στην βάση δεδομένων
        try:
            self.session.add(appointment)
            self.session.commit()
            self.max_id += 1
            logger.log_info(f"Assigned id={self.max_id}")
        except Exception as e:
            logger.log_error(str(e))
            self.session.rollback()
            return None

        # Έλεγχος ορθής λειτουργίας
        appointment_with_id = (
            self.session.query(Appointment)
            .filter(Appointment.id == self.max_id)
            .first()
        )
        if appointment_with_id is None:
            logger.log_error("Failed to retrieve appointment id after insertion")
            raise Exception(f"DB Failure on inserting {appointment}")

        # Ενημέρωση του cache
        if appointment_with_id:
            self.cache.add(appointment_with_id)

        # Ενημέρωση των subscribers
        self.update_subscribers()

        # Επιστροφή του μοναδικού id για περεταίρω διαχείρηση δεδομένων
        return appointment_with_id.id

    def is_similar(self, appointment1: Appointment, appointment2: Appointment):
        return all(
            (
                appointment1.id == appointment2.id,
                appointment1.date == appointment2.date,
                appointment1.is_alerted == appointment2.is_alerted,
                appointment1.duration == appointment2.duration,
            )
        )

    def update_appointment(
        self, appointment: Appointment, customer_id: int | None = None
    ) -> bool:
        """
        Ενημέρωση στοιχείων ραντεβού στην βάση δεδομένων και ενημέρωση cache
        Επιβάλλει να υπάρχει id στο ραντεβού προς ενημέρωση

        Επιστρέφει boolean επιτυχίας
        """
        logger.log_info(f"Excecuting update of {appointment}")

        if self.has_overlap(appointment):
            logger.log_warn(f"{appointment} overlaps with existing")
            return False

        if appointment.id is None:
            logger.log_warn("Appointment must have an id")
            return False

        old_appointment = (
            session.query(Appointment).filter_by(id=appointment.id).first()
        )

        if old_appointment is None:
            logger.log_warn("Appointment was not found in database")
            return False

        if isinstance(customer_id, int):
            logger.log_info(f"Adding {customer_id=} to {appointment.id=}")
            old_appointment.customer_id = customer_id

        old_appointment.date = appointment.date
        old_appointment.duration = appointment.duration
        old_appointment.is_alerted = appointment.is_alerted
        logger.log_debug(f"{old_appointment=}")
        # Ενημέρωση του στοιχείου
        try:
            self.session.commit()
        except Exception as e:
            logger.log_error(str(e))
            self.session.rollback()
            return False

        # Ενημέρωση του cache
        self.cache.update(old_appointment, appointment.date)

        # Ενημέρωση των subscribers
        self.update_subscribers()
        return True

    def delete_appointment(self, appointment: Appointment) -> bool:
        logger.log_info(f"Excecuting deletion of {appointment=}")

        if appointment.id is None:
            logger.log_error("Appointment for deletion must have an id")
            return False

        appointment_to_delete = self.get_appointment_by_id(appointment.id)
        if appointment_to_delete is None:
            logger.log_error("Failed to locate appointment in db")
            return False

        # Διαγραφή του στοιχείου από την βάση δεδομένων
        try:
            self.session.delete(appointment_to_delete)
            self.session.commit()
        except Exception as e:
            logger.log_error(str(e))
            self.session.rollback()
            return False

        # Ενημέρωση του cache
        self.cache.delete(appointment_to_delete)
        self.max_id = self.find_max_id()

        # Ενημέρωση των subscribers
        self.update_subscribers()
        return True

    def get_appointments(self) -> dict[int, list[Appointment]]:
        """
        Διπλή λειτουργία ανάκτησης στοιχείων απο την βάση δεδομένων και
        διάθεσης του cache στις σχετικές μονάδες.
        """
        logger.log_debug(f"Excecuting query of all appointments")
        return self.cache.data

    def get_appointment_by_id(self, appointment_id: int) -> Appointment | None:
        """
        Συνάρτηση συνήθους περίπτωσης
        """
        logger.log_debug(f"Excecuting query of appointment by id={appointment_id}")
        return self.session.query(Appointment).filter_by(id=appointment_id).first()

    def get_appointment_by_date(self, date: datetime) -> Appointment | None:
        """
        Συνάρτηση συνήθους περίπτωσης
        """
        logger.log_debug(f"Excecuting query of appointment by {date=}")
        return self.session.query(Appointment).filter_by(date=date).first()

    def get_appointments_from_to_date(
        self, from_date: datetime, to_date: datetime
    ) -> list[Appointment]:

        result = (
            self.session.query(Appointment)
            .filter(Appointment.date >= from_date, Appointment.date < to_date)
            .all()
        )

        return result

    def get_appointments_by_period(self, date: datetime):

        return [*self.cache.iter_date_range(date, date)]

    def get_time_between_appointments(
        self,
        start_date: datetime = datetime.now(),
        end_date: datetime = datetime.now() + timedelta(days=1),
        minumum_free_period: timedelta = PERIOD,
    ) -> list[tuple[datetime, timedelta]]:
        """
        Συνάρτηση αναζήτησης κενού χρόνου μεταξύ των ραντεβού. Σκοπός είναι
        ο χρήστης να μπορεί γρήγορα να βρεί σε ποιές ημερομηνίες μπορεί να
        εξυπηρετήσει τον πελάτη με βάση τον προβλεπόμενο χρόνο που απατείται
        για τις ανάγκες του

        Η παράμετρος include_start ορίζει αν η αρχική ημερομηνία θα υπολογιστεί
        ώς "ραντεβού".
        """
        logger.log_debug(f"Excecuting calculation of time between appointments")

        # Για λόγους στατιστικών στοιχείων, εάν δεν δωθεί αρχική ημερομηνία,
        # υπολογίζει από την αρχή

        result_date: list[datetime] = [start_date]
        result_duration: list[timedelta] = []

        for appointment in self.cache.iter_date_range(start_date, end_date):

            # Αγνοεί τα ραντεβού πριν και μετά την ημερομηνία που θέλει ο χρηστης
            if appointment.end_date < start_date:
                continue

            if appointment.date >= end_date:
                break

            previous_date = result_date[-1]
            next_date = appointment.date
            diff = next_date - previous_date

            if diff < minumum_free_period:
                result_date[-1] = appointment.end_date
                continue

            if diff >= minumum_free_period:
                result_date.append(appointment.end_date)
                result_duration.append(diff)

        return [*zip(result_date, result_duration)]

    def add_subscriber(self, subscriber: Subscriber):
        """
        Δήλωση των subscribers στην λίστα προς ενημέρωση
        """
        # Έλεγχος εάν το αντικείμενο υλοποιεί την κατάλληλη διεπαφή
        if not hasattr(subscriber, "subscriber_update"):
            logger.log_error("Object is not a subscriber")
            raise Exception("Subscribers must implement the subscriber interface")

        logger.log_info(f"Adding {subscriber=}")
        self.subscribers.append(subscriber)

    def update_subscribers(self):
        """
        Ενημέρωση των δηλωμένων subscribers
        """
        logger.log_info(
            f"Excecuting notification of {len(self.subscribers)} subscribers"
        )
        for subscriber in self.subscribers:
            logger.log_debug(str(subscriber))
            subscriber.subscriber_update()

    def find_max_id(self) -> int:
        result = self.session.query(func.max(Appointment.id)).scalar()
        if result is None:
            return 0
        return result
