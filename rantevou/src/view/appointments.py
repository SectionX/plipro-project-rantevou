from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror
from datetime import datetime, timedelta
from datetime import timedelta as td
from typing import Any
from .abstract_views import AppFrame
from ..controller.appointments_controller import AppointmentControl as AC
from ..controller.customers_controller import CustomerControl as CC
from ..controller.logging import Logger
from ..controller.mailer import Mailer
from ..controller import get_config
from ..model.types import Customer, Appointment

logger = Logger("Appointments")
ac = AC()
cc = CC()
mailer = Mailer()
module_state: dict[str, Any] = {}
cfg: dict[str, Any] = get_config()
cfg["minutes_in_period"] = cfg["working_hours"] // cfg["rows"] * 60


def add_subscription(node):
    ac.add_subscription(node)


def call_update():
    ac.update_subscribers()


def fetch_customers():
    return cc.get_customers()


def fetch_customer_by_property(**kwargs):
    return cc.get_customer_by_properties(**kwargs)


def add_appointment(**kwargs) -> bool:
    try:
        ac.create_appointment(Appointment(**kwargs))
        return True
    except Exception as e:
        logger.log_warn(str(e))
        return False


def update_appointment(**kwargs) -> bool:
    try:
        ac.update_appointment(Appointment(**kwargs))
        return True
    except Exception as e:
        logger.log_warn(str(e))
        return False


def delete_appointment(**kwargs) -> bool:
    try:
        ac.delete_appointment(**kwargs)
        return True
    except Exception as e:
        logger.log_warn(str(e))
        return False


def add_customer(**kwargs) -> bool:
    try:
        cc.create_customer(Customer(**kwargs))
        return True
    except Exception as e:
        logger.log_warn(str(e))
        return False


def fetch_appointments():
    appointments = ac.get_appointments()
    appointments.sort(key=lambda x: x.date)
    return appointments


def fetch_appointmets_by_id(id):
    return ac.get_appointment_by_id(id)


def send_mail(*appointments):
    mailer.send_email(*appointments)


def dict_to_customer(dict):
    return Customer(**dict)


def dict_to_appointment(dict):
    return Appointment(**dict)


def get_appointment_tab(node):
    return node.nametowidget(".!notebook.!appointments")


class Appointments(AppFrame):

    appointments: list[Appointment]
    cfg: dict[str, Any]
    start_date: datetime
    end_date: datetime
    time_format: str = "%H:%M"
    appointment_groups: dict[int, list[Appointment]] = {}
    appointment_group_index: int = 0
    grid_buttons: list[ttk.Widget] = []
    button_grid: ttk.Frame
    side_panel: ttk.Frame

    def __init__(self, root, *args, name="appointments", **kwargs):
        super().__init__(root, *args, **kwargs)
        self.name = name
        self.appointments = fetch_appointments()

        self.cfg = cfg
        self.cfg["working_minutes"] = self.cfg["working_hours"] * 60
        self.cfg["periods_per_day"] = self.cfg["working_hours"] // self.cfg["rows"]
        self.cfg["period_duration_in_hours"] = timedelta(
            hours=self.cfg["working_hours"] // self.cfg["rows"]
        )

        self.max_button_count = int(
            self.cfg["columns"]
            * self.cfg["working_hours"]
            // self.cfg["minimum_appointment_duration"]
        )

        self.start_date = datetime.now().replace(
            hour=self.cfg["opening_hour"],
            minute=0,
            second=0,
            microsecond=0,
        )

        self.end_date = self.start_date + timedelta(
            days=self.cfg["columns"],
            hours=self.cfg["working_hours"],
        )

        self.group_period = timedelta(
            hours=self.cfg["working_hours"] // self.cfg["rows"]
        )
        self.appointment_groups = ac.get_appointments_grouped_in_periods(
            start=self.start_date, period=self.cfg["period_duration_in_hours"]
        )

        self.side_panel = ttk.Frame(self, name="side_panel", style="primary.TFrame")
        self.side_panel.pack(side=tk.RIGHT, fill="y", padx=10, pady=10)

        self.grid = ttk.Frame(self, name="button_grid")
        self.grid.pack(side=tk.LEFT, fill="both", expand=True, padx=10, pady=10)

        self.navigation_bar = ttk.Frame(self.grid, name="navbar")
        self.navigation_bar.pack(side=tk.TOP, fill=("x"))


###

data_pipeline: dict[str, Any] = {}


class SubscriberInterface:
    def __init__(self):
        add_subscription(self)

    def update(self):
        raise NotImplementedError


class GridNavBar(ttk.Frame):
    move_left: ttk.Button
    move_right: ttk.Button

    def __init__(self, root: Grid, *args, **kwargs):
        super().__init__(root, *args, **kwargs)
        self.move_left = ttk.Button(self, text="Previous", command=root.move_left)
        self.move_right = ttk.Button(self, text="Next", command=root.move_right)


class Grid(ttk.Frame):
    columns: list[GridColumn]
    navbar: GridNavBar
    start_date: datetime

    def __init__(self, root, start_date, *args, **kwargs):
        self.start_date = start_date
        self.period_duration = timedelta(hours=2)
        self.columns = []

        self.navbar = GridNavBar(root, *args, **kwargs)
        self.navbar.pack(fill="x")

        for i in range(7):
            start_date = self.start_date + timedelta(days=i)
            end_date = start_date + timedelta(days=i, hours=8)
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

    def draw(self):
        self.config(text=self.date.strftime("%d/%m"))

    def move_left(self):
        self.date -= timedelta(days=1)
        self.draw()

    def move_right(self):
        self.date += timedelta(days=1)
        self.draw()


class GridColumn(ttk.Frame):
    header: GridHeader
    rows: list[GridGroup]
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
            self.rows.append(GridGroup(self, start_index + i, start, period_duration))
            i += 1
            start += period_duration

        self.draw()

    def draw(self):
        self.header.pack(fill="x")
        for row in self.rows:
            row.pack(fill="both", expand=True)

    def move_left(self):
        self.header.move_left()
        for row in self.rows:
            row.move_left()

    def move_right(self):
        self.header.move_right()
        for row in self.rows:
            row.move_right()


class GridGroup(ttk.Frame, SubscriberInterface):
    edit_buttons: list[AppointmentEditButton]
    add_button: AppointmentAddButton
    group_index: int
    period_start: datetime
    period_duration: timedelta
    top: Appointments

    def __init__(
        self,
        root,
        appointment_group_index: int,
        period_start: datetime,
        period_duration: timedelta,
        *args,
        **kwargs,
    ):
        SubscriberInterface.__init__(self)
        ttk.Frame.__init__(self, root, *args, **kwargs)
        self.group_index = appointment_group_index
        self.period_start = period_start
        self.period_duration = period_duration
        self.period_end = period_start + period_duration
        self.text = ttk.Label(self)
        self.text.pack(fill="both", expand=True)

        self.top = get_appointment_tab(self)
        self.update()

    @property
    def appointments(self):
        return self.top.appointment_groups[self.group_index]

    def update(self):
        self.draw()

    def draw(self):
        start = self.period_start.strftime("%H:%M")
        end = self.period_end.strftime("%H:%M")
        self.text.config(
            text=(f"{start}-{end}\n" f"Appointments: {len(self.appointments)}")
        )

    def move_left(self):
        self.period_start -= timedelta(days=1)
        self.period_end -= timedelta(days=1)
        self.group_index -= 4
        self.draw()

    def move_right(self):
        self.period_start += timedelta(days=1)
        self.period_end += timedelta(days=1)
        self.group_index += 4
        self.draw()


class SidePanel(ttk.Frame):
    side_views: dict[str, SideView]
    search_bar: SearchBar
    active_view: SideView

    def __init__(self, root, *args, **kwargs):
        super().__init__(root, *args, **kwargs)
        self.panel_views = {
            "alert": AlertsView(self),
            "appointment": AppointmentView(self),
            "search": SearchResultsView(self),
            "edit": EditAppointmentView(self),
            "add": AddAppointmentView(self),
        }
        self.active_view = self.side_views["alert"]
        self.search_bar = SearchBar(self)
        self.search_bar.pack(side=tk.BOTTOM, fill="x")
        self.select_view()

    def select_view(self, view: str | None = None):
        self.active_view.forget()
        if view is None:
            view = "alert"
        self.active_view = self.panel_views[view]
        self.active_view.pack(side=tk.TOP, fill="both", expand=True)
        self.active_view.update_contents()


class SidePanelHeader(ttk.Label):
    panel_name: str


class SideView(ttk.Frame):
    name: str = ""
    data: Any

    def update_contents(self):
        self.data = data_pipeline[self.name]
        ...
        raise NotImplementedError


class AppointmentView(SideView):
    name: str = "appointment"


class AlertsView(SideView):
    name: str = "alert"


class SearchResultsView(SideView):
    name: str = "search"


class EditAppointmentView(SideView):
    name: str = "edit"


class AddAppointmentView(SideView):
    name: str = "add"


class SearchBar(ttk.Frame):
    label: ttk.Label
    entry: ttk.Entry
    button: ttk.Button
    duration: timedelta
    affects: SearchResultsView
    search_results: list[tuple[datetime, timedelta]]

    def search(self):
        self.duration = timedelta(minutes=int(self.entry.get()))
        self.search_results = ac.get_time_between_appointments(
            start_date=datetime.now(), minumum_free_period=self.duration
        )


class AppointmentButton(ttk.Button, SubscriberInterface):
    pass


class AppointmentAddButton(AppointmentButton):
    cancel: bool

    def __init__(self, root, *args, **kwargs):
        super().__init__(root, *args, **kwargs)
        self.config(text="+")
        self.cancel = False

    def add_appointment(self):
        ...
        if self.cancel:
            self.cancel = False
            return
        raise NotImplementedError


class AppointmentEditButton(AppointmentButton):
    cancel: bool

    def edit_appointment(self):
        ...
        if self.cancel:
            self.cancel = False
            return
        raise NotImplementedError
