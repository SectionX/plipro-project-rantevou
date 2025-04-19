from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror
from datetime import datetime, timedelta

from .sidepanel import SidePanel
from .entries import AppointmentEntry, CustomerEntry
from .abstract_views import SideView, EntryWithPlaceholder
from ..model.types import Appointment, Customer
from ..controller.appointments_controller import AppointmentControl
from ..controller.logging import Logger
from ..controller.mailer import Mailer
from ..controller.exceptions import *

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

        self.appointment_entry = AppointmentEntry(self.main_frame)
        self.appointment_entry.pack(fill="x")

        self.customer_entry = CustomerEntry(self.main_frame)
        self.customer_entry.pack(fill="x")

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
            raise ViewWrongDataError(caller_data)

        if not isinstance(caller_data, Appointment):
            raise ViewWrongDataError(caller_data)

        self.appointment = caller_data
        self.customer = caller_data.customer

        logger.log_info(f"Showing data {self.customer} for editing")

        self.appointment_entry.populate(self.appointment)
        self.customer_entry.populate(self.customer)

    def delete(self):
        self.appointment = self.appointment_entry.get()
        result = AppointmentControl().delete_appointment(self.appointment)
        if result is True:
            self.sidepanel.go_back()
        else:
            showerror(message="Failed to delete Appointment")

    def save(self):
        self.appointment = self.appointment_entry.get()
        self.customer = self.customer_entry.get()
        result = AppointmentControl().update_appointment(
            self.appointment, self.customer
        )
        if result is True:
            self.sidepanel.go_back()
        else:
            showerror(message="Failed to update Appointment")

    def reset(self):
        for k, v in self.__dict__.items():
            if isinstance(v, ttk.Entry):
                v.delete(0, tk.END)

    def populate_from_customer_tab(self, customer_data: Customer | list):
        if not (isinstance(customer_data, list) or isinstance(customer_data, Customer)):
            raise ViewWrongDataError(customer_data)

        self.customer_entry.populate(customer_data)


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

        self.appointment_entry = AppointmentEntry(self.main_frame)
        self.customer_entry = CustomerEntry(self.main_frame)

        self.appointment_entry.pack(fill="x")
        self.customer_entry.pack(fill="x")

        self.save_button = ttk.Button(self.main_frame, text="Add", command=self.save)
        self.save_button.pack()

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

        self.appointment_entry.populate(
            Appointment(
                date=caller_data[0],
                duration=caller_data[1],
            )
        )
        self.customer_entry.populate(None)

    def save(self):
        appointment = self.appointment_entry.get()
        customer = self.customer_entry.get()

        AppointmentControl().create_appointment(appointment, customer)
        self.sidepanel.go_back()

    def populate_from_customer_tab(self, customer_data):
        if not isinstance(customer_data, list):
            logger.log_warn("Failed to communicate customer data")
            return

        if len(customer_data) < 5:
            logger.log_warn("Failed to communicate customer data")
            return

        self.customer_entry.populate(customer_data)

    def reset(self):
        for k, v in self.__dict__.items():
            if isinstance(v, EntryWithPlaceholder):
                v.delete(0, tk.END)
                v.put_placeholder()
