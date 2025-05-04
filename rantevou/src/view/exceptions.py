from typing import Literal
from rantevou.src.controller.logging import Logger

search_logger = Logger("Search-View")
alert_logger = Logger("Alert-View")


class ViewException(Exception):
    """Base exception for view errors"""

    logger = Logger("View")
    level: Literal["DEBUG", "INFO", "WARN", "ERROR"] = "WARN"

    def __init__(self):
        if self.__doc__ is None:
            self.__doc__ = ""
        self.logger.log(self.__doc__, self.level)

    def __str__(self):
        if self.__doc__ is None:
            return ""
        return self.__doc__


class ViewWrongDataError(ViewException):
    """View cannot process this type"""

    def __init__(self, view, caller, data):
        buffer = f"View: {str(view)}, Caller:{str(caller)}, Type:{type(data)}"
        if self.__doc__ is None:
            self.__doc__ = buffer
        else:
            self.__doc__ += ": " + buffer
        super().__init__()


class ViewCommunicationError(ViewException):
    """Για όταν κάποιο view component δεν μπορεί να καλέσει κάποιο άλλο"""


class ViewInternalError(ViewException):
    """Internal logic error"""

    def __init__(self, message):
        if self.__doc__ is None:
            self.__doc__ = message
        else:
            self.__doc__ += ": " + message
        super().__init__()


class ViewInputError(ViewException):
    """User Generated Error"""

    def __init__(self, message):
        if self.__doc__ is None:
            self.__doc__ = message
        else:
            self.__doc__ += ": " + message
        super().__init__()
