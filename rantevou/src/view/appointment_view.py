from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror
from datetime import datetime, timedelta
from typing import Literal

from .sidepanel import SidePanel
from .abstract_views import EntryWithPlaceholder
from . import abstract_views

from ..model.entities import Appointment, Customer
from ..controller.appointments_controller import AppointmentControl
from ..controller.logging import Logger
from ..controller.mailer import Mailer
from ..controller.exceptions import *

#
logger = Logger("appointment-view")
mailer = Mailer()


class AppointmentViewButton(ttk.Button):
    appointment: Appointment

    def __init__(
        self,
        master,
        *args,
        **kwargs,
    ):
        super().__init__(master, *args, **kwargs)
        self.sidepanel: SidePanel = master.master.sidepanel

    def set(self, appointment: Appointment):
        self.appointment = appointment
        if appointment.id:
            text = f"{appointment.date.strftime('%H:%M')}-{appointment.end_date.strftime('%H:%M')}"
            self.config(text=text, style="edit.TButton", command=self.edit_appointment)
        else:
            self.config(style="add.TButton")
            self.create_add_button()

    def create_add_button(self):
        date = self.appointment.date
        duration = self.appointment.duration
        end_date = self.appointment.end_date

        time_to_expire = end_date - datetime.now()
        if time_to_expire < timedelta(0):
            time_to_expire = timedelta(0)

        if end_date < datetime.now():
            self.after(0, self.destroy)
            return

        if duration == timedelta(0):
            self.after(0, self.destroy)
            return

        start = date.strftime("%H:%M")
        minutes = f"{int(duration.total_seconds() // 60)} λεπτά"

        self.config(
            text=f"{start}: {minutes}",
            command=self.add_appointment,
        )

    def add_appointment(self):
        self.sidepanel.select_view(
            "add",
            caller=self,
            caller_data=(self.appointment.date, self.appointment.duration),
        )

    def edit_appointment(self):
        self.sidepanel.select_view("edit", caller=self, caller_data=self.appointment)


class AppointmentView(abstract_views.SideView):
    name: str = "appointments"
    add_button: ttk.Button
    edit_button: ttk.Button
    caller_data: list[Appointment]

    def __init__(self, master: SidePanel, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.name = self.__class__.name
        self.sidepanel = master
        self.main_frame = ttk.Frame(self, style="primary.TFrame", borderwidth=3, relief="sunken")
        self.set_title("Ραντεβού")
        self.main_frame.pack(fill="both", expand=True)
        self.back_btn.config(command=master.go_back)

    def update_content(self, caller, caller_data):
        if not isinstance(caller_data, list):
            raise ViewWrongDataError(caller_data)

        if len(caller_data) == 0:
            return

        if not isinstance(caller_data[0], Appointment):
            raise ViewWrongDataError(caller_data[0])

        buttons: list[AppointmentViewButton] = []
        for widget in self.main_frame.children.values():
            if isinstance(widget, AppointmentViewButton):
                buttons.append(widget)

        app_len = len(caller_data)
        but_len = len(buttons)
        diff = app_len - but_len

        if diff > 0:
            for i in range(diff):
                AppointmentViewButton(self.main_frame).pack(fill="x")
        else:
            for _ in range(-diff):
                buttons.pop().destroy()

        buttons.clear()
        for widget in self.main_frame.children.values():
            if isinstance(widget, AppointmentViewButton):
                buttons.append(widget)

        for button, appointment in zip(buttons, caller_data, strict=True):
            button.set(appointment)
