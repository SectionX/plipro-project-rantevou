from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey

from .session import Base


class Appointment(Base):
    __tablename__ = "appointment"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime]
    customer_id: Mapped[int] = mapped_column(ForeignKey("customer.id"))

    def __repr__(self):
        return (
            f"Appointment(id={self.id}, date={self.date}, "
            f"customer_id={self.customer_id})"
        )
