from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
from datetime import timedelta
from typing import Any

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

    appointments = ac.get_appointments()
    appointment_groups = ac.get_appointments_grouped_in_periods(
        start=start_date, period=timedelta(minutes=120)
    )

    def __init__(self, root, *args, **kwargs):
        super().__init__(root, *args, **kwargs)
        SubscriberInterface.__init__(self)
        self.main_panel = Grid(self, AppointmentsTab.start_date)
        self.main_panel.pack(fill="both", expand=True)

    def subscriber_update(self):
        AppointmentsTab.appointments = ac.get_appointments()
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

        self.draw()

    @property
    def appointments(self):
        return AppointmentsTab.appointment_groups[self.group_index]

    @property
    def first_of_next_period(self):
        appointments = AppointmentsTab.appointment_groups[self.group_index + 1]
        if len(appointments) == 0:
            return Appointment(
                date=self.period_end + timedelta(minutes=0),
                duration=timedelta(minutes=0),
            )
        return appointments[0]

    @property
    def last_of_previous_period(self):
        appointments = AppointmentsTab.appointment_groups[self.group_index - 1]
        if len(appointments) == 0:
            return Appointment(date=self.period_start, duration=timedelta(0))
        return appointments[-1]

    @property
    def times_between_appointments(self) -> list[tuple[datetime, timedelta]]:
        return ac.get_time_between_appointments(
            start_date=self.period_start,
            end_date=self.period_end,
            minumum_free_period=timedelta(0),
        )

    def subscriber_update(self):
        self.draw()

    def draw(self):
        appointment_count = len(self.appointments)
        times_between = self.times_between_appointments
        times_between.sort(key=lambda x: x[1])

        minimum = cfg["minimum_appointment_duration"]

        if appointment_count <= 1:
            self.text.config(style="low.TLabel")
        elif appointment_count == 2:
            self.text.config(style="medium.TLabel")
        elif appointment_count == 3:
            self.text.config(style="high.TLabel")
        elif appointment_count > 3:
            self.text.config(style="max.TLabel")

        text = f"Ραντεβού:{appointment_count}"
        self.text.config(text=text)

    def move_left(self):
        self.period_start -= timedelta(days=1)
        self.period_end -= timedelta(days=1)
        self.group_index = ac.get_index_from_date(
            self.period_start, AppointmentsTab.start_date, self.period_duration
        )
        self.draw()

    def move_right(self):
        self.period_start += timedelta(days=1)
        self.period_end += timedelta(days=1)
        self.group_index = ac.get_index_from_date(
            self.period_start, AppointmentsTab.start_date, self.period_duration
        )
        self.draw()

    def show_in_sidepanel(self):
        appointments = []
        true_first = self.last_of_previous_period.end_date
        fake_first = self.period_start

        if fake_first > true_first:
            delta = timedelta(0)

        else:
            delta = true_first - fake_first

        first = Appointment(date=self.period_start, duration=delta)
        last = self.first_of_next_period

        temp = [first] + self.appointments + [last]

        for i, appointment in enumerate(temp):
            date = appointment.end_date
            if i == len(temp) - 1:
                break

            appointments.append(appointment)
            while date < temp[i + 1].date:
                appointments.append(
                    Appointment(
                        date=date,
                        duration=min(
                            temp[i + 1].date - date,
                            timedelta(minutes=20),
                        ),
                    )
                )
                if appointment.date > self.period_end:
                    appointments.pop()
                date += timedelta(minutes=20)
        appointments.append(last)

        SidePanel.select_view(view="appointments", caller=self, data=appointments[1:-1])
