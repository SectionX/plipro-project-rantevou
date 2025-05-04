from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror
from datetime import datetime, timedelta
from typing import Literal, Iterable

from .sidepanel import SideView, SidePanel

from ..model.entities import Appointment, Customer
from ..controller.appointments_controller import AppointmentControl
from ..controller.logging import Logger
from ..controller.mailer import Mailer
from ..controller import SubscriberInterface
from typing import Protocol

logger = Logger("alerts-view")
mailer = Mailer()


class AlertRow(ttk.Frame):
    appointment: Appointment | None
    customer: Customer | None
    show_button: ttk.Button
    email_button: ttk.Button
    name_label: ttk.Label
    time_label: ttk.Label
    cancel_id: str | None
    _state: Literal["inactive", "active", "pending"]

    def __init__(self, master: AlertsView, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.root = master
        self.sidepanel = master.sidepanel
        self.name_label = ttk.Label(self)
        self.time_label = ttk.Label(self)
        self.show_button = ttk.Button(self, text="S", command=self.show_edit, width=2)
        self.email_button = ttk.Button(self, text="@", command=self.send_email, width=2)
        self.customer = None
        self.cancel_id = None
        self._state = "inactive"

        self.email_button.pack(side=tk.RIGHT)
        self.show_button.pack(side=tk.RIGHT, fill="x")
        self.time_label.pack(side=tk.RIGHT, fill="x")
        self.name_label.pack(side=tk.LEFT, fill="x")

    def set_appointment(self, appointment: Appointment | None):
        if self.cancel_id is not None:
            self.after_cancel(self.cancel_id)

        if appointment is None:
            self.after(0, self.forget)
            self._state = "inactive"
            return

        self._state = "active"
        self.appointment = appointment
        self.customer = appointment.customer
        self.update_content()

    def update_content(self):
        if self.appointment is None:
            self.after(0, self.forget)
            self._state = "inactive"
            return

        original_date = self.appointment.date
        extended_date = self.appointment.end_date
        now = datetime.now()

        if extended_date < now:
            self.after(0, self.forget)
            self._state = "inactive"
            return

        if original_date <= extended_date < now:
            self._state = "pending"

        self.draw()
        self.cancel_id = self.after(1000, self.update_content)

    def draw(self):
        if self.appointment is None:
            return
        total_secs = self.appointment.time_to_appointment.total_seconds()
        mins, secs = total_secs // 60, total_secs % 60
        hours, mins = mins // 60, mins % 60
        time = f"{int(hours):02d}:{int(mins):02d}"

        if self.customer and self.customer.name:
            name = self.customer.name
        else:
            name = "     ---     "
        self.name_label.config(text=name)
        self.time_label.config(text=time)

    def send_email(self):
        if self.appointment:
            if self.customer and self.customer.email:
                mailer.send_email([self.appointment], debug=True)  # TODO change for live
            else:
                showerror("Customer doesn't have an email")

    def show_edit(self):
        self.sidepanel.select_view(
            "edit",
            self.root,
            self.appointment,
        )


class AlertsView(SideView, SubscriberInterface):
    name: str = "alert"
    rows: list[AlertRow]
    appointments: Iterable[Appointment]

    def __init__(self, root: SidePanel, *args, **kwargs):
        super().__init__(root, *args, **kwargs)
        SubscriberInterface.__init__(self)
        self.name = self.__class__.name
        self.set_title("Ειδοποιήσεις")
        self.appointments = []
        self.rows = []
        self.back_btn.destroy()

    def update_content(self, *args, **kwargs):
        self.appointments = list(
            AppointmentControl().get_appointments_from_to_date(
                start=datetime.now(), end=datetime.now() + timedelta(days=1)
            )
        )

        rows_count = len(self.rows)
        i = 0
        for i, appointment in enumerate(self.appointments):
            if i < rows_count:
                self.rows[i].set_appointment(appointment)
            else:
                self.rows.append(AlertRow(self))
                self.rows[i].set_appointment(appointment)
                self.rows[i].pack(fill="x", pady=1, padx=1)

        while len(self.rows) > len(self.appointments):
            self.rows.pop().destroy()

    def subscriber_update(self):
        self.update_content()

    def show_in_sidepanel(self):
        self.sidepanel.select_view("alerts", self)
