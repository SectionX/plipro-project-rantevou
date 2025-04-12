from __future__ import annotations
from datetime import datetime, timedelta
from typing import Any
from collections import defaultdict

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from .session import Base, SessionLocal
from . import customer

from typing import Protocol


class Subscriber(Protocol):
    """
    Interface για όλα τα στοιχεία που κάνουν subscribe για να
    ενημερώνονται όταν γίνονται σημαντικές αλλαγές στην  βάση
    δεδομένων
    """

    def subscriber_update(self):
        pass


class Appointment(Base):
    """
    Ορισμός της οντότητας "ραντεβού"
    """

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
        """
        Υπολογίζει την ακριβή ημερομηνία που θα πρέπει να έχει
        ολοκληρωθεί το ραντεβού
        """
        return self.date + timedelta(minutes=self.duration)

    @property
    def time_to_appointment(self) -> timedelta:
        """
        Υπολογίζει τον χρόνο που απομένει μέχρι το ραντεβού
        """
        return self.date - datetime.now()

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


class AppointmentModel:
    """
    Ορίζει το μοντέλο των δεδομένων και διαχειρίζεται την αναζήτηση και
    ανάκτηση πληροφορίας.
    """

    appointments: list[Appointment]
    subscribers: list[Subscriber]

    def __init__(self):
        self.subscribers = []
        self.appointments = []
        self.session = SessionLocal()
        self.appointments = self.get_appointments(cached=False)

    def sort(self, list_=None) -> list[Appointment]:
        """
        Sort με βάση τον χρόνο επειδή είναι η πιο χρήσιμη
        πληροφορία αυτής της οντότητας.
        """
        if list_:
            list_.sort(key=lambda x: x.date)
            return list_
        else:
            self.appointments.sort(key=lambda x: x.date)
            return self.appointments

    def add_appointment(self, appointment: Appointment):
        self.session.add(appointment)
        self.session.commit()
        appointment_with_id = (
            self.session.query(Appointment)
            .filter(Appointment.date == appointment.date)
            .first()
        )

        if appointment_with_id:
            self.add_to_cache(appointment_with_id)

        self.update_subscribers()

    def update_appointment(self, new: Appointment):
        target = None

        old = self.session.query(Appointment).filter_by(id=new.id).first()
        if old:
            self.replace_in_cache(old, new)
            self.appointments.append(new)
            old.id = new.id
            old.date = new.date
            old.is_alerted = new.is_alerted
            old.duration = new.duration
            old.customer_id = new.customer_id
        self.session.commit()

        if target:
            self.appointments[self.appointments.index(target)] = new
        self.update_subscribers()

    def delete_appointment(self, appointment: Appointment):
        self.session.delete(appointment)
        self.appointments.remove(appointment)
        self.sort()
        self.update_subscribers()

    def get_appointments(self, cached=True) -> list[Appointment]:
        """
        Το μοντέλο είναι ρυθμισμένο να κρατάει τα δεδομένα στην μνήμη
        """
        if cached:
            return self.appointments

        query = self.session.query(Appointment).all()
        return self.sort(query)

    def get_appointment_by_id(self, appointment_id: int) -> Appointment | None:
        """
        Συνάρτηση συνήθους περίπτωσης
        """
        return self.session.query(Appointment).filter_by(id=appointment_id).first()

    def get_appointment_by_date(self, date: datetime) -> Appointment | None:
        """
        Συνάρτηση συνήθους περίπτωσης
        """
        return self.session.query(Appointment).filter_by(date=date).first()

    def get_appointments_from_to_date(
        self, from_date: datetime, to_date: datetime
    ) -> list[Appointment]:
        """
        Συνάρτηση συνήθους περίπτωσης
        """
        return (
            self.session.query(Appointment)
            .filter(Appointment.date >= from_date, Appointment.date < to_date)
            .all()
        )

    def add_subscriber(self, subscriber: Subscriber):
        """
        Απαραίτητο όλοι οι subscribers να υλοποιούν το subscriber
        interface
        """
        self.subscribers.append(subscriber)

    def update_subscribers(self):
        """
        Ενημέρωση των subscribers
        """
        for subscriber in self.subscribers:
            subscriber.subscriber_update()

    def split_appointments_in_periods(
        self,
        period: timedelta,
        start: datetime | None = None,
    ) -> dict[int, list[Appointment]]:
        """
        Συνάρτηση συνήθους περίπτωσης
        """
        if start is None:
            start = self.appointments[0].date

        dict_: dict[int, list[Appointment]] = defaultdict(list)
        for appointment in self.appointments:
            index = (appointment.date - start) // period
            dict_[index].append(appointment)

        return dict_

    def get_appointment_period_index(
        self,
        appointment: Appointment,
        period: timedelta,
        start: datetime | None = None,
    ) -> int:
        """
        Συνάρτηση συνήθους περίπτωσης, βοηθητική της
        split_appointments_in_periods
        """
        if start is None:
            start = self.appointments[0].date

        return (appointment.date - start) // period

    def get_time_between_appointments(
        self,
        start_date: datetime | None = None,
        minumum_free_period: timedelta | None = None,
    ) -> list[tuple[datetime, timedelta]]:
        """
        Συνάρτηση συνήθους περίπτωσης. Λύνει την περίπτωση εύρεσης
        χρόνου μεταξύ των ραντεβού
        """
        result: list[tuple[datetime, timedelta]] = []

        if start_date is None:
            start_date = self.appointments[0].date

        if minumum_free_period is None:
            minumum_free_period = timedelta(0)

        for i, appointment in enumerate(self.appointments):
            if appointment.date < start_date:
                continue

            if i == len(self.appointments) - 1:
                break

            previous = appointment
            next = self.appointments[i + 1]
            diff = previous.time_between_appointments(next)
            if diff > minumum_free_period:
                result.append((previous.end_date, diff))

        return result

    def replace_in_cache(self, target, new):
        """
        Συνάρτηση ενημέρωσης του cache
        """
        i = self.appointments.index(target)
        self.appointments[i] = new

    def add_to_cache(self, target):
        """
        Συνάρτηση ενημέρωσης του cache
        """
        for i in range(len(self.appointments) - 1, 0, -1):
            if self.appointments[i].date > target.date:
                continue
            self.appointments.insert(i + 1, target)
            break

    def delete_from_cache(self, target):
        """
        Συνάρτηση ενημέρωσης του cache
        """
        self.appointments.remove(target)
