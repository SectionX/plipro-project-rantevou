from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from .session import Base


class Appointment(Base):
    """
    Ορισμός της οντότητας "ραντεβού"
        id: Εσωτερικός μοναδικός αριθμός, παράγεται από την βάση δεδομένων
        date: Ημερομηνία του ραντεβού, μικρότερες μονάδες από τα λεπτά αγνοούνται
        is_alerted: Εάν ο πελάτης έχει ενημερωθεί με email
        customer_id: Εξωτερικό κλειδί, id του πελάτη που σχετίζεται με το ραντεβού
        employee_id: Για μελλοντική χρήση, το id του εργαζόμενου που εξυπηρετεί
        customer: Ο πελάτης που έχει σχέση με το ραντεβού, ορίζεται από το customer_id
    """

    __tablename__ = "appointment"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    date: Mapped[datetime] = mapped_column(nullable=False, unique=True, index=True)
    is_alerted: Mapped[bool] = mapped_column(default=False)
    duration: Mapped[timedelta] = mapped_column(default=timedelta(minutes=20))
    customer_id: Mapped[int | None] = mapped_column(
        ForeignKey("customer.id"), nullable=True
    )
    employee_id: Mapped[int] = mapped_column(default=0)

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
    def values(self) -> tuple[int, datetime, bool, timedelta, int | None]:
        return (self.id, self.date, self.is_alerted, self.duration, self.customer_id)

    @property
    def end_date(self) -> datetime:
        """
        Υπολογίζει την ακριβή ημερομηνία που θα πρέπει να έχει
        ολοκληρωθεί το ραντεβού
        """
        return self.date + self.duration

    @property
    def time_to_appointment(self) -> timedelta:
        """
        Υπολογίζει τον χρόνο που απομένει μέχρι το ραντεβού
        """
        return self.date - datetime.now()

    def overlap(self, other: Appointment):
        if self.id == other.id:
            return False
        return not (self.date >= other.end_date or self.end_date <= other.date)

    def time_between_appointments(self, appointment: Appointment) -> timedelta:
        """
        Υπολογίζει τον χρόνο μεταξύ 2 ραντεβού λαμβάνοντας υπόψην
        τον χρόνο ολοκλήρωσης αυτών
        """
        if self.date > appointment.date:
            return self.date - appointment.end_date
        return appointment.date - self.end_date

    def time_between_dates(self, date: datetime) -> timedelta:
        """
        Βοηθητική συνάρτηση υπολογισμού χρόνου με αγνωστικό
        χαρακτήρα
        """
        return abs(self.date - date)

    def to_dict(self):
        """
        Μετατροπή του τύπου Appointment σε τύπο dict
        """
        dict_: dict[str, Any] = {}
        dict_.update(self.__dict__)
        for k in dict_.keys():
            if k.startswith("_"):
                dict_.pop(k)


class Customer(Base):
    """
    Ορισμός της οντότητας "πελάτης"
        id: Εσωτερικός μοναδικός αριθμός. Παράγεται από την βάση δεδομένων.
        name: Όνομα του πελάτη, δεν μπορεί να είναι κενό
        surname: Επώνυμο του πελάτη
        normalized_name: Όνομα χωρίς τόνους και κεφαλαία.
        normalized_surname: Επώνυμο χωρίς τόνους και κεφαλαία
        email: Email του πελάτη, πρέπει να είναι μοναδικό
        phone: Τηλέφωνο του πελάτη, πρέπει να είναι μοναδικό

    Τα normalized στοιχεία παράγονται από το μοντέλο πριν την εισαγωγή
    στην βάση δεδομένων και εξυπηρετούν σκοπούς αναζήτησης επειδή η sqlite3
    δεν υποστηρίζει case insensitive search σε unicode και δεν ξέρει πως
    να διαχειριστεί τους τόνους
    """

    __tablename__ = "customer"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    surname: Mapped[str] = mapped_column(nullable=True)
    normalized_name: Mapped[str] = mapped_column(nullable=False, index=True)
    normalized_surname: Mapped[str] = mapped_column(nullable=True, index=True)
    email: Mapped[str] = mapped_column(unique=True, nullable=True, index=True)
    phone: Mapped[str] = mapped_column(unique=True, nullable=True, index=True)

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
        return ["id", "name", "surname", "phone", "email"]

    def __str__(self) -> str:
        return (
            f"Customer(id={self.id}, name={self.name}, "
            f"surname={self.surname}, email={self.email}"
            f", phone={self.phone})"
        )

    def __repr__(self) -> str:
        return self.__str__()
