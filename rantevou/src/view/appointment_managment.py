from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror
from datetime import datetime, timedelta
from typing import Literal

from .sidepanel import SidePanel
from .abstract_views import SideView, EntryWithPlaceholder
from ..model.types import Appointment, Customer
from ..controller.appointments_controller import AppointmentControl
from ..controller.logging import Logger
from ..controller.mailer import Mailer

ac = AppointmentControl()
logger = Logger("appointment-manager")
mailer = Mailer()


class EditAppointmentView(SideView):
    name: str = "edit"
    appointment: Appointment
    customer: Customer | None

    def __init__(self, master: SidePanel, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.name = self.__class__.name
        self.sidepanel = master
        self.main_frame = ttk.Frame(self, borderwidth=3, relief="sunken")
        self.main_frame.pack(fill="both", expand=True)
        self.back_btn.config(command=master.go_back)

        self.appointment = Appointment()
        self.customer = None

        self.date_frame = ttk.Frame(self.main_frame)
        self.date_frame.pack()

        self.hour_frame = ttk.Frame(self.main_frame)
        self.hour_frame.pack()

        self.app_entry_day = ttk.Entry(self.date_frame, width=2)
        self.app_entry_day.pack(side=tk.LEFT)
        ttk.Label(self.date_frame, text="/").pack(side=tk.LEFT)
        self.app_entry_month = ttk.Entry(self.date_frame, width=2)
        self.app_entry_month.pack(side=tk.LEFT)
        ttk.Label(self.date_frame, text="/").pack(side=tk.LEFT)
        self.app_entry_year = ttk.Entry(self.date_frame, width=4)
        self.app_entry_year.pack(side=tk.LEFT)

        self.app_entry_hour = ttk.Entry(self.hour_frame, width=2)
        self.app_entry_hour.pack(side=tk.LEFT)
        ttk.Label(self.hour_frame, text=":").pack(side=tk.LEFT)
        self.app_entry_minute = ttk.Entry(self.hour_frame, width=2)
        self.app_entry_minute.pack(side=tk.LEFT)

        self.app_entry_duration = ttk.Entry(self.main_frame)
        self.app_entry_duration.pack(fill="x")

        self.cus_entry_name = EntryWithPlaceholder(self.main_frame, placeholder="name")
        self.cus_entry_name.pack(fill="x")
        self.cus_entry_surname = EntryWithPlaceholder(
            self.main_frame, placeholder="surname"
        )
        self.cus_entry_surname.pack(fill="x")
        self.cus_entry_phone = EntryWithPlaceholder(
            self.main_frame, placeholder="phone number"
        )
        self.cus_entry_phone.pack(fill="x")
        self.cus_entry_email = EntryWithPlaceholder(
            self.main_frame, placeholder="email address"
        )
        self.cus_entry_email.pack(fill="x")
        self.save_button = ttk.Button(self.main_frame, text="Save", command=self.save)
        self.save_button.pack()
        self.delete_button = ttk.Button(
            self.main_frame, text="Delete", command=self.delete
        )
        self.delete_button.pack()

    def update_content(self, caller, caller_data):
        self.reset()
        logger.log_info(f"Showing data {caller_data} for editing")

        if caller_data is None:
            logger.log_warn("Failed to retrieve appointment data")
            return

        if not isinstance(caller_data, Appointment):
            logger.log_warn("Failed to retrieve appointment data")
            return

        self.appointment = caller_data
        if self.appointment is None:
            logger.log_warn("Failed to retrieve appointment data")
            raise ValueError

        self.customer = self.appointment.customer
        logger.log_info(f"Showing data {self.customer} for editing")

        date = self.appointment.date

        self.app_entry_year.insert(0, str(date.year))
        self.app_entry_month.insert(0, f"{date.month:02d}")
        self.app_entry_day.insert(0, f"{date.day:02d}")
        self.app_entry_hour.insert(0, f"{date.hour:02d}")
        self.app_entry_minute.insert(0, f"{date.minute:02d}")
        self.app_entry_duration.insert(
            0, str(int(self.appointment.duration.total_seconds() // 60))
        )

        if self.customer is None:
            self.cus_entry_name.put_placeholder()
            self.cus_entry_surname.put_placeholder()
            self.cus_entry_phone.put_placeholder()
            self.cus_entry_email.put_placeholder()
        else:
            self.cus_entry_name.insert(0, self.customer.name)
            if self.cus_entry_surname is not None:
                self.cus_entry_surname.insert(0, self.customer.surname)
            if self.cus_entry_phone is not None:
                self.cus_entry_phone.insert(0, self.customer.phone)
            if self.cus_entry_email is not None:
                self.cus_entry_email.insert(0, self.customer.email)

    def delete(self):
        # TODO Μετατροπή δεδομένων σε κατάλληλο τύπο και σύνδεση με την
        # βάση δεδομένων
        ac.delete_appointment(self.appointment)
        self.sidepanel.go_back()

    def save(self):
        # TODO Μετατροπή δεδομένων σε κατάλληλο τύπο και σύνδεση με την
        # βάση δεδομένων

        date = datetime(
            year=int(self.app_entry_year.get()),
            month=int(self.app_entry_month.get()),
            day=int(self.app_entry_day.get()),
            hour=int(self.app_entry_hour.get()),
            minute=int(self.app_entry_minute.get()),
        )

        new_appointment = Appointment(
            id=self.appointment.id,
            date=date,
            duration=timedelta(minutes=int(self.app_entry_duration.get())),
            is_alerted=self.appointment.is_alerted,
            customer_id=self.appointment.customer_id,
        )
        new_customer: Customer = Customer(
            name=self.cus_entry_name.get_without_placeholder(),
            surname=self.cus_entry_surname.get_without_placeholder(),
            phone=self.cus_entry_phone.get_without_placeholder(),
            email=self.cus_entry_email.get_without_placeholder(),
        )
        if self.customer is not None:
            new_customer.id = self.customer.id

        if new_customer.name == None:
            logger.log_info("Updating appointmenth without customer")
            result = ac.update_appointment(new_appointment)
        else:
            result = ac.update_appointment(new_appointment, new_customer)

        # if not result:
        #     showerror("Something went wrong...")
        # self.update_content(caller, caller_data)
        # sidepanel.
        self.sidepanel.go_back()

    def reset(self):
        for k, v in self.__dict__.items():
            if isinstance(v, ttk.Entry):
                v.delete(0, tk.END)

    def populate_from_customer_tab(self, customer_data):
        data = customer_data
        if not isinstance(data, list):
            logger.log_error("Data from customer was wrong type")
            return

        id, name, surname, phone, email, *_ = data
        self.cus_entry_name.delete(0, tk.END)
        self.cus_entry_name.insert(0, name)
        self.cus_entry_surname.delete(0, tk.END)
        self.cus_entry_surname.insert(0, surname)
        self.cus_entry_phone.delete(0, tk.END)
        self.cus_entry_phone.insert(0, phone)
        self.cus_entry_email.delete(0, tk.END)
        self.cus_entry_email.insert(0, email)
        self.appointment.customer_id = int(id)


class AddAppointmentView(SideView):
    name: str = "add"
    field_day: ttk.Entry
    field_hour: ttk.Entry
    field_minute: ttk.Entry
    field_customer: ttk.Entry

    def __init__(self, root, *args, **kwargs):
        super().__init__(root, *args, **kwargs)
        self.name = self.__class__.name
        self.set_title("Προσθήκη νέου ραντεβού")
        self.main_frame = ttk.Frame(self, borderwidth=3, relief="sunken")
        self.main_frame.pack(fill="both", expand=True)
        self.back_btn.config(command=self.sidepanel.go_back)

        self.appointment = None
        self.customer = None

        year, month, day, *_ = self.date_to_string(datetime.now())
        duration = "20"  # TODO να έρχεται από το config file

        self.date_frame = ttk.Frame(self.main_frame)
        self.date_frame.pack()

        self.app_entry_day = EntryWithPlaceholder(self.date_frame, placeholder="")
        self.app_entry_day.pack(side=tk.LEFT)
        ttk.Label(self.date_frame, text="/").pack(
            side=tk.LEFT,
        )
        self.app_entry_month = EntryWithPlaceholder(self.date_frame, placeholder="")
        self.app_entry_month.pack(side=tk.LEFT)
        ttk.Label(self.date_frame, text="/").pack(
            side=tk.LEFT,
        )
        self.app_entry_year = EntryWithPlaceholder(self.date_frame, placeholder="")
        self.app_entry_year.pack(side=tk.LEFT)

        self.hour_frame = ttk.Frame(self.main_frame)
        self.hour_frame.pack()

        self.app_entry_hour = EntryWithPlaceholder(self.hour_frame, placeholder="")
        self.app_entry_hour.pack(side=tk.LEFT)
        ttk.Label(self.hour_frame, text=":").pack(side=tk.LEFT)
        self.app_entry_minutes = EntryWithPlaceholder(self.hour_frame, placeholder="")
        self.app_entry_minutes.pack(side=tk.LEFT)

        self.app_entry_duration = EntryWithPlaceholder(
            self.main_frame, placeholder=duration
        )
        self.app_entry_duration.pack(fill="x")
        self.cus_entry_name = EntryWithPlaceholder(self.main_frame, placeholder="name")
        self.cus_entry_name.pack(fill="x")
        self.cus_entry_surname = EntryWithPlaceholder(
            self.main_frame, placeholder="surname"
        )
        self.cus_entry_surname.pack(fill="x")
        self.cus_entry_phone = EntryWithPlaceholder(
            self.main_frame, placeholder="phone number"
        )
        self.cus_entry_phone.pack(fill="x")
        self.cus_entry_email = EntryWithPlaceholder(
            self.main_frame, placeholder="email address"
        )
        self.cus_entry_email.pack(fill="x")
        self.save_button = ttk.Button(self.main_frame, text="Save", command=self.save)
        self.save_button.pack()

    def date_to_string(self, date: datetime) -> list[str]:
        datestring = date.strftime("%Y_%m_%d_%H_%M_%S")
        return datestring.split("_")

    def update_content(self, caller, caller_data):
        logger.log_info(f"Showing appointment creation panel with data {caller_data}")

        if not isinstance(caller_data, tuple):
            logger.log_warn("Wrong data")
            return

        if not isinstance(caller_data[0], datetime):
            logger.log_warn("Wrong data")
            return

        if not isinstance(caller_data[1], timedelta):
            logger.log_warn("Wrong data")
            return

        date = caller_data[0]
        duration = caller_data[1]

        year, month, day, hour, minute, *_ = self.date_to_string(date)
        self.app_entry_year.placeholder = year
        self.app_entry_month.placeholder = month
        self.app_entry_day.placeholder = day
        self.app_entry_hour.placeholder = hour
        self.app_entry_minutes.placeholder = minute
        self.app_entry_duration.placeholder = str(int(duration.total_seconds() // 60))
        self.reset()

    def save(self):
        date = datetime(
            year=int(self.app_entry_year.get()),
            month=int(self.app_entry_month.get()),
            day=int(self.app_entry_day.get()),
            hour=int(self.app_entry_hour.get()),
            minute=int(self.app_entry_minutes.get()),
            second=0,
            microsecond=0,
        )
        duration = timedelta(minutes=int(self.app_entry_duration.get()))

        appointment = Appointment(date=date, duration=duration)
        customer = Customer(
            name=self.cus_entry_name.get_without_placeholder(),
            surname=self.cus_entry_surname.get_without_placeholder(),
            phone=self.cus_entry_phone.get_without_placeholder(),
            email=self.cus_entry_email.get_without_placeholder(),
        )
        ac.create_appointment(appointment, customer)
        self.sidepanel.go_back()

    def populate_from_customer_tab(self, customer_data):
        if not isinstance(customer_data, list):
            logger.log_warn("Failed to communicate customer data")
            return

        if len(customer_data) < 5:
            logger.log_warn("Failed to communicate customer data")
            return

        self.cus_entry_name.delete(0, tk.END)
        self.cus_entry_surname.delete(0, tk.END)
        self.cus_entry_phone.delete(0, tk.END)
        self.cus_entry_email.delete(0, tk.END)

        self.cus_entry_name.insert(0, customer_data[1])
        self.cus_entry_surname.insert(0, customer_data[2])
        self.cus_entry_phone.insert(0, customer_data[3])
        self.cus_entry_email.insert(0, customer_data[4])

    def reset(self):
        for k, v in self.__dict__.items():
            if isinstance(v, EntryWithPlaceholder):
                v.delete(0, tk.END)
                v.put_placeholder()
