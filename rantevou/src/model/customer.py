from sqlalchemy.orm import Mapped, mapped_column, relationship
from .session import Base, SessionLocal
from . import appointment
from ..controller.logging import Logger

logger = Logger("customer-model")


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

    @property
    def full_name(self):
        return f"{self.name} {self.surname or ''}"

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


class CustomerModel:
    # TODO more functionality, error checking etc
    def add_customer(self, customer: Customer) -> int:
        with SessionLocal() as session:
            session.add(customer)
            session.commit()

            customer_with_id = (
                session.query(Customer).filter_by(email=customer.email).first()
            )

            if customer_with_id is None:
                logger.log_error("Failed to retrieve customer id after insertion")
                raise Exception(f"DB Error on {customer}")
            return customer_with_id.id
