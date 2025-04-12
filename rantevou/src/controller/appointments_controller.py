from datetime import datetime, timedelta
from typing import NamedTuple
from .logging import Logger
from ..model.session import SessionLocal
from ..model.types import Appointment, AppointmentModel

# TODO: Ιδανικά για κάθε συνάρτηση θέλουμε και διαγνωστικά logs
# TODO: Πρέπει να ελεγχθούν όλοι οι είσοδοι ότι έχουν ορθά στοιχεία και να
# επιστραφεί το κατάλληλο μύνημα

# Ουσιαστικά οι περισσότερες συναρτήσεις απλά καλούν το αποτέλεσμα από το model.
# Το όλο θέμα είναι να μπουν logs και error checking σε κάθε συνάρτηση

logger = Logger("appointments_controller")


class AppointmentGroup(NamedTuple):
    order: int
    start_date: datetime
    end_date: datetime
    length: int
    appointments: tuple[Appointment, ...]


class AppointmentControl:
    """
    Διαχειρίζεται όλες τις ενέργειες που απαιτούν στοιχεία από
    το table Appointments
    """

    def __init__(self):
        self.model = AppointmentModel()

    def get_appointments(self) -> list[Appointment]:
        """
        Επιστρέφει όλες τις εγγραφές από το table Appointments
        """
        return self.model.get_appointments()

    def create_appointment(self, appointment: Appointment | dict) -> None:
        """
        Προσθέτει καινούρια εγγραφή στο table Appointments
        """
        # TODO Η υλοποίηση είναι ενδεικτική. Θέλουμε να υποστηρίζει
        # και Appointment Class και dictionary ως παράμετρο

        if not self.validate_appointment(appointment):
            raise ValueError

        if isinstance(appointment, Appointment):
            self.model.add_appointment(appointment)
        else:
            raise NotImplementedError

    def delete_appointment(self, appointment: Appointment | dict | int) -> bool:
        """
        Σβήνει μια εγγραφή από το table Appointments
        """
        if isinstance(appointment, int):
            full_appointment = self.model.get_appointment_by_id(appointment)
            if full_appointment:
                appointment = full_appointment
            else:
                return False

        if isinstance(appointment, dict):
            try:
                appointment = Appointment(**appointment)
            except Exception as e:
                logger.log_warn(str(e))
                return False

        self.model.delete_appointment(appointment)

        return True

    def update_appointment(self, appointment: Appointment | dict) -> bool:
        """
        Μεταβάλλει τα στοιχεία μιας εγγραφής στο table Appointments
        """
        if isinstance(appointment, dict):
            try:
                appointment = Appointment(**appointment)
            except Exception as e:
                logger.log_warn(str(e))
                return False

        self.model.update_appointment(appointment)
        return True

    def get_appointment_by_id(self, id: int) -> Appointment | None:
        """
        Επιστρέφει μια εγγραφή με βάση το id από το table Appointments
        """
        return self.model.get_appointment_by_id(id)

    def get_appointment_by_date(self, date: datetime) -> Appointment | None:
        """
        Επιστρέφει μια εγγραφή με βάση το id από το table Appointments
        """
        return self.model.get_appointment_by_date(date)

    def validate_appointment(self, appointment: Appointment | dict) -> bool:
        """
        Ελέγχει ότι τα στοιχεία της εγγραφής ειναι σωστά και ότι
        δεν μπαίνει καινούριο ραντεβού σε περιόδο που είναι ήδη
        γεμάτη.
        """
        # TODO λείπει όλη η υλοποίηση
        return True

    def get_appointments_grouped_in_periods(
        self,
        start: datetime,
        period: timedelta,
    ):
        return self.model.split_appointments_in_periods(period, start)

    def add_subscription(self, subscriber):
        self.model.add_subscriber(subscriber)

    def get_time_between_appointments(
        self,
        start_date: datetime | None = None,
        minumum_free_period: timedelta | None = None,
    ) -> list[tuple[datetime, timedelta]]:

        return self.model.get_time_between_appointments(start_date, minumum_free_period)

    def get_index_from_date(
        self, date: datetime, start_date: datetime, period_duration: timedelta
    ) -> int:
        return (date - start_date) // period_duration

    def get_appointments_from_to_date(self, start: datetime, end: datetime):
        return self.model.get_appointments_from_to_date(start, end)
