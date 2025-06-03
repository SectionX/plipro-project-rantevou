from __future__ import annotations

from datetime import datetime, timedelta
from enum import Enum

from . import get_config
from .logging import Logger
from .customers_controller import CustomerControl
from ..model.entities import Appointment, Customer
from ..model.appointment import AppointmentModel
from ..model.exceptions import *

cfg = get_config()["view_settings"]
PERIOD = timedelta(hours=cfg["working_hours"] // cfg["rows"])

logger = Logger("appointments_controller")


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
        Επιστρέφει όλες τις εγγραφές από το table Appointments που υπάρχουν στο cache.

        Προσοχή!
        Αυτή η συνάρτηση προορίζεται για παραγωγή διαγνωστικών και στατιστικών στοιχείων
        που αφορούν περισσότερο τις εσωτερικές λειτουργίες του προγράμματος. Για γενική
        χρήση προτίνεται η ".get_appointments_from_to_date"

        Returns:
            dict[int, list[Appointment]]
        """
        logger.log_info("Requesting list of appointments")
        return self.model.get_appointments()

    def create_appointment(self, appointment: Appointment, customer: Customer | None = None) -> int | None:
        """
        Προσθέτει καινούρια εγγραφή στο table Appointments
        """
        logger.log_info(f"Requesting creation of {appointment}")

        if customer is None:
            logger.log_debug("Creating appointment without customer")
            appointment.customer_id = None
            return self.model.add_appointment(appointment)

        if not any(customer.values):
            logger.log_debug("Creating appointment without customer")
            appointment.customer_id = None
            return self.model.add_appointment(appointment)

        cc = CustomerControl()
        if customer.id is None:
            logger.log_debug("Creating appointment and adding customer")
            customer = cc.create_customer(customer)
            appointment.customer_id = customer.id  # type: ignore
            return self.model.add_appointment(appointment)

        if customer.id is not None:
            logger.log_debug("Creating appointment and updating customer")
            cc.update_customer(customer)
            appointment.customer_id = customer.id
            return self.model.add_appointment(appointment)

        logger.log_warn("Request Failure")
        return None

    def delete_appointment(self, appointment: Appointment) -> tuple[bool, str]:
        """
        Σβήνει ένα ραντεβού από την βάση δεδομένων. Το ραντεβού πρέπει να έχει id,
        να υπάρχει στην βάση δεδομένων και τα στοιχεία του να είναι ίδια με της
        βάσης δεδομένων.

        Args:
            appointment (Appointment): Ραντεβού προς διαγραφή

        Returns:
            tuple[bool, str]: Boolean ορθής ολοκλήρωσης και λόγος αποτυχίας
        """
        logger.log_info(f"Requesting deletion for {appointment}")
        try:
            return self.model.delete_appointment(appointment), "ok"
        except IdMissing:
            return False, "Το ραντεβού δεν έχει id"
        except WrongAppointment:
            return False, f"Τα στοιχεία του ραντεβού με id {appointment.id} δεν είναι σωστά"
        except IdNotFoundInDB:
            return False, f"Το ραντεβού με id {appointment.id} δεν υπάρχει"
        except AppointmentDBError as e:
            return False, str(e.__doc__)

    def update_appointment(
        self,
        appointment: Appointment,
        customer: Customer | None = None,
    ) -> tuple[bool, str]:
        """
        Μεταβάλλει τα στοιχεία μιας εγγραφής στο table Appointments. Επίσης
        ανανεώνει τα στοιχεία των αντικειμένων που δώθηκαν ως παράμετροι

        Args:
            appointment (Appointment): _description_
            customer (Customer | None, optional): _description_. Defaults to None.

        Returns:
            tuple[bool, str]: κωδικός επιτυχίας και λόγος αποτυχίας
        """
        logger.log_info(f"Requesting update for {appointment} for {customer}")

        if customer is None:
            logger.log_debug("Updating appointment without customer")
            return self.model.update_appointment(appointment), ""

        cc = CustomerControl()
        if customer.id is None:
            logger.log_debug("Updating appointment and adding customer")
            customer = cc.create_customer(customer)
            return self.model.update_appointment(appointment, customer.id), ""

        if customer.id is not None:
            logger.log_debug("Updating appointment and customer")
            cc.update_customer(customer)
            return self.model.update_appointment(appointment, customer.id), ""

        logger.log_warn("Request Failure")
        return False, "Αποτυχία ενημέρωσης ραντεβού"

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

    def add_subscription(self, subscriber):
        logger.log_info(f"Requesting subscription for {subscriber}")
        self.model.add_subscriber(subscriber)

    def get_time_between_appointments(
        self,
        start_date: datetime = datetime.now(),
        end_date: datetime = datetime.now() + timedelta(days=1),
        minumum_free_period: timedelta = timedelta(minutes=20),  # TODO import settings
    ) -> list[tuple[datetime, timedelta]]:
        logger.log_debug(f"Requesting list of time between appointments for {start_date=}, {minumum_free_period=}")
        return self.model.get_time_between_appointments(start_date, end_date, minumum_free_period)

    def get_index_from_date(self, date: datetime, start_date: datetime, period_duration: timedelta) -> int:
        logger.log_debug(f"Requesting calculation of group index for {date=}, {start_date=}, {period_duration=}")
        return (date - start_date) // period_duration

    def get_appointments_from_to_date(self, start: datetime, end: datetime):
        logger.log_debug(f"Requesting query of appointments from {start} to {end}")
        return self.model.get_appointments_from_to_date(start, end)
