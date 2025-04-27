from __future__ import annotations

from datetime import datetime, timedelta
from typing import NamedTuple

from . import get_config
from .logging import Logger
from ..model.entities import Appointment, Customer
from ..model.appointment import AppointmentModel
from .customers_controller import CustomerControl

# TODO: Ιδανικά για κάθε συνάρτηση θέλουμε και διαγνωστικά logs
# TODO: Πρέπει να ελεγχθούν όλοι οι είσοδοι ότι έχουν ορθά στοιχεία και να
# επιστραφεί το κατάλληλο μύνημα

# Ουσιαστικά οι περισσότερες συναρτήσεις απλά καλούν το αποτέλεσμα από το model.
# Το όλο θέμα είναι να μπουν logs και error checking σε κάθε συνάρτηση

cfg = get_config()["view_settings"]
PERIOD = timedelta(hours=cfg["working_hours"] // cfg["rows"])

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
    mode: AppointmentModel

    def __new__(cls, *args, **kwargs) -> AppointmentControl:
        if cls._instance:
            return cls._instance

        cls._instance = super(AppointmentControl, cls).__new__(cls, *args, **kwargs)
        cls.model = AppointmentModel()
        return cls._instance

    def get_appointments(self) -> dict[int, list[Appointment]]:
        """
        Επιστρέφει όλες τις εγγραφές από το table Appointments
        """
        logger.log_info("Requesting list of appointments")
        return self.model.get_appointments()

    def create_appointment(
        self, appointment: Appointment, customer: Customer | None = None
    ) -> int | None:
        """
        Προσθέτει καινούρια εγγραφή στο table Appointments
        """
        logger.log_info(f"Requesting creation of {appointment} for {customer}")

        if customer is None:
            logger.log_debug("Creating appointment without customer")
            appointment.customer_id = None
            return self.model.add_appointment(appointment)

        cc = CustomerControl()
        if customer.id is None:
            logger.log_debug("Creating appointment and adding customer")
            customer_id, _ = cc.create_customer(customer)
            appointment.customer_id = customer_id  # type: ignore
            return self.model.add_appointment(appointment)

        if customer.id is not None:
            logger.log_debug("Creating appointment and updating customer")
            cc.update_customer(customer)
            appointment.customer_id = customer.id
            return self.model.add_appointment(appointment)

        logger.log_warn("Request Failure")
        return None

    def delete_appointment(self, appointment: Appointment) -> bool:
        """
        Σβήνει μια εγγραφή από το table Appointments
        """
        logger.log_info(f"Requesting deletion for {appointment}")
        return self.model.delete_appointment(appointment)

    def update_appointment(
        self,
        appointment: Appointment,
        customer: Customer | None = None,
    ) -> bool:
        """
        Μεταβάλλει τα στοιχεία μιας εγγραφής στο table Appointments
        """
        logger.log_info(f"Requesting update for {appointment} for {customer}")

        if customer is None:
            logger.log_debug("Updating appointment without customer")
            return self.model.update_appointment(appointment)

        cc = CustomerControl()
        if customer.id is None:
            logger.log_debug("Updating appointment and adding customer")
            customer_id, _ = cc.create_customer(customer)
            return self.model.update_appointment(appointment, customer_id)

        if customer.id is not None:
            logger.log_debug("Updating appointment and customer")
            cc.update_customer(customer)
            return self.model.update_appointment(appointment, customer.id)

        logger.log_warn("Request Failure")
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

    # def get_appointments_grouped_in_periods(
    #     self,
    #     start: datetime,
    #     period: timedelta,
    # ):
    #     logger.log_debug(
    #         f"Requesting model to split appointments in groups for {start=}, {period=}"
    #     )
    #     return self.model.split_appointments_in_periods(period, start)

    def add_subscription(self, subscriber):
        logger.log_info(f"Requesting subscription for {subscriber}")
        self.model.add_subscriber(subscriber)

    def get_time_between_appointments(
        self,
        start_date: datetime = datetime.now(),
        end_date: datetime = datetime.now() + timedelta(days=1),
        minumum_free_period: timedelta = timedelta(minutes=120),  # TODO import settings
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

    def get_appointments_by_period(self, date: datetime) -> list[Appointment]:
        return self.model.get_appointments_from_to_date(date, date + PERIOD)
