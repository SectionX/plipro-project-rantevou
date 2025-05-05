from __future__ import annotations


import re
import unicodedata
from datetime import datetime, timedelta
from typing import Any


from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase, validates
from sqlalchemy import ForeignKey

from .exceptions import ValidationError


class Base(DeclarativeBase): ...


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
    customer_id: Mapped[int | None] = mapped_column(ForeignKey("customer.id"), nullable=True)
    employee_id: Mapped[int] = mapped_column(default=0)

    customer = relationship(
        "Customer",
        back_populates="appointments",
        foreign_keys="[Appointment.customer_id]",
    )

    def __str__(self) -> str:
        return (
            f"Appointment(id={self.id}, date={self.date}, "
            f"customer_id={self.customer_id}, duration=({self.duration}))"
        )

    @validates("id", "customer_id", "employee_id")
    def __id_validator(self, key, value):
        if value is None:
            return None

        if isinstance(value, int):
            return value

        try:
            return int(value)
        except (TypeError, ValueError):
            try:
                return int(str(value))
            except ValueError as e:
                raise ValidationError(f"{key} must be numeric") from e

    @validates("duration")
    def __duration_validator(self, key, value):
        if isinstance(value, timedelta):
            return value

        if value is None:
            return timedelta(0)

        if isinstance(value, int):
            return timedelta(minutes=value)

        if isinstance(value, dict):
            try:
                return timedelta(**value)
            except ValueError as e:
                raise ValidationError(key) from e

        if isinstance(value, str):
            if value.isdigit():
                return timedelta(minutes=int(value))
            else:
                raise ValidationError(key)

        raise ValidationError(key)

    @validates("date")
    def __date_validator(self, key, value):
        if isinstance(value, datetime):
            return value

        if isinstance(self, dict):
            try:
                datetime(**value)
            except ValueError as e:
                raise ValidationError(f"Error trying to convert dict to datetime") from e

        if isinstance(value, str):
            try:
                return datetime.strptime(value, "%d/%m/%Y, %H:%M:%S")
            except ValueError as e:
                pass

            try:
                return datetime.strptime(value, "%d/%m/%Y, %H:%M")
            except ValueError as e:
                raise ValidationError("Date string must be %d/%m/%Y, %H:%M:%S") from e

        if value is None:
            raise ValidationError("Date can't be None")

        raise ValidationError(key)

    @validates("is_alerted")
    def __alert_validator(self, key, value):
        try:
            return bool(value)
        except Exception as e:
            raise ValidationError(key) from e

    @property
    def values(self) -> tuple[int, datetime, bool, timedelta, int | None]:
        """
        Επιστρέφει πλειάδα με τα δεδομένα του ραντεβού

        Returns:
            tuple[int, datetime, bool, timedelta, int | None]: Τα στοιχεία του ραντεβού σε μορφή λίστας
        """
        return (self.id, self.date, self.is_alerted, self.duration, self.customer_id)

    @property
    def end_date(self) -> datetime:
        """
        Υπολογίζει το τέλος του ραντεβού

        Returns:
            datetime: Ημερομηνία περάτωσης του ραντεβού
        """
        return self.date + self.duration

    @property
    def time_to_appointment(self) -> timedelta:
        """
        Υπολογίζει πόσος χρόνος απομένει μέχρι το ραντεβού

        Returns:
            timedelta: Χρόνος μέχρι το ραντεβού
        """
        return self.date - datetime.now()

    def overlap(self, other: Appointment) -> bool:
        """
        Ελέγχει εάν κάνουν overlap οι ημερομηνίες και διάρκειες των ραντεβού

        Args:
            other (Appointment)

        Returns:
            bool: True εαν συμπίπτουν, αλλιώς False
        """
        if self.id == other.id:
            return False
        return not (self.date >= other.end_date or self.end_date <= other.date)

    def time_between_appointments(self, appointment: Appointment) -> timedelta:
        """
        Υπολογίζει τον χρόνο μεταξύ 2 ραντεβού λαμβάνοντας υπόψην τον χρόνο ολοκλήρωσης αυτών

        Η χρονική σειρά δεν έχει σημασία.

        Args:
            appointment (Appointment)

        Returns:
            timedelta: Χρόνος από το τέλος του ενός μέχρι την αρχή του άλλου.
        """

        if self.date > appointment.date:
            return self.date - appointment.end_date
        return appointment.date - self.end_date

    def time_between_dates(self, date: datetime) -> timedelta:
        """
        Βοηθητική συνάρτηση υπολογισμού χρόνου με αγνωστικό χαρακτήρα
        """
        return abs(self.date - date)

    def to_dict_api(self) -> dict[str, Any]:
        """
        Αναπαράσταση του ραντεβού σε JSON-compatible μορφη για χρήση από το webapi server

        Returns:
            dict[str, Any]: Αναπαράσταση του ραντεβού
        """
        dict_: dict[str, int | str | float | None] = {}
        dict_["id"] = self.id
        dict_["date"] = self.date.strftime("%d/%m/%Y, %H:%M:%S")
        dict_["duration"] = self.duration.total_seconds() // 60
        dict_["end_date"] = self.end_date.strftime("%d/%m/%Y, %H:%M:%S")
        dict_["customer_id"] = self.customer_id
        dict_["employee_id"] = self.employee_id
        return dict_

    def to_dict_native(self):
        """
        Αναπαράσταση του ραντεβού σε μορφή dict για χρήση από αντικείμενα που δεν αποδέχονται
        τύπο Appointment

        Returns:
            dict[str, Any]: Αναπαράσταση του ραντεβού
        """
        dict_: dict[str, int | str | float | datetime | timedelta | None] = {}
        dict_["id"] = self.id
        dict_["date"] = self.date
        dict_["duration"] = self.duration
        dict_["end_date"] = self.end_date
        dict_["customer_id"] = self.customer_id
        dict_["employee_id"] = self.employee_id
        return dict_


class Customer(Base):
    """
    Ορισμός της οντότητας "πελάτης"

    * id: Εσωτερικός μοναδικός αριθμός. Παράγεται από την βάση δεδομένων.
    * name: Όνομα του πελάτη, δεν μπορεί να είναι κενό
    * surname: Επώνυμο του πελάτη
    * normalized_name: Όνομα χωρίς τόνους και κεφαλαία.
    * normalized_surname: Επώνυμο χωρίς τόνους και κεφαλαία
    * email: Email του πελάτη, πρέπει να είναι μοναδικό
    * phone: Τηλέφωνο του πελάτη, πρέπει να είναι μοναδικό

    Τα normalized στοιχεία παράγονται από το μοντέλο πριν την εισαγωγή
    στην βάση δεδομένων και εξυπηρετούν σκοπούς αναζήτησης επειδή η sqlite3
    δεν υποστηρίζει case insensitive search σε unicode και δεν ξέρει πως
    να διαχειριστεί τους τόνους
    """

    phone_pattern = re.compile(r"\+?[\s\d]+$")
    email_pattern = re.compile(r"(\S+?)@(\S+?)\.([^\.\s]+)$")

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

    @validates("name", "surname")
    def __name_validator(self, key, value):
        if value is None:
            return value

        value = str(value)

        if value == "":
            return None

        normalized = unicodedata.normalize("NFKD", value)
        normalized = normalized.lower().replace("́", "")

        if key == "name":
            self.normalized_name = normalized

        if key == "surname":
            self.normalized_surname = normalized

        return value

    @validates("phone")
    def __phone_validator(self, key, value):
        if value is None:
            return None

        value = str(value).strip()
        if value.strip() == "":
            return None

        value = value.strip().replace(" ", "").replace("-", "").replace("_", "").replace("+", "00")
        if not value.isdigit():
            raise ValidationError(key)

        if len(value) == 10 or len(value) == 14:
            return value

        raise ValidationError(key, value)

    @validates("email")
    def __email_validator(self, key, value):
        if value is None:
            return value

        value = str(value)
        if value.strip() == "":
            return None

        match = self.email_pattern.match(value)
        if match is not None:
            return value

        raise ValidationError(key, value)

    @property
    def full_name(self) -> str:
        """
        Returns:
            str: Ονοματεπώνυμο
        """
        return f"{self.name} {self.surname or ''}"

    @property
    def values(self) -> list:
        """
        Returns:
            list: Τιμές των πεδίων
        """
        return [
            self.id,
            self.name,
            self.surname,
            self.phone,
            self.email,
        ]

    @classmethod
    def field_names(cls) -> list[str]:
        """
        Είναι αντίστοιχα με την σειρά που επιστρέφει η .values

        Returns:
            list[str]: Λίστα με όνοματα ορισμάτων
        """
        return ["id", "name", "surname", "phone", "email"]

    def __str__(self) -> str:
        return (
            f"Customer(id={self.id}, name={self.name}, "
            f"surname={self.surname}, email={self.email}"
            f", phone={self.phone})"
        )

    def to_dict_api(self) -> dict[str, str]:
        """
        Αναπαράσταση σε JSON-compatible μορφη για χρήση από το webapi server

        Returns:
            dict[str, Any]: Αναπαράσταση του πελάτη
        """
        dict_ = {
            "name": self.name,
            "surname": self.surname,
            "phone": self.phone,
            "email": self.email,
        }
        return dict_
