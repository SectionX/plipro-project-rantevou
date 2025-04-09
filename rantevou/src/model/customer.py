from sqlalchemy.orm import Mapped, mapped_column, relationship
from .session import Base
from . import appointment


class Customer(Base):
    __tablename__ = "customer"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    surname: Mapped[str] = mapped_column(nullable=True)
    email: Mapped[str] = mapped_column(unique=True, nullable=True)
    phone: Mapped[str] = mapped_column(unique=True, nullable=True)

    appointments = relationship(
        "Appointment",
        back_populates="customer",
        foreign_keys="[Appointment.customer_id]",
    )

    def __str__(self) -> str:
        return (
            f"Customer(id={self.id}, name={self.name}, "
            f"surname={self.surname}, email={self.email}"
            f", phone={self.phone})"
        )

    def __repr__(self) -> str:
        return self.__str__()

    def get_appointments(self) -> list[appointment.Appointment]:
        return self.appointments
