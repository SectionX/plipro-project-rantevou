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
from collections import defaultdict

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, func

from .session import Base, session
from . import customer
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
    appointments: defaultdict[int, list[Appointment]] = defaultdict(list)
    subscribers: list[Subscriber] = []
    max_id = 0

    def __new__(cls, *args, **kwargs) -> AppointmentModel:
        if cls._instance is None:
            cls._instance = super(AppointmentModel, cls).__new__(cls, *args, **kwargs)

            cls.max_id = session.query(func.max(Appointment.id)).scalar()
            if cls.max_id is None:
                cls.max_id = 0

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
                index = (appointment.date - cls.now) // PERIOD
                cls.appointments.setdefault(index, [])
                cls.appointments[index].append(appointment)

        return cls._instance

    def add_appointment(self, appointment: Appointment) -> int | None:
        """
        Προσθήκη νέου ραντεβού στην βάση δεδομένων και ενημέρωση του cache
        """
        logger.log_info(f"Excecuting creation of new {appointment=}")

        # TODO Έλεγχος για overlap στις ημερομηνίες. Πρέπει η καινούρια
        # ημερομηνία και η διάρκεια να μην είναι μεταξύ date, end_date

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
            self.add_to_cache(appointment_with_id)

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
        self.replace_in_cache(old_appointment, appointment.date)

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
        self.delete_from_cache(appointment_to_delete)
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
        return self.appointments

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
    ) -> Generator[Appointment]:
        """
        Συνάρτηση συνήθους περίπτωσης
        """
        index1 = self.get_index(from_date)
        index2 = self.get_index(to_date)
        for i in range(index1, index2 + 1):
            for appointment in self.appointments[i]:
                yield appointment

    def split_appointments_in_periods(self, *args, **kwargs):
        return self.appointments

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

        start_index = self.get_index(start_date)
        end_index = self.get_index(end_date)

        appointments: list[Appointment] = []
        for i in range(start_index, end_index + 1):
            appointments.extend(self.appointments[i])

        result: list[tuple[datetime, timedelta]] = []

        i = 0
        for i, appointment in enumerate(appointments):

            # Αγνοεί τα ραντεβού πριν και μετά την ημερομηνία που θέλει ο χρηστης
            if appointment.end_date < start_date:
                continue

            if appointment.date >= end_date:
                break

            # Για να μην βγεί εκτός ορίων εφόσον κοιτάμε ένα ραντεβού μπροστά
            if i == len(appointments) - 1:
                break

            previous = appointment
            next = appointments[i + 1]
            diff = previous.time_between_appointments(next)
            if diff >= minumum_free_period:
                result.append((previous.end_date, diff))

        if i == 0:
            return [(datetime.now(), timedelta(minutes=20))]

        return result

    def replace_in_cache(
        self, new_appointment: Appointment, old_date: datetime | None = None
    ) -> None:
        """
        Συνάρτηση ενημέρωσης του cache.
        """
        logger.log_info(f"Excecuting cache replacement")
        if old_date is None:
            index = self.get_index(new_appointment.date)
        else:
            index = self.get_index(old_date)

        for i in range(len(self.appointments[index])):
            if self.appointments[index][i].id == new_appointment.id:
                self.appointments[index][i] = new_appointment
                return

    def get_index(self, date: datetime):
        return (date - self.now) // PERIOD

    def add_to_cache(self, target: Appointment):
        """
        Συνάρτηση ενημέρωσης του cache
        """
        logger.log_info(f"Excecuting cache addition")

        index = self.get_index(target.date)
        self.appointments[index].append(target)
        self.appointments[index].sort(key=lambda x: x.date)

    def delete_from_cache(self, target: Appointment):
        """
        Συνάρτηση ενημέρωσης του cache
        """
        logger.log_info(f"Excecuting cache deletion")
        index = self.get_index(target.date)
        self.appointments[index].remove(target)

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

    def load_to_cache(self, date: datetime):
        if date > self.max_date:
            start = self.max_date
            end = date
            self.max_date = date
        elif date < self.min_date:
            start = date
            end = self.min_date
            self.min_date = date
        else:
            return

        appointments = (
            self.session.query(Appointment)
            .filter(Appointment.date >= start, Appointment.date < end)
            .order_by(Appointment.date)
            .all()
        )
        for appointment in appointments:
            index = self.get_index(appointment.date)
            self.appointments.setdefault(index, [])
            self.appointments[index].append(appointment)
