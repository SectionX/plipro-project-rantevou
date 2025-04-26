from datetime import datetime, timedelta
from typing import Any, Generator
from .entities import Appointment
from ..controller.logging import Logger
from ..controller import get_config

config = get_config()

__hours = config["view_settings"]["working_hours"]
__rows = config["view_settings"]["rows"]
PERIOD = timedelta(hours=int(__hours // __rows))


class AppointmentCache:

    logger = Logger("appointment-cache")

    def __init__(self, model: Any):  # Any = AppointmentModel
        self.data: dict[int, list[Appointment]] = {}
        self.id_index: dict[int, int] = {}
        self.start: int
        self.end: int
        self.now = datetime.now().replace(
            hour=9, minute=0, second=0, microsecond=0
        )  # TODO Config setting
        self.min_index: int
        self.max_index: int
        self.model = model

    def add(self, appointment: Appointment) -> bool:
        hit = True
        index = self.hash(appointment.date)
        value = self.data.get(index)
        if value is None:
            hit = False
            self.data.setdefault(index, [])
        self.data[index].append(appointment)
        self.id_index[appointment.id] = index
        return hit

    def update(self, appointment) -> bool:
        try:
            self.delete(appointment)
            self.add(appointment)
        except Exception as e:
            self.logger.log_error(str(e))
            return False
        return True

    def delete(self, appointment: Appointment) -> bool:
        date_index = self.id_index[appointment.id]
        self.id_index.pop(appointment.id)
        try:
            for i, existing in enumerate(self.data[date_index]):
                if existing.id == appointment.id:
                    del self.data[date_index][i]
                    break
            return True
        except ValueError:
            return False

    def lookup(self, date_index: int) -> list[Appointment]:
        values = self.data.get(date_index)
        if values is None:
            self.query_by_date(self.unhash(date_index), self.unhash(date_index + 1))
            return self.lookup(date_index)
        return values

    def lookup_date(self, date: datetime) -> list[Appointment]:
        return self.lookup(self.hash(date))

    def lookup_id(self, id: int) -> Appointment | None:
        appointments = self.data.get(self.id_index[id])

        if appointments is None:
            return None

        for appointment in appointments:
            if appointment.id == id:
                return appointment

        return None

    def hash(self, date: datetime) -> int:
        return (date - self.now) // PERIOD

    def unhash(self, index: int) -> datetime:
        return self.now + index * PERIOD

    def iter_date_range(
        self, start: datetime, end: datetime | None
    ) -> Generator[Appointment, None, None]:
        if end is None:
            end = start
        self.start = self.hash(start)
        self.end = self.hash(end)
        return self.__next__()

    def __iter__(self) -> Generator[Appointment, None, None]:
        raise Exception("Use Cache.iter_date_range instead")

    def __next__(self) -> Generator[Appointment, None, None]:
        for i in range(self.start, self.end + 1):
            for appointment in self.lookup(i):
                yield appointment

    def query_by_date(self, start: datetime, end: datetime):
        result = self.model.get_appointments_from_to_date(start, end)
        if len(result) == 0:
            for i in range(self.hash(start), self.hash(end) + 1):
                self.data.setdefault(self.hash(start), [])
        for appointment in result:
            self.add(appointment)

    def query_by_id(self, id: int):
        appointment = self.model.get_appointment_by_id(id)
        if appointment is None:
            return
        self.query_by_date(appointment.date, appointment.end_date)
