from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
from datetime import timedelta
from typing import Any
from itertools import chain
from collections import deque

from .abstract_views import AppFrame
from .sidepanel import SidePanel

from ..controller.appointments_controller import AppointmentControl
from ..controller.customers_controller import CustomerControl
from ..controller.logging import Logger
from ..controller import get_config

from ..model.types import Appointment

logger = Logger("AppointmentsTab")
ac = AppointmentControl()
cc = CustomerControl()
cfg: dict[str, Any] = get_config()["view_settings"]
cfg["group_period"] = timedelta(hours=cfg["working_hours"] // cfg["rows"])
cfgb = get_config()["buttons"]


class SubscriberInterface:
    def __init__(self):
        ac.add_subscription(self)
        cc.add_subscription(self)

    def subscriber_update(self):
        raise NotImplementedError


class AppointmentsTab(AppFrame, SubscriberInterface):

    appointments: list[Appointment]
    appointment_groups: dict[int, list[Appointment]]
    start_date: datetime
    group_period: timedelta
    end_date: datetime

    mail_panel: Grid

    # Shared data
    start_date = datetime.now().replace(
        hour=cfg["opening_hour"],
        minute=0,
        second=0,
        microsecond=0,
    )

    end_date = start_date + timedelta(
        days=cfg["columns"],
        hours=cfg["working_hours"],
    )

    group_period = cfg["group_period"]

    appointment_groups = ac.get_appointments_grouped_in_periods(
        start=start_date, period=timedelta(minutes=120)
    )

    def __init__(self, root, *args, **kwargs):
        super().__init__(root, *args, **kwargs)
        SubscriberInterface.__init__(self)
        self.main_panel = Grid(self, AppointmentsTab.start_date)
        self.main_panel.pack(fill="both", expand=True)

    def subscriber_update(self):
        AppointmentsTab.appointment_groups = ac.get_appointments_grouped_in_periods(
            AppointmentsTab.start_date, AppointmentsTab.group_period
        )


class GridNavBar(ttk.Frame):
    move_left: ttk.Button
    move_right: ttk.Button

    def __init__(self, root: Grid, *args, **kwargs):
        super().__init__(root, *args, **kwargs)
        self.move_left = ttk.Button(
            self, text="Previous", command=root.move_left, style="low.TButton"
        )
        self.move_right = ttk.Button(
            self, text="Next", command=root.move_right, style="low.TButton"
        )
        self.move_right.pack(side=tk.RIGHT)
        self.move_left.pack(side=tk.RIGHT)


class Grid(ttk.Frame):
    columns: list[GridColumn]
    navbar: GridNavBar
    start_date: datetime

    def __init__(self, root, start_date, *args, **kwargs):
        super().__init__(root, *args, **kwargs)
        self.start_date = start_date
        self.period_duration = timedelta(hours=2)
        self.columns = []

        self.navbar = GridNavBar(self, *args, **kwargs)
        self.navbar.pack(fill="x")

        self.rowheader = GridVerticalHeader(
            self, start_date, self.period_duration, cfg["rows"]
        )
        self.rowheader.pack(side=tk.LEFT, fill="both")

        for i in range(7):
            start_date = self.start_date + timedelta(days=i)
            end_date = start_date + timedelta(hours=8)
            start_index = ac.get_index_from_date(
                start_date, self.start_date, self.period_duration
            )
            self.columns.append(
                GridColumn(
                    self,
                    start_date=start_date,
                    end_date=end_date,
                    start_index=start_index,
                    period_duration=self.period_duration,
                )
            )
            self.columns[i].pack(side=tk.LEFT, fill="both", expand=True, pady=10)

    def move_left(self):
        for column in self.columns:
            column.move_left()

    def move_right(self):
        for column in self.columns:
            column.move_right()


class GridHeader(ttk.Label):
    date: datetime

    def __init__(self, root, date: datetime, *args, **kwargs):
        super().__init__(root, *args, **kwargs)
        self.date = date
        self.draw()

    def draw(self):
        self.config(text=self.date.strftime("%d/%m"))

    def move_left(self):
        self.date -= timedelta(days=1)
        self.draw()

    def move_right(self):
        self.date += timedelta(days=1)
        self.draw()


class GridVerticalHeader(ttk.Label):
    start: datetime
    interval: timedelta
    rows: int

    def __init__(
        self, master, start: datetime, interval: timedelta, rows: int, *args, **kwargs
    ):
        super().__init__(master, *args, **kwargs)
        self.start = start
        self.interval = interval
        self.rows = rows
        for i in range(rows):
            from_time = (self.start + interval * i).strftime("%H:%M")
            to_time = (self.start + interval * (i + 1)).strftime("%H:%M")
            text = f"{from_time}-{to_time}"
            ttk.Label(self, text=text).pack(fill="both", expand=True)


class GridColumn(ttk.Frame):
    header: GridHeader
    rows: list[GridCell]
    start_date: datetime
    end_date: datetime
    period_duration: timedelta

    def __init__(
        self,
        root,
        start_date,
        end_date,
        start_index,
        period_duration,
        *args,
        **kwargs,
    ):
        super().__init__(root, *args, **kwargs)
        self.start_date = start_date
        self.end_date = end_date
        self.period_duration = period_duration
        self.start_index = start_index
        self.header = GridHeader(self, start_date)
        self.rows = []

        start = start_date
        i = 0
        while start < end_date:
            self.rows.append(GridCell(self, start_index + i, start, period_duration))
            i += 1
            start += period_duration

        self.header.pack(fill="x")
        for row in self.rows:
            row.pack(fill="both", expand=True, padx=3, pady=3)

    def move_left(self):
        self.header.move_left()
        for row in self.rows:
            row.move_left()

    def move_right(self):
        self.header.move_right()
        for row in self.rows:
            row.move_right()


class GridCell(ttk.Frame, SubscriberInterface):
    group_index: int
    period_start: datetime
    period_duration: timedelta
    current_focus = None

    def __init__(
        self,
        root,
        appointment_group_index: int,
        period_start: datetime,
        period_duration: timedelta,
        *args,
        **kwargs,
    ):
        super().__init__(root, *args, **kwargs)
        SubscriberInterface.__init__(self)

        self.group_index = appointment_group_index
        self.period_start = period_start
        self.period_duration = period_duration
        self.period_end = period_start + period_duration

        self.text = ttk.Label(self)
        self.text.pack(fill="both", expand=True, padx=3, pady=3)
        self.text.bind("<Button-1>", lambda x: self.show_in_sidepanel())
        self.config(borderwidth=1)

        self.cache: None | list = None
        self.draw()

    @property
    def appointments(self):
        AppointmentsTab.appointment_groups[self.group_index].sort(key=lambda x: x.date)
        return AppointmentsTab.appointment_groups[self.group_index]

    @property
    def times_between_appointments(self) -> list[tuple[datetime, timedelta]]:
        return ac.get_time_between_appointments(
            start_date=self.period_start,
            end_date=self.period_end,
            minumum_free_period=timedelta(0),
        )

    @property
    def previous_period_appointments(self):
        AppointmentsTab.appointment_groups[self.group_index - 1].sort(
            key=lambda x: x.date
        )
        return AppointmentsTab.appointment_groups[self.group_index - 1]

    @property
    def next_period_appointments(self):
        AppointmentsTab.appointment_groups[self.group_index + 1].sort(
            key=lambda x: x.date
        )
        return AppointmentsTab.appointment_groups[self.group_index + 1]

    def subscriber_update(self):
        self.draw()
        self.cache = None

    def draw(self):
        appointment_count = len(self.appointments)

        if appointment_count <= 1:
            self.style = "low.TLabel"
        elif appointment_count == 2:
            self.style = "medium.TLabel"
        elif appointment_count == 3:
            self.style = "high.TLabel"
        elif appointment_count > 3:
            self.style = "max.TLabel"
        self.text.config(style=self.style)

        text = f"Ραντεβού:{appointment_count}"
        self.text.config(text=text)

    def move_left(self):
        self.period_start -= timedelta(days=1)
        self.period_end -= timedelta(days=1)
        self.group_index = ac.get_index_from_date(
            self.period_start, AppointmentsTab.start_date, self.period_duration
        )
        self.cache = None
        self.draw()

    def move_right(self):
        self.period_start += timedelta(days=1)
        self.period_end += timedelta(days=1)
        self.group_index = ac.get_index_from_date(
            self.period_start, AppointmentsTab.start_date, self.period_duration
        )
        self.draw()
        self.cache = None

    def unfocus(self):
        self.config(relief="flat")

    def show_focus(self):
        self.config(relief="raised")
        if GridCell.current_focus:
            GridCell.current_focus.unfocus()
        GridCell.current_focus = self

    def show_in_sidepanel(self):
        self.show_focus()
        sidepanel = self.nametowidget(".!sidepanel")

        if self.cache:
            logger.log_debug(f"{self.winfo_name()} showing cached version")
            return sidepanel.select_view("appointments", self, self.cache)

        min_duration = timedelta(minutes=cfg["minimum_appointment_duration"])

        if len(self.appointments) == 0:
            return sidepanel.select_view(
                "appointments",
                self,
                [
                    Appointment(
                        date=self.period_start + i * min_duration,
                        duration=min_duration,
                    )
                    for i in range(self.period_duration // min_duration)
                ],
            )

        previous_appointments = self.previous_period_appointments
        next_appointments = self.next_period_appointments
        if len(previous_appointments) == 0:
            previous_appointments = [
                Appointment(date=self.period_start, duration=timedelta(0))
            ]

        if len(next_appointments) == 0:
            next_appointments = [
                Appointment(date=self.period_end, duration=timedelta(0))
            ]

        appointments: deque[Appointment] = deque(
            chain(
                previous_appointments,
                self.appointments,
                next_appointments,
            )
        )
        slots: list[Appointment] = []
        is_eligible = lambda a, b: a < self.period_end and b > self.period_start

        while len(appointments) > 1:
            previous = appointments.popleft()
            next = appointments[0]

            if is_eligible(previous.date, previous.end_date):
                slots.append(previous)

            diff = previous.time_between_appointments(next)
            full_appointments = diff // min_duration
            remainer = diff % min_duration

            for i in range(full_appointments):
                date = previous.end_date + min_duration * i
                duration = min_duration
                end_date = date + duration

                if is_eligible(date, end_date):
                    slots.append(
                        Appointment(
                            date=date,
                            duration=duration,
                        )
                    )

            if remainer > timedelta(0):
                date = next.date - remainer
                duration = remainer
                end_date = next.date

                if is_eligible(date, end_date):
                    slots.append(
                        Appointment(
                            date=date,
                            duration=duration,
                        )
                    )

        if appointments:
            last = appointments.pop()
            if is_eligible(last.date, last.end_date):
                slots.append(last)

        self.cache = slots
        sidepanel.select_view("appointments", self, slots)
