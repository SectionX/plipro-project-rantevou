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
cfg = get_config()
cfg["minutes_in_period"] = cfg["working_hours"] // cfg["rows"] * 60


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


class GridElement:

    def update(self):
        pass

    def move_to_the_left(self):
        pass

    def move_to_the_right(self):
        pass


class AppointmentElement:

    def update(self):
        pass


class ColumnLabel(ttk.Label, GridElement):

    def __init__(self, master, date, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.date = date
        self.update()

    def update(self):
        self["text"] = self.date.strftime("%d/%m")

    def move_to_the_left(self):
        self.date += timedelta(days=-1)
        self["text"] = self.date.strftime("%d/%m")

    def move_to_the_right(self):
        self.date += timedelta(days=1)
        self["text"] = self.date.strftime("%d/%m")


class AppointmentGroup(ttk.Frame, GridElement, AppointmentElement):

    def __init__(self, root, group_id, *args, **kwargs):
        super().__init__(root, *args, **kwargs)

        self.wname = "bgrid"
        self.root = root
        self.group_id = group_id
        self.view = SidePanelAppointmentViewer(self.top.bodyframe, self.group_id)
        self.text = tk.Label(self)
        self.text.pack(fill="both", expand=True)

        self.change_text()
        self.text.bind("<1>", self.show_in_side_panel)

    @property
    def top(self) -> Appointments:
        return get_appointment_tab(self)

    @property
    def start_date(self):
        self.top.get_date_from_group(self.group_id)

    @property
    def appointments(self):
        return Appointments.appointment_groups[self.group_id]

    @property
    def name(self):
        return f"{self.wname}-{self.group_id}"

    def change_text(self):
        self.text["text"] = f"{self.name}'\n'{len(self.appointments)}"

    def update(self, *event):
        try:
            self.change_text()
        except:
            self.text["text"] = f"{self.name}"

    def move_to_the_left(self, *args):
        self.group_id -= cfg["rows"]
        self.update()

    def move_to_the_right(self, *args):
        self.group_id -= cfg["rows"]
        self.update()

    def show_in_side_panel(self, *events):
        self.top.change_side_view(self.view)


class SidePanelElement:
    pass


class AddAppointment(ttk.Button, SidePanelElement):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class SingleAppointment(ttk.Frame, SidePanelElement, AppointmentElement):

    customer: Customer
    customer_date: str
    customer_is_alerted: str
    date: datetime
    add_button: ttk.Widget

    def __init__(self, root, appointment: Appointment | None, *args, **kwargs):
        super().__init__(root, *args, **kwargs)
        self.appointment = appointment
        if self.appointment:
            ttk.Button(self, text=str(appointment.date)).pack(side=tk.TOP, fill="x")
        else:
            ttk.Button(self, text="+").pack(side=tk.TOP, fill="x")

    def update(self):
        pass


class SidePanelViewer(ttk.Frame):
    pass


class SidePanelAppointmentViewer(SidePanelViewer):

    active_group: int
    appointment_container: ttk.Frame
    appointment_widgets: list[ttk.Widget]
    header: ttk.Label
    footer: ttk.Button

    def __init__(self, master, group_no: int, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.group_no = group_no
        self.initialize()
        self.update()

    def initialize(self):
        self.appointment_widgets = []
        self.header = ttk.Label(self, text="Ραντεβου")
        self.footer = ttk.Button(
            self, text="Back", command=lambda: self.top.change_side_view(None)
        )
        for appointment in self.appointments:
            self.appointment_widgets.append(SingleAppointment(self, appointment))
        if len(self.appointment_widgets) < 6:
            self.appointment_widgets.append(SingleAppointment(self, None))

    def update(self):
        self.header.forget()
        self.footer.forget()
        self.header.pack(side=tk.TOP, fill="x")
        for widget in self.appointment_widgets:
            widget.forget()
        for widget in self.appointment_widgets:
            widget.pack(side=tk.TOP, fill="both")
        self.footer.pack(side=tk.BOTTOM, fill="x")

    @property
    def top(self) -> Appointments:
        return get_appointment_tab(self)

    @property
    def start_date(self) -> datetime:
        return self.top.get_date_from_group(self.group_no)

    @property
    def appointments(self) -> list[Appointment]:
        return self.top.appointment_groups[self.group_no]


class AppointmentFrame(ttk.Frame, SidePanelElement):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Appointments(AppFrame):

    appointments: list[Appointment]
    cfg: dict[str, int]
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
        self.cfg["period_duration_in_hours"] = (
            self.cfg["working_hours"] // self.cfg["rows"]
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
        self.split_appointments_to_groups()

        self.side_panel = ttk.Frame(self, name="side_panel")
        self.side_panel.pack(side=tk.RIGHT, fill="y", padx=10, pady=10)
        self.button_grid = ttk.Frame(self, name="button_grid")
        self.button_grid.pack(side=tk.LEFT, fill="both", expand=True, padx=10, pady=10)
        self.navigation_bar = ttk.Frame(self.button_grid, name="navbar")
        self.navigation_bar.pack(side=tk.TOP, fill=("x"))

        self.initialize_side_panel()
        self.initialize_grid()
        self.initialize_navbar()

    ### ---------   NAVBAR    --------- ###

    def initialize_navbar(self):
        def previous_day():
            children: list[AppointmentGroup] = self.get_all_children(
                self, filter=lambda x: isinstance(x, GridElement)
            )
            for child in children:
                child.move_to_the_left()

        def next_day():
            children: list[AppointmentGroup] = self.get_all_children(
                self, filter=lambda x: isinstance(x, GridElement)
            )
            for child in children:
                child.move_to_the_right()

        previous = ttk.Button(
            self.navigation_bar, text="previous", command=previous_day
        )
        next = ttk.Button(self.navigation_bar, text="next", command=next_day)
        next.pack(side=tk.RIGHT)
        previous.pack(side=tk.RIGHT)

    ### --------- BUTTON GRID --------- ###

    def initialize_grid(self):
        for col in range(self.cfg["columns"]):
            container = ttk.Frame(self.button_grid)
            container.pack(side=tk.LEFT, fill="both", expand=True)
            label = ColumnLabel(
                container,
                date=self.start_date + td(days=col),
            )
            label.pack(fill="x")
            for row in range(self.cfg["rows"]):
                element = AppointmentGroup(container, col * cfg["rows"] + row)
                self.grid_buttons.append(element)
                element.pack(fill="both", expand=True)

    ### --------- SIDE PANEL MAIN --------- ###

    def initialize_side_panel(self):

        search_container = tk.Frame(self.side_panel, width=self.side_panel["width"])
        search_container.pack(side=tk.BOTTOM)

        self.search_button = ttk.Button(
            search_container,
            text="Εύρεση κενού χρόνου",
            name="search_button",
            command=self.find_free_appointment,
            width=search_container["width"] // 7,
        )
        self.search_button.pack(side=tk.BOTTOM, fill="x")

        entry_frame = ttk.Frame(search_container)
        entry_frame.pack(side=tk.BOTTOM, fill="x")

        self.search_entry = ttk.Entry(entry_frame)
        self.search_entry.pack(side=tk.RIGHT, fill="x")

        self.search_label = ttk.Label(entry_frame, text="Διάρκεια: ")
        self.search_label.pack(side=tk.LEFT, fill="x")

        self.bodyframe = tk.Frame(self.side_panel)
        self.bodyframe.pack(fill="both", expand=True)
        self.initial_child: SidePanelViewer = SidePanelViewer(self.bodyframe)
        self.bodyframe_child: SidePanelViewer | None = None

    def change_side_view(self, frame: SidePanelViewer | None = None):
        if frame is None:
            frame = self.initial_child
        if self.bodyframe_child:
            self.bodyframe_child.forget()
        self.bodyframe_child = frame
        self.bodyframe_child.pack(fill="both", expand=True)
        self.bodyframe_child.update()

    @property
    def time_between_appointments(self):
        return ac.get_free_periods()

    def find_free_appointment(self):
        target: timedelta | None = None
        try:
            input = int(self.search_entry.get())
            target = td(minutes=int(input))
        except:
            showerror("Error", "Η αναζήτηση πρέπει να είναι αριθμός")
            return

        for appointment, delta in self.time_between_appointments:
            if target <= delta:
                print(appointment.end_date)

    ### --------- SIDE PANEL APPOINTMENT GROUP --------- ###

    ### ---------HELPER FUNCTIONS--------- ###

    def get_appointment_from_date(self, date: datetime):
        apt_length = self.cfg["minimum_appointment_duration"]  # minutes

        day_delta = date.day - self.start_date.day
        hour_delta = date.hour - self.start_date.hour
        minute_delta = date.minute - self.start_date.minute

        # turn everything to minutes
        hour_delta = hour_delta * 60
        day_delta = day_delta * self.cfg["working_minutes"]
        total_minute_offset = minute_delta + hour_delta + day_delta

        total_appointment_offset = total_minute_offset // apt_length
        return total_appointment_offset

    def get_group_from_date(self, date: datetime):
        apt_length = self.cfg["minimum_appointment_duration"]  # minutes
        apt_per_hour = 60 // apt_length
        apt_per_group = apt_per_hour * self.cfg["working_hours"] // self.cfg["rows"]

        total_appointment_offset = self.get_appointment_from_date(date)
        total_group_offset = total_appointment_offset // apt_per_group

        return total_group_offset

    def get_date_from_group(self, group_no: int):
        rows = self.cfg["rows"]
        hours_per_row = self.cfg["working_hours"] // self.cfg["rows"]

        days = group_no // rows
        hours = (group_no % rows) * hours_per_row

        return self.start_date + timedelta(days=days, hours=hours)

    def split_appointments_to_groups(self):

        groups = ac.get_appointments_grouped_in_periods(
            start=self.start_date,
            period=td(hours=self.cfg["period_duration_in_hours"]),
        )
        flag = 0
        order = 0
        for i, group in enumerate(groups, 1):
            if flag == 0:
                self.appointment_groups[order] = list(group.appointments)
                order += 1
                if i % self.cfg["rows"] == 0:
                    flag = 1
                continue
            if flag == 1:
                if i % (24 // self.cfg["periods_per_day"]) == 0:
                    flag = 0

        while order < self.cfg["columns"] * self.cfg["rows"]:
            self.appointment_groups[order] = []
            order += 1
