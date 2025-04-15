from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror
from datetime import datetime, timedelta
from typing import Literal

from .sidepanel import SidePanel
from .abstract_views import EntryWithPlaceholder
from . import abstract_views

from ..model.types import Appointment, Customer
from ..controller.appointments_controller import AppointmentControl
from ..controller.logging import Logger
from ..controller.mailer import Mailer

#
ac = AppointmentControl()
logger = Logger("appointment-view")
mailer = Mailer()


class AppointmentViewButton(ttk.Button):
    appointment: Appointment | None

    def __init__(
        self,
        master,
        duration: timedelta,
        expiration_date: datetime,
        *args,
        appointment: Appointment | None = None,
        **kwargs,
    ):
        super().__init__(master, *args, **kwargs)
        self.sidepanel = master.master.sidepanel
        self.appointment = appointment
        self.duration = duration
        self.expiration_date = expiration_date

        if self.appointment:
            text = f"{self.appointment.date.strftime('%H:%M')}-{self.appointment.end_date.strftime('%H:%M')}"
            self.config(text=text, style="edit.TButton", command=self.edit_appointment)
        else:
            self.config(style="add.TButton")
            self.create_add_button()

    def create_add_button(self):
        time_to_expire = self.expiration_date - datetime.now()
        if time_to_expire < timedelta(0):
            time_to_expire = timedelta(0)

        if self.expiration_date < datetime.now():
            self.after(int(time_to_expire.total_seconds() * 1000), self.forget)
            return

        if self.duration == timedelta(0):
            self.after(0, self.forget)
            return

        start = (self.expiration_date - self.duration).strftime("%H:%M")
        minutes = f"{int(self.duration.total_seconds() // 60)} λεπτά"

        self.config(
            text=f"{start}: {minutes}",
            command=self.add_appointment,
        )

    def add_appointment(self):
        self.sidepanel.select_view(
            "add",
            caller=self.master,
            data=(self.expiration_date - self.duration, self.duration),
        )

    def edit_appointment(self):
        self.sidepanel.select_view("edit", caller=self.master, data=self.appointment)


class AppointmentView(abstract_views.SideView):
    name: str = "appointments"
    add_button: ttk.Button
    edit_button: ttk.Button
    caller_data: list[Appointment]

    def __init__(self, master: SidePanel, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.name = self.__class__.name
        self.sidepanel = master
        self.main_frame = ttk.Frame(
            self, style="primary.TFrame", borderwidth=3, relief="sunken"
        )
        self.set_title("Ραντεβού")
        self.main_frame.pack(fill="both", expand=True)
        self.back_btn.config(command=master.go_back)

    def update_content(self, caller, caller_data):
        for button in tuple(self.main_frame.children.values()):
            button.destroy()

        if not (
            isinstance(caller_data, list) and isinstance(caller_data[0], Appointment)
        ):
            logger.log_warn("Wrong data")
            return

        appointment: Appointment
        for appointment in caller_data:
            if appointment.id is not None:
                AppointmentViewButton(
                    self.main_frame,
                    duration=appointment.duration,
                    expiration_date=appointment.end_date,
                    appointment=appointment,
                ).pack(fill="x")
                continue

            AppointmentViewButton(
                self.main_frame,
                duration=appointment.duration,
                expiration_date=appointment.end_date,
                appointment=None,
            ).pack(fill="x")
