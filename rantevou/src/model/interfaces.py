from typing import Protocol, runtime_checkable
from datetime import datetime

from .entities import Appointment


@runtime_checkable
class Subscriber(Protocol):
    """
    Interface για όλα τα στοιχεία που κάνουν subscribe για να
    ενημερώνονται όταν γίνονται σημαντικές αλλαγές στην  βάση
    δεδομένων
    """

    def subscriber_update(self): ...


class AppointmentModel(Protocol):
    """
    Interface με το μοντέλο ραντεβού
    """

    def get_appointment_by_id(self, appointment_id: int) -> Appointment | None: ...
    def get_appointment_by_date(self, date: datetime) -> Appointment | None: ...
    def get_appointments_from_to_date(
        self, from_date: datetime, to_date: datetime
    ) -> list[Appointment]: ...
