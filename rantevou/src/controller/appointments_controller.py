from datetime import datetime, timedelta
from typing import NamedTuple
from .logging import Logger
from tkinter import ttk
from ..model.types import Appointment, AppointmentModel, Customer, CustomerModel

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

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance:
            return cls._instance

        cls._instance = super(AppointmentControl, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.model = AppointmentModel()

    def get_appointments(self) -> list[Appointment]:
        """
        Επιστρέφει όλες τις εγγραφές από το table Appointments
        """
        logger.log_info("Requesting list of appointments")
        return self.model.get_appointments()

    def create_appointment(
        self, appointment: Appointment, customer: Customer | None = None
    ) -> None:
        """
        Προσθέτει καινούρια εγγραφή στο table Appointments
        """
        logger.log_info(
            f"Requesting new appointment creation {appointment=}, {customer=}"
        )
        # TODO Η υλοποίηση είναι ενδεικτική. Ότι έχει να κάνει με πελάτες
        # πρέπει να εκτελεστεί από το customer control

        if customer is None:
            appointment.customer_id = None
            self.model.add_appointment(appointment)
            return

        cmodel = CustomerModel()
        existing_customer = (
            cmodel.session.query(Customer)
            .filter(
                Customer.name == customer.name,
                Customer.surname == customer.surname,
                Customer.phone == customer.phone,
                Customer.email == customer.email,
            )
            .first()
        )

        if existing_customer is None:
            id = cmodel.add_customer(customer)
            appointment.customer_id = id
        else:
            appointment.customer_id = existing_customer.id

        self.model.add_appointment(appointment)

    def delete_appointment(self, appointment: Appointment | dict | int) -> bool:
        """
        Σβήνει μια εγγραφή από το table Appointments
        """
        logger.log_info(f"Requesting appointment deletion for {appointment=}")
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

    def update_appointment(
        self,
        old_appointment: Appointment,
        appointment: Appointment,
        customer: Customer | None = None,
    ) -> bool:
        """
        Μεταβάλλει τα στοιχεία μιας εγγραφής στο table Appointments
        """
        logger.log_info(
            f"Requesting appointment update for {appointment=}, {customer=}"
        )

        check = self.model.get_appointment_by_id(old_appointment.id)
        if check is None:
            logger.log_error("Cannot update non existing appointment")
            return False

        cmodel = CustomerModel()
        try:
            if customer:
                old_customer = cmodel.get_customer_by_email(customer.email)
                if old_customer is None:
                    id = cmodel.add_customer(customer)
                    appointment.customer_id = id
                    self.model.update_appointment(old_appointment, appointment)
                    return True

                if old_customer != customer:
                    cmodel.update_customer(customer)

            self.model.update_appointment(old_appointment, appointment)
            return True
        except Exception as e:
            logger.log_error(f"Failer to update appointment with error {str(e)}")
            return False

    def get_appointment_by_id(self, id: int) -> Appointment | None:
        """
        Επιστρέφει μια εγγραφή με βάση το id από το table Appointments
        """
        logger.log_info(f"Requesting appointment by {id=}")
        return self.model.get_appointment_by_id(id)

    def get_appointment_by_date(self, date: datetime) -> Appointment | None:
        """
        Επιστρέφει μια εγγραφή με βάση το id από το table Appointments
        """
        logger.log_info(f"Requesting appointment by {date=}")
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
        logger.log_debug(
            f"Requesting model to split appointments in groups for {start=}, {period=}"
        )
        return self.model.split_appointments_in_periods(period, start)

    def add_subscription(self, subscriber):
        logger.log_info(f"Requesting subscription for {subscriber}")
        self.model.add_subscriber(subscriber)

    def get_time_between_appointments(
        self,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        minumum_free_period: timedelta | None = None,
    ) -> list[tuple[datetime, timedelta]]:
        logger.log_debug(
            f"Requesting list of time between appointments for {start_date=}, {minumum_free_period=}"
        )
        return self.model.get_time_between_appointments(
            start_date, end_date, minumum_free_period
        )

    def get_index_from_date(
        self, date: datetime, start_date: datetime, period_duration: timedelta
    ) -> int:
        logger.log_debug(
            f"Requesting calculation of group index for {date=}, {start_date=}, {period_duration=}"
        )
        return (date - start_date) // period_duration

    def get_appointments_from_to_date(self, start: datetime, end: datetime):
        logger.log_debug(f"Requesting query of appointments from {start} to {end}")
        return self.model.get_appointments_from_to_date(start, end)
