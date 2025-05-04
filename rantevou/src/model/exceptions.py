from typing import Literal
from rantevou.src.controller.logging import Logger

appointment_logger = Logger("Appointment-Model")
customer_logger = Logger("Customer-Model")


class ModelException(Exception):
    """Base exception for model errors"""

    logger = Logger("Model")
    level: Literal["DEBUG", "INFO", "WARN", "ERROR"] = "WARN"

    def __init__(self):
        if self.__doc__ is None:
            self.__doc__ = ""
        self.logger.log(self.__doc__, self.level)

    def __str__(self):
        if self.__doc__ is None:
            return ""
        return self.__doc__


class AppointmentModelException(ModelException):
    """Base exception for appointment model errors"""

    logger = appointment_logger

    def __init__(self, appointment=None, db_exception=None):
        if db_exception is not None:
            self.level = "ERROR"
        super().__init__()
        self.appointment = appointment
        self.db_exception = db_exception

    def __str__(self) -> str:
        buffer = []
        if self.db_exception is not None:
            buffer.append(str(self.db_exception))
        if self.__doc__ is not None:
            buffer.append(self.__doc__)
        if self.appointment is not None:
            buffer.append(str(self.appointment))

        if self.__doc__ is None:
            return ""
        self.__doc__ = "\n".join(buffer)
        return self.__doc__


class CustomerModelException(ModelException):
    """Base exception for customer model errors"""

    logger = customer_logger


### Appointment Exceptions


class DateOverlap(AppointmentModelException):
    """Cannot add new appointment in this time slot"""


class AppointmentIdAlreadyExists(AppointmentModelException):
    """Manual id assignment is discouraged"""


class AppointmentIdNotFound(AppointmentModelException):
    """Id not found"""


class AppointmentDateNotFound(AppointmentModelException):
    """Date not found"""


class IdMissing(AppointmentModelException):
    """This operation requires the caller to provide the id"""


class IdNotFoundInDB(AppointmentModelException):
    """This id does not exist in DB"""


class DateMissing(AppointmentModelException):
    """Date field is required"""


class DurationMissing(AppointmentModelException):
    """Duration field is required"""


class AppointmentDBError(AppointmentModelException):
    """Database Error"""


class SynchronizationDBError(AppointmentModelException):
    """DB and Cache are out of sync, restart the application"""


### Customer Exceptions


class NameMissing(CustomerModelException):
    """Name field is required"""


class CustomerIdAlreadyExists(CustomerModelException):
    """Manual id assignment is discouraged"""


class PhoneAlreadyExists(CustomerModelException):
    """Phone field must be unique"""


class EmailAlreadyExists(CustomerModelException):
    """Email field must be unique"""


class InvalidEmail(CustomerModelException):
    """Email entry cannot be validated"""


class InvalidPhone(CustomerModelException):
    """Phone entry cannot be validated"""
