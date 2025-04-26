"""
Πιθανές βελτιώσεις:
1. Ασύγχρονη λειτουργία ενημέρωσης της βάσης δεδομένων
2. Ενημέρωση του cache και των συνδρομητών με πιο αποτελεσματικό τρόπο
3. Οι συναρτήσεις συνήθους περίπτωσης να δίνουν δυνατότητα αναζήτησης στο cache
   (πιθανώς με δυαδική αναζήτηση στην περίπτωση της ημερομηνίας)
"""

from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import func

from .session import session
from .entities import Appointment
from .caching import AppointmentCache
from .interfaces import Subscriber

from ..controller.logging import Logger


logger = Logger("appointment-model")
PERIOD = timedelta(hours=2)


class AppointmentModel:
    """
    Ορίζει το μοντέλο των δεδομένων και διαχειρίζεται την αναζήτηση και
    ανάκτηση πληροφορίας. Κάνει αυτόματο caching τα αποτελέσματα αναζήτησης.
    """

    _instance = None
    session = session
    # appointments: list[Appointment] = []
    subscribers: list[Subscriber] = []
    max_id = 0
    cache: AppointmentCache

    def __new__(cls, *args, **kwargs) -> AppointmentModel:
        """
        Εφαρμογή μοτίβου singleton. Αρχικοποιεί καινούριο αντικείμενο μόνο εάν
        δεν υπάρχει ήδη.
        """
        if cls._instance is None:
            cls._instance = super(AppointmentModel, cls).__new__(cls, *args, **kwargs)
            cls.max_id = session.query(func.max(Appointment.id)).scalar()
            if cls.max_id is None:
                cls.max_id = 0

            cls.cache = AppointmentCache(cls._instance)

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
        """
        Ελέγχει εάν η ημερομηνία ενός ραντεβού συμπίπτει με ήδη υπάρχοντα
        """
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
        """
        Ελέγχει εάν τα σημαντικά στοιχεία ενός ραντεβού είναι ίδια
        """
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
        self.cache.update(old_appointment)

        # Ενημέρωση των subscribers
        self.update_subscribers()
        return True

    def delete_appointment(self, appointment: Appointment) -> bool:
        """
        Διαγραφή ενός ραντεβού από την βάση δεδομένων και ενημέρωση cache.
        Ενημερώνει το τρέχων μέγιστο id για πιο γρήγορη προσθήκη νέων ραντεβού.
        Επιβάλλει στο ραντεβού προς διαγραφή να έχει id.
        """
        logger.log_info(f"Excecuting deletion of {appointment=}")

        # Έλεγχος αν το ραντεβού έχει id
        if appointment.id is None:
            logger.log_error("Appointment for deletion must have an id")
            return False

        # Εύρεση του ραντεβού στην βάση δεδομένων για επιβεβαίωση του id και
        # σύνδεση με την sqlalchemy
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
        Επιστρέφει όλα τα ραντεβού που έχουν αποθηκευτεί στο cache κατα
        την αρχικοποίηση και αργότερα με τις ενέργειες του χρήστη.
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
        """
        Συνάρτηση συνήθους περίπτωσης
        """
        result = (
            self.session.query(Appointment)
            .filter(Appointment.date >= from_date, Appointment.date < to_date)
            .all()
        )

        return result

    def get_appointments_by_period(self, date: datetime):
        """
        Ειδικευμένη συνάρτηση που επιστρέφει όλα τα ραντεβού εντός
        της περιόδου που ανήκει η ημερομηνία date
        """
        return [*self.cache.iter_date_range(date, date)]

    def get_time_between_appointments(
        self,
        start_date: datetime = datetime.now(),
        end_date: datetime = datetime.now() + timedelta(days=1),
        minumum_free_period: timedelta = PERIOD,
    ) -> list[tuple[datetime, timedelta]]:
        """
        Συνάρτηση αναζήτησης κενού χρόνου μεταξύ των ραντεβού.
        """
        logger.log_debug(f"Excecuting calculation of time between appointments")

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
