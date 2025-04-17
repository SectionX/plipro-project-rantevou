from __future__ import annotations
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Protocol
from .session import Base, session
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
    def full_name(self) -> str:
        return f"{self.name} {self.surname or ''}"

    @property
    def values(self) -> list:
        return [
            self.id,
            self.name,
            self.surname,
            self.phone,
            self.email,
        ]

    @classmethod
    def field_names(cls) -> list[str]:
        return ["id", "name", "surname", "phone", "email", "appointments"]

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
    _instance = None
    session = session

    def __new__(cls, *args, **kwargs) -> CustomerModel:
        if cls._instance is None:
            cls._instance = super(CustomerModel, cls).__new__(cls, *args, **kwargs)
            cls.customers = session.query(Customer).all()
            cls.subscribers = []
            if len(cls.customers) > 0:
                cls.max_id = max(cls.customers, key=lambda x: x.id).id
            else:
                cls.max_id = 0

        return cls._instance

    def sanitize(self, customer: Customer):
        for k, v in customer.__dict__.items():
            if k.startswith("_"):
                continue
            if isinstance(v, str) and v == "":
                customer.__dict__[k] = None

    def is_similar(self, customer1: Customer, customer2: Customer) -> bool:
        return all(
            (
                customer1.name == customer2.name,
                customer1.surname == customer2.surname,
                customer1.phone == customer2.phone,
                customer1.email == customer2.email,
            )
        )

    def get_fields(self) -> list[str]:
        return ["id", "name", "surname", "phone", "email", "appointments"]

    def filter_by_all(self, customer: Customer) -> Customer | None:
        return (
            session.query(Customer)
            .filter(
                Customer.name == customer.name,
                Customer.surname == customer.surname,
                Customer.phone == customer.phone,
                Customer.email == customer.email,
            )
            .first()
        )

    def add_customer(self, customer: Customer) -> tuple[int | None, bool]:
        """
        Δημιουργία καινούριου πελάτη. Ελέγχει αν υπάρχει ήδη ο πελάτης
        πριν τον προσθέσει στην βάση δεδομένων. Ισότητα σημαίνει όλα τα
        πεδία είναι ίδια.

        Επιστρέφει πλειάδα tuple(customer.id, επιτυχία προσθήκης)
        """
        logger.log_info(f"Excecuting creation of {customer}")

        # Σημαντική προεπεξεργασία ώστε τα κενά strings να μετατρέπονται
        # σε None. Αλλιώς θεωρεί ότι το "" είναι πληροφορία και δεν δέχεται
        # δεύτερο πελάτη με κενό τηλέφωνο η email.
        self.sanitize(customer)

        # Έλεγχος ύπαρξης πελάτη
        existing_customer = self.filter_by_all(customer)
        if existing_customer is not None:
            logger.log_info(f"{existing_customer} already exists")
            return existing_customer.id, False

        # Προσθήκη νέου πελάτη
        if existing_customer is None:
            try:
                session.add(customer)
                session.commit()
                self.max_id += 1
                logger.log_info(f"Assigned id={self.max_id}")
            except Exception as e:
                logger.log_error(str(e))
                session.rollback()
                return None, False

        # Έλεγχος ορθής προσθήκης
        new_customer = self.get_customer_by_id(self.max_id)
        if new_customer is None:
            logger.log_error("Failed to retrieve customer id after insertion")
            raise Exception(f"DB Error on {customer}")

        # Ενημέρωση subscriber
        self.add_to_cache(new_customer)
        self.notify_subscribers()
        return self.max_id, True

    def delete_customer(self, customer: Customer) -> bool:
        """
        Διαγραφή πελάτη. Επιβάλλει την ύπαρξη customer.id πριν την
        διαγραφή.

        Επιστρέφει boolean επιτυχούς διαγραφής
        """
        logger.log_info(f"Excecuting deletion of {customer}")

        # Επιβολή ύπαρξης id
        if customer.id is None:
            logger.log_warn(f"{customer} does not have an id")
            return False

        # Διαγραφή πελάτη. To query είναι αναγκαίο για το sqlalchemy
        customer_to_delete = self.get_customer_by_id(customer.id)
        try:
            session.delete(customer_to_delete)
            session.commit()
        except Exception as e:
            logger.log_error(str(e))
            session.rollback()
            return False

        # Έλεγχος επιτυχούς διαγραφής
        # TODO: Μπορεί να αφαιρεθεί μόνο μετά από εξωνυχιστικό testing
        deleted_customer = self.get_customer_by_id(customer.id)
        if deleted_customer is not None:
            logger.log_error(f"Failed to delete {customer}")
            raise Exception(f"DB Error on {customer}")

        # Ενημέρωση cache και max_id για ευκολότερη διαχείρηση
        self.delete_from_cache(customer_to_delete)
        if len(self.customers) == 0:
            self.max_id = 0
        else:
            self.max_id = max(self.customers, key=lambda x: x.id).id

        # Ενημέρωση subscriber
        self.notify_subscribers()
        return True

    def update_customer(self, new_customer: Customer) -> bool:
        """
        Ενημέρωση στοιχείων πελάτη. Ελέγχει αν ήδη υπάρχει ο πελάτης
        πριν τον ενημερώσει.

        Επιστρέφει boolean επιτυχούς ενημέρωσης
        """
        logger.log_info(f"Excecuting update of {new_customer}")

        self.sanitize(new_customer)

        # Αναζητεί την παλιά εγγραφή του πελάτη
        old_customer = None
        if new_customer.id is not None:
            old_customer = self.get_customer_by_id(new_customer.id)

        if new_customer.id is None:
            old_customer = self.filter_by_all(new_customer)

        if old_customer is None:
            logger.log_warn(f"{new_customer} does not exist in database")
            return False

        if self.is_similar(old_customer, new_customer):
            logger.log_info(f"{new_customer} has not changed")
            return False

        # Ενημερώνει με τα καινούρια στοιχεία
        old_customer.name = new_customer.name
        old_customer.surname = new_customer.surname
        old_customer.phone = new_customer.phone
        old_customer.email = new_customer.email

        # Εκτελεί την ενημέρωση στην βάση δεδομένων
        try:
            session.commit()
        except Exception as e:
            logger.log_error(str(e))
            session.rollback()
            return False

        updated_customer = self.get_customer_by_id(old_customer.id)
        if updated_customer is None:
            logger.log_error(f"Failed to update {new_customer}")
            raise Exception(f"DB Error on {new_customer}")

        # Ενημερώνει το cache και τους subscribers
        # Σημαντικό να χρησιμοποιηθεί το αποτέλεσμα του νέου query και όχι ο πελάτης της παραμέτρου
        self.update_in_cache(old_customer)
        self.notify_subscribers()
        return True

    def get_customer_by_id(self, id: int) -> Customer | None:
        return session.query(Customer).filter_by(id=id).first()

    def get_customer_by_email(self, email: str) -> Customer | None:
        return session.query(Customer).filter_by(email=email).first()

    def get_customer_by_phone(self, phone: str) -> Customer | None:
        return session.query(Customer).filter_by(phone=phone).first()

    def get_customers(self) -> list[Customer]:
        if len(self.customers) == 0:
            self.customers = session.query(Customer).all()
        return self.customers

    def add_subscriber(self, subscriber: Subscriber) -> None:
        logger.log_info(f"Excecuting subscription of {subscriber}")
        self.subscribers.append(subscriber)

    def notify_subscribers(self) -> None:
        logger.log_info(
            f"Excecuting notification of {len(self.subscribers)} subscribers"
        )
        for sub in self.subscribers:
            sub.subscriber_update()

    def add_to_cache(self, customer) -> None:
        self.customers.append(customer)

    def delete_from_cache(self, customer) -> None:
        self.customers.remove(customer)

    def update_in_cache(self, customer) -> None:
        for i, cached_customer in enumerate(self.customers):
            if cached_customer.id == customer.id:
                self.customers[i] = customer
                break
