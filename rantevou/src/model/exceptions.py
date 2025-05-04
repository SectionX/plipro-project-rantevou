from rantevou.src.controller.logging import Logger


appointment_logger = Logger("Appointment-Model")
customer_logger = Logger("Customer-Model")


class ModelException(Exception):
    """Base exception for model errors"""

    logger = Logger("Model")

    def __init__(self):
        if self.__doc__ is None:
            self.__doc__ = ""
        self.logger.log_error(self.__doc__)

    def __str__(self):
        if self.__doc__ is None:
            return ""
        return self.__doc__


class AppointmentModelException(ModelException):
    """Base exception for appointment model errors"""

    logger = appointment_logger


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


class DateMissing(AppointmentModelException):
    """Date field is required"""


class DurationMissing(AppointmentModelException):
    """Duration field is required"""


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
