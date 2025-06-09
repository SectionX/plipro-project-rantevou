from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror
from datetime import datetime, timedelta
from typing import Any

from .sidepanel import SidePanel
from .forms import AppointmentForm, CustomerForm
from .abstract_views import SideView, EntryWithPlaceholder
from .exceptions import *
from ..model.entities import Appointment, Customer
from ..controller.appointments_controller import AppointmentControl
from ..controller.logging import Logger
from ..controller.mailer import Mailer

logger = Logger("appointment-manager")
mailer = Mailer()


class EditAppointmentView(SideView):
    """
    View που εμφανίζει την φόρμα επεξεργασίας ραντεβού
    """

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

        self.appointment_entry = AppointmentForm(self.main_frame)
        self.appointment_entry.pack(fill="x")

        self.customer_entry = CustomerForm(self.main_frame)
        self.customer_entry.pack(fill="x")

        self.save_button = ttk.Button(self.main_frame, text="Save", command=self.save)
        self.save_button.pack()
        self.delete_button = ttk.Button(self.main_frame, text="Delete", command=self.delete)
        self.delete_button.pack()

    def update_content(self, caller, caller_data: Appointment | Any | None):
        self.reset()
        appointment = caller_data

        logger.log_info(f"Showing data {appointment} for editing")

        if appointment is None:
            raise ViewWrongDataError(self, caller, appointment)

        if not isinstance(appointment, Appointment):
            raise ViewWrongDataError(self, caller, appointment)

        self.appointment = appointment
        self.appointment_entry.populate(self.appointment)

        self.customer = appointment.customer
        self.customer_entry.populate(self.customer)

        logger.log_info(f"Showing data {self.customer} for editing")

    def delete(self):
        self.appointment = self.appointment_entry.get()
        result, reason = AppointmentControl().delete_appointment(self.appointment)
        if result is True:
            self.sidepanel.go_back()
        else:
            showerror(message=reason)

    def save(self):
        self.appointment = self.appointment_entry.get()
        self.customer = self.customer_entry.get()
        if self.customer.name is None:
            self.customer = None

        result = AppointmentControl().update_appointment(self.appointment, self.customer)
        if result is True:
            self.sidepanel.go_back()
        else:
            showerror(message="Failed to update Appointment")

    def reset(self):
        for k, v in self.__dict__.items():
            if isinstance(v, ttk.Entry):
                v.delete(0, tk.END)

    def populate_from_customer_tab(self, customer_data: Customer):
        if not (isinstance(customer_data, list) or isinstance(customer_data, Customer)):
            raise ViewWrongDataError(customer_data)

        self.customer_entry.populate(customer_data)


class AddAppointmentView(SideView):
    "View που εμφανίζει την φόρμα δημιουργίας νέου ραντεβού"

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

        self.appointment_entry = AppointmentForm(self.main_frame)
        self.customer_entry = CustomerForm(self.main_frame)

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
        if not isinstance(customer_data, Customer):
            logger.log_warn("Failed to communicate customer data")
            return

        self.customer_entry.populate(customer_data)
