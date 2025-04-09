from __future__ import annotations
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from .session import Base
from . import customer


class Appointment(Base):
    __tablename__ = "appointment"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime] = mapped_column(nullable=False, unique=True)
    is_alerted: Mapped[bool] = mapped_column(default=False)
    duration: Mapped[int] = mapped_column(default=20)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customer.id"), nullable=True)

    customer = relationship(
        "Customer",
        back_populates="appointments",
        foreign_keys="[Appointment.customer_id]",
    )

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return (
            f"Appointment(id={self.id}, date={self.date}, "
            f"customer_id={self.customer_id}, duration=({self.duration}))"
        )

    @property
    def end_date(self) -> datetime:
        return self.date + timedelta(minutes=self.duration)

    @property
    def time_to_appointment(self) -> timedelta:
        return self.date - datetime.now()

    def get_customer(self) -> customer.Customer:  # type: ignore
        return self.customer

    def time_between_appointments(self, appointment: Appointment) -> timedelta:
        if self.date > appointment.date:
            return self.date - appointment.end_date
        return appointment.date - self.end_date

    def time_between_dates(self, date: datetime) -> timedelta:
        return abs(self.date - date)

    def to_dict(self):
        dict_: dict[str, Any] = {}
        dict_.update(self.__dict__)
        for k in dict_.keys():
            if k.startswith("_"):
                dict_.pop(k)
