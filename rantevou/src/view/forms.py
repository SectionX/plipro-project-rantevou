from typing import Sequence
from datetime import datetime, timedelta
from tkinter import ttk
import tkinter as tk
from .exceptions import *
from .abstract_views import EntryWithPlaceholder
from ..controller.logging import Logger
from ..model.entities import Appointment, Customer

logger = Logger("entry")


class AppointmentForm(ttk.Frame):
    """
    Φόρμα εισαγωγής/επεξεργασίας ραντεβού
    """

    values: Sequence | None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.anchor("nw")
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        self.columnconfigure(2, weight=2)
        self.columnconfigure(3, weight=2)

        self.data_id: int | None = None
        self.data_date: datetime = datetime(1970, 1, 1)
        self.data_is_alerted: bool = False
        self.data_duration: timedelta | None = None
        self.data_customer_id: int | None = None

        self.app_label_date = ttk.Label(self, text="Date")
        self.app_entry_day = ttk.Entry(self, width=2)
        self.app_entry_month = ttk.Entry(self, width=2)
        self.app_entry_year = ttk.Entry(self, width=4)

        self.app_label_time = ttk.Label(self, text="Time")
        self.app_entry_hour = ttk.Entry(self, width=2)
        self.app_entry_minute = ttk.Entry(self, width=2)

        self.app_label_duration = ttk.Label(self, text="Duration")
        self.app_entry_duration = ttk.Entry(self, width=2)

        self.app_label_date.grid(row=0, column=0, sticky="e", padx=3)
        self.app_entry_day.grid(row=0, column=1, sticky="we")
        self.app_entry_month.grid(row=0, column=2, sticky="we")
        self.app_entry_year.grid(row=0, column=3, sticky="we")

        self.app_label_time.grid(row=1, column=0, sticky="e", padx=3)
        self.app_entry_hour.grid(row=1, column=1, sticky="we")
        self.app_entry_minute.grid(row=1, column=2, sticky="we")

        self.app_label_duration.grid(row=2, column=0, sticky="e", padx=3)
        self.app_entry_duration.grid(row=2, column=1, sticky="we")

    def split_date(self, date: datetime):
        return date.strftime("%Y+%m+%d+%H+%M+%S").split("+")

    def assemble_date(self, items: list[str]):
        if len(items) <= 6:
            return datetime(*map(int, items))  # type: ignore
        else:
            raise ViewInternalError("Datetime needs up to 6 fields")

    def reset(self):
        for v in self.__dict__.values():
            if isinstance(v, ttk.Entry):
                v.delete(0, tk.END)

    def get(self) -> Appointment:
        try:
            return Appointment(
                id=self.data_id,
                date=self.assemble_date(
                    [
                        self.app_entry_year.get(),
                        self.app_entry_month.get(),
                        self.app_entry_day.get(),
                        self.app_entry_hour.get(),
                        self.app_entry_minute.get(),
                    ]
                ),
                duration=timedelta(minutes=int(self.app_entry_duration.get())),
                is_alerted=self.data_is_alerted,
                customer_id=self.data_customer_id,
            )
        except ValueError as e:
            raise ViewInputError(str(e))
        except Exception as e:
            raise ViewInternalError(str(e))

    def populate(self, appointment: Appointment | list):
        self.reset()

        values: Sequence | None = None
        if isinstance(appointment, Appointment):
            values = appointment.values

        if isinstance(appointment, Sequence):
            values = appointment

        if values is None:
            raise ViewWrongDataError(self, self, values)

        (
            self.data_id,
            self.data_date,
            self.data_is_alerted,
            self.data_duration,
            self.data_customer_id,
        ) = values
        (
            self.data_year,
            self.data_month,
            self.data_day,
            self.data_hour,
            self.data_minute,
            _,
        ) = self.split_date(self.data_date)

        for k, v in self.__dict__.items():
            if k.startswith("data_"):
                name = k.rsplit("_", maxsplit=1)[-1]
                entry = self.__dict__.get(f"app_entry_{name}")
                if isinstance(entry, ttk.Entry):
                    if isinstance(v, timedelta):
                        v = str(int(v.total_seconds() // 60))
                    entry.insert(0, v)


class CustomerForm(ttk.Frame):
    """
    Φορμα εγγραφής/επεξεργασίας πελάτη
    """

    values: Sequence | None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_id: str | None = None
        self.data_name: str | None = None
        self.data_surname: str | None = None
        self.data_phone: str | None = None
        self.data_email: str | None = None

        self.cus_label_name = ttk.Label(self, text="Name")
        self.cus_label_surname = ttk.Label(self, text="Surname")
        self.cus_label_phone = ttk.Label(self, text="Phone")
        self.cus_label_email = ttk.Label(self, text="email")

        self.cus_entry_name = ttk.Entry(
            self,
        )
        self.cus_entry_surname = ttk.Entry(
            self,
        )
        self.cus_entry_phone = ttk.Entry(self)
        self.cus_entry_email = ttk.Entry(self)

        for i in range(2):
            self.columnconfigure(i, weight=1)

        self.cus_label_name.grid(column=0, row=0, sticky="nse")
        self.cus_label_surname.grid(column=0, row=1, sticky="nse")
        self.cus_label_phone.grid(column=0, row=2, sticky="nse")
        self.cus_label_email.grid(column=0, row=3, sticky="nse")

        self.cus_entry_name.grid(column=1, row=0, sticky="nse")
        self.cus_entry_surname.grid(column=1, row=1, sticky="nse")
        self.cus_entry_phone.grid(column=1, row=2, sticky="nse")
        self.cus_entry_email.grid(column=1, row=3, sticky="nse")

    def reset(self):
        for v in self.__dict__.values():
            if isinstance(v, ttk.Entry):
                v.delete(0, tk.END)

    def get(self):
        return Customer(
            id=self.data_id,
            name=self.cus_entry_name.get(),
            surname=self.cus_entry_surname.get(),
            phone=self.cus_entry_phone.get(),
            email=self.cus_entry_email.get(),
        )

    def populate(self, customer: Customer | Sequence | None):
        self.reset()
        if customer is None:
            for k, v in self.__dict__.items():
                if k.startswith("data"):
                    v = None
                if isinstance(v, EntryWithPlaceholder):
                    v.put_placeholder()
            return

        values: Sequence | None = None
        if isinstance(customer, Customer):
            values = customer.values

        if isinstance(customer, Sequence):
            values = customer

        if values is not None:
            (
                self.data_id,
                self.data_name,
                self.data_surname,
                self.data_phone,
                self.data_email,
                *_,
            ) = values

            for k, v in self.__dict__.items():
                if k.startswith("data_"):
                    name = k.rsplit("_", maxsplit=1)[-1]
                    entry = self.__dict__.get(f"cus_entry_{name}")
                    if isinstance(entry, ttk.Entry):
                        if v is None:
                            v = ""
                        entry.insert(0, v)
        else:
            raise ViewWrongDataError(self, self.master, customer)
