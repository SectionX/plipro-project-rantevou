"""
Ορισμός του μοντέλου δεδομένων των ραντεβού
"""

from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import func
from sqlalchemy.exc import DatabaseError

from .session import session
from .entities import Appointment
from .caching import AppointmentCache

from .interfaces import SubscriberInterface
from ..controller.logging import Logger
from ..controller import get_config

from .exceptions import (
    DateOverlap,
    WrongAppointment,
    AppointmentDBError,
    SynchronizationDBError,
    IdMissing,
    IdNotFoundInDB,
    NoSubscriberInterface,
)

cfg = get_config()
_working_hours = int(cfg["view_settings"]["working_hours"])
_rows = int(cfg["view_settings"]["rows"])
PERIOD = timedelta(minutes=_working_hours // _rows)

logger = Logger("Appointment-Model")


class AppointmentModel:
    """
    Ορισμός του μοντέλου δεδομένων για τα ραντεβού.

    Εφαρμόζει singleton pattern ώστε να υπάρχει μόνο ένα instance
    ενεργό σε όλη στην εφαρμογή. Έχει αυτόματη λειτουργία caching.

    >>> from rantevou.src.model.appointment import AppointmentModel
    >>> a = AppointmentModel()
    >>> b = AppointmentModel()
    >>> a is b
    True
    """

    _instance = None
    session = session
    subscribers: list[SubscriberInterface] = []
    max_id = 0
    cache: AppointmentCache

    def __new__(cls, *args, **kwargs) -> AppointmentModel:
        """
        Constructor, εφαρμογή του Singleton Pattern

        Αρχικοποιεί ραντεβού για 10 μέρες πριν και μετά την αρχή της σημερινής εργάσιμης μέρας
        """
        if cls._instance is None:
            logger.log_info("Initializing Appointment Model")

            cls._instance = super(AppointmentModel, cls).__new__(cls, *args, **kwargs)
            cls.max_id = session.query(func.max(Appointment.id)).scalar()
            if cls.max_id is None:
                cls.max_id = 0

            cls.cache = AppointmentCache(cls._instance)

            cls.now = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
            cls.min_date = cls.now - timedelta(days=9, hours=23)
            cls.max_date = cls.now + timedelta(days=9, hours=23)

            appointments = (
                session.query(Appointment)
                .filter(Appointment.date >= cls.min_date, Appointment.date <= cls.max_date)
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

        Returns:
            bool: True εάν υπάρχει overlap, αλλιώς False
        """
        for existing_appointment in self.cache.iter_date_range(appointment.date, appointment.end_date):
            if existing_appointment.overlap(appointment):
                return True
        return False

    def add_appointment(self, appointment: Appointment) -> int:
        """
        Προσθήκη νέου ραντεβού στην βάση δεδομένων και ενημέρωση του cache

        Args:
            appointment (Appointment): Αναπαράσταση του καινούριου ραντεβού. Δεν πρέπει να έχει id

        Raises:
            DateOverlap: Εάν η ημερομηνία συμπίπτει με άλλη
            AppointmentDBError: Εάν κάτι πάει λάθος κατα την είσοδο στην βάση δεδομένων
            SynchronizationDBError: Εάν ο μετρητής max_id δεν συμπίπτει με το max id στην βάση δεδομένων

        Returns:
            int: Το id του καινούριου ραντεβού
        """

        logger.log_info(f"Excecuting creation of {appointment}")

        if self.has_overlap(appointment):
            raise DateOverlap(appointment)

        # Προσθήκη στην βάση δεδομένων
        try:
            self.session.add(appointment)
            self.session.commit()
            self.max_id += 1
            logger.log_debug(f"Assigned id={self.max_id}")
        except DatabaseError as e:
            self.session.rollback()
            raise AppointmentDBError(appointment, e) from e

        # Έλεγχος ορθής λειτουργίας
        appointment_with_id = self.session.query(Appointment).filter(Appointment.id == self.max_id).first()
        if appointment_with_id is None:
            raise SynchronizationDBError(appointment)

        # Ενημέρωση του cache
        if appointment_with_id:
            self.cache.add(appointment_with_id)

        # Ενημέρωση των subscribers
        self.update_subscribers()

        # Επιστροφή του μοναδικού id
        return appointment_with_id.id

    def is_similar(self, appointment1: Appointment, appointment2: Appointment):
        """
        Ελέγχει εάν τα σημαντικά στοιχεία ενός ραντεβού (εκτός του id) είναι ίδια

        Args:
            appointment1 (Appointment): Ραντεβού για σύγκριση
            appointment2 (Appointment): Ραντεβού για σύγκριση

        Returns:
            bool: True εαν είναι παρόμοια, αλλιώς False
        """
        return all(
            (
                appointment1.id == appointment2.id,
                appointment1.date == appointment2.date,
                appointment1.is_alerted == appointment2.is_alerted,
                appointment1.duration == appointment2.duration,
            )
        )

    def update_appointment(self, appointment: Appointment, customer_id: int | None = None) -> bool:
        """
        Ενημέρωση στοιχείων ραντεβού στην βάση δεδομένων και ενημέρωση cache

        Επιβάλλει να υπάρχει id στο ραντεβού προς ενημέρωση. Επιστρέφει μόνο True εάν όλα πάνε καλά

        Args:
            appointment (Appointment): Ραντεβού προς αλλαγή
            customer_id (int | None, optional): Id του πελάτη θα σχετιστεί με το ραντεβού. Defaults to None.

        Raises:
            DateOverlap: Εάν η ημερομηνία συμπίπτει με άλλη
            IdMissing: Εάν το ραντεβού προς αλλαγή δεν έχει id
            IdNotFoundInDB: Εάν το id του ραντεβού προς αλλαγή δεν υπάρχει στην βάση δεδομένων
            AppointmentDBError: Εάν υπάρξει κάποιο σφάλμα κατα την επεξεργασία στην βάση δεδομένων

        Returns:
            bool: True εάν η διαδικασία ολοκληρωθεί επιτυχώς.
        """
        logger.log_info(f"Excecuting update of {appointment}")

        # Έλεγχος περιπτώσεων σφάλματος
        if self.has_overlap(appointment):
            raise DateOverlap(appointment)

        if appointment.id is None:
            raise IdMissing(appointment)

        old_appointment = session.query(Appointment).filter_by(id=appointment.id).first()

        if old_appointment is None:
            raise IdNotFoundInDB(appointment)

        # Ενημέρωση του ραντεβού
        if customer_id is not None:
            logger.log_debug(f"Adding {customer_id=} to {appointment.id=}")
            old_appointment.customer_id = customer_id

        old_appointment.date = appointment.date
        old_appointment.duration = appointment.duration
        old_appointment.is_alerted = appointment.is_alerted

        # Εγγραφή στην βάση δεδομένων
        try:
            self.session.commit()
        except DatabaseError as e:
            self.session.rollback()
            raise AppointmentDBError(appointment, e) from e

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

        Args:
            appointment (Appointment): Το ραντεβού προς διαγραφή

        Raises:
            IdMissing: Εάν το ραντεβού δεν έχει id
            WrongAppointment: Εάν τα στοιχεία του ραντεβού στην βάση δεδομένων είναι διαφορετικά
            IdNotFoundInDB: Εάν το το id του ραντεβού δεν υπάρχει στην βάση δεδομένων
            AppointmentDBError: Εάν κάτι πήγε λάθος κατα την διαγραφή από την βάση δεδομένων

        Returns:
            bool: True εαν η διαγραφή είναι επιτυχής, αλλιώς exception
        """

        logger.log_info(f"Excecuting deletion of {appointment}")

        # Έλεγχος αν το ραντεβού έχει id
        if appointment.id is None:
            raise IdMissing(appointment)

        # Εύρεση του ραντεβού στην βάση δεδομένων για επιβεβαίωση του id και
        # σύνδεση με την sqlalchemy
        appointment_to_delete = self.get_appointment_by_id(appointment.id)
        if appointment_to_delete is None:
            raise IdNotFoundInDB(appointment)

        if not self.is_similar(appointment, appointment_to_delete):
            raise WrongAppointment(appointment)

        # Διαγραφή του στοιχείου από την βάση δεδομένων
        try:
            self.session.delete(appointment_to_delete)
            self.session.commit()
        except DatabaseError as e:
            self.session.rollback()
            raise AppointmentDBError(appointment, e) from e

        # Ενημέρωση του cache
        self.cache.delete(appointment_to_delete)
        self.max_id = self._find_max_id()

        # Ενημέρωση των subscribers
        self.update_subscribers()
        return True

    def get_appointments(self) -> dict[int, list[Appointment]]:
        """
        Επιστρέφει όλα τα ραντεβού που είναι αποθηκευμένα στο cache

        Σημαντικό, η συνάρτηση δεν κάνει αναζήτηση στην βάση δεδομένων. Για γενικές αναζητήσεις
        χρησιμοποίησε μια από τις άλλες get συναρτήσεις.

        Returns:
            dict[int, list[Appointment]]: Dictionary με τα ραντεβού χωρισμένα ανα περίοδο, με 0
            την αρχή της σημερινής μέρας. Η περίοδος ορίζεται στο settings.json και είναι το αποτέλεσμα
            της πράξης working_hours / rows
        """
        logger.log_debug("Excecuting query of cached appointments")
        return self.cache.data

    def get_appointment_by_id(self, appointment_id: int) -> Appointment | None:
        """
        Εύρεση ραντεβού με βάση το id

        Args:
            appointment_id (int): Id προς αναζήτηση

        Returns:
            Appointment | None: Το ραντεβού ή None αν δεν υπάρχει
        """
        logger.log_debug(f"Excecuting query of appointment by id={appointment_id}")
        return self.session.query(Appointment).filter_by(id=appointment_id).first()

    def get_appointment_by_date(self, date: datetime) -> Appointment | None:
        """
        Εύρεση ραντεβού με βάση την ημερομηνία

        Args:
            date (datetime): Ημερομηνία προς αναζήτηση

        Returns:
            Appointment | None: Το ραντεβού ή None αν δεν υπάρχει
        """
        logger.log_debug(f"Excecuting query of appointment by {date=}")
        return self.session.query(Appointment).filter_by(date=date).first()

    def get_appointments_from_to_date(self, from_date: datetime, to_date: datetime) -> list[Appointment]:
        """
        Εύρεση ραντεβού μεταξύ ημερομηνιών.

        Args:
            from_date (datetime): Αρχή της περιόδου
            to_date (datetime): Τέλος της περιόδου

        Returns:
            list[Appointment]: Λίστα με τα ραντεβού. Επιστρέφει άδεια λίστα εαν δεν υπάρχουν αποτελέσματα
        """
        logger.log_debug(f"Excecuting query of appointment from {str(from_date)} to {str(to_date)}")
        result = self.session.query(Appointment).filter(Appointment.date >= from_date, Appointment.date < to_date).all()

        return result

    def get_time_between_appointments(
        self,
        start_date: datetime = datetime.now(),
        end_date: datetime = datetime.now() + timedelta(days=1),
        minumum_free_period: timedelta = PERIOD,
    ) -> list[tuple[datetime, timedelta]]:
        """
        Συνάρτηση αναζήτησης κενού χρόνου μεταξύ των ραντεβού.
        """
        logger.log_debug("Excecuting calculation of time between appointments")

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

    def add_subscriber(self, subscriber: SubscriberInterface):
        """
        Δήλωση των subscribers στην λίστα προς ενημέρωση

        Args:
            subscriber (SubscriberInterface): Το αντικείμενο που θέλει να παίρνει ενημερώσεις απο
            το μοντέλο. Συνήθως τα στοιχεία GUI. Πρέπει να υλοποιεί την διεπαφή SubscriberInterface,
            δηλαδή να έχει μέθοδο .subscriber_update.

        Raises:
            NoSubscriberInterface: Εάν το αντικείμενο δεν εφαρμόζει την διεπαφή SubscriberInterface
        """
        # Έλεγχος εάν το αντικείμενο υλοποιεί την κατάλληλη διεπαφή
        if not hasattr(subscriber, "subscriber_update"):
            logger.log_error("Object is not a subscriber")
            raise NoSubscriberInterface(subscriber)

        logger.log_debug(f"Adding {subscriber=}")
        self.subscribers.append(subscriber)

    def update_subscribers(self):
        """
        Ενημέρωση των δηλωμένων subscriber.

        Να καλείται όταν γίνεται κάποια μετατροπή στην βάση δεδομένων.
        """
        logger.log_info(f"Excecuting notification of {len(self.subscribers)} subscribers")
        for subscriber in self.subscribers:
            logger.log_debug(str(subscriber))
            subscriber.subscriber_update()

    def _find_max_id(self) -> int:
        """
        Ψάχνει το μέγιστο id στο Appointment table για λόγους συγχρονισμού με το cache
        """
        logger.log_debug("Executing recalculation of maximum id")
        result = self.session.query(func.max(Appointment.id)).scalar()
        if result is None:
            return 0
        return result
