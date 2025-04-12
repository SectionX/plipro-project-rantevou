from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Protocol
from .session import Base, session
from . import appointment
from ..controller.logging import Logger

logger = Logger("customer-model")


class Subscriber(Protocol):
    def subscriber_update(self): ...


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

    @property
    def values(self):
        return [
            self.id,
            self.name,
            self.surname,
            self.phone,
            self.email,
            self.appointments,
        ]

    def __str__(self) -> str:
        return (
            f"Customer(id={self.id}, name={self.name}, "
            f"surname={self.surname}, email={self.email}"
            f", phone={self.phone})"
        )

    def __repr__(self) -> str:
        return self.__str__()


class CustomerModel:
    # TODO more functionality, error checking etc
    customers: list[Customer]
    subscribers: list[Subscriber]

    def __init__(self):
        self.session = session
        self.customers = session.query(Customer).all()
        self.subscribers = []

    def get_fields(self):
        return ["id", "name", "surname", "phone", "email", "appointments"]

    def add_customer(self, customer: Customer) -> int:
        session.add(customer)
        session.commit()

        customer_with_id = (
            session.query(Customer).filter_by(email=customer.email).first()
        )
        # TODO update cache
        if customer_with_id is None:
            logger.log_error("Failed to retrieve customer id after insertion")
            raise Exception(f"DB Error on {customer}")

        self.notify_subscribers()
        return customer_with_id.id

    def delete_customer(self, customer):
        session.delete(customer)
        session.commit()
        self.notify_subscribers()
        # TODO update cache

    def update_customer(self, new_customer: Customer):
        old_customer = (
            session.query(Customer).filter_by(email=new_customer.email).first()
        )
        if old_customer is None:
            # TODO handle
            return

        old_customer.email = new_customer.email
        old_customer.name = new_customer.name
        old_customer.surname = new_customer.surname
        old_customer.phone = new_customer.phone
        session.commit()
        logger.log_info(f"Updated customer {new_customer}")
        self.notify_subscribers()
        # TODO update cache

    def get_customer_by_id(self, id: int):
        return session.query(Customer).filter_by(id=id).first()

    def get_customer_by_email(self, email: str):
        return session.query(Customer).filter_by(email=email).first()

    def get_customers(self):
        return session.query(Customer).all()
        # TODO update and return cache instead

    def add_subscriber(self, subscriber: Subscriber):
        self.subscribers.append(subscriber)

    def notify_subscribers(self):
        print(self.subscribers)
        for sub in self.subscribers:
            logger.log_info(f"Notifying sub {sub}")
            sub.subscriber_update()
