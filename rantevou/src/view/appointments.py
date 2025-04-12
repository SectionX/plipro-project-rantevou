from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror
from datetime import datetime, timedelta, time
from datetime import timedelta as td
from typing import Any, Literal
from .abstract_views import AppFrame
from ..controller.appointments_controller import AppointmentControl as AC
from ..controller.customers_controller import CustomerControl as CC
from ..controller.logging import Logger
from ..controller.mailer import Mailer
from ..controller import get_config
from ..model.types import Customer, Appointment

logger = Logger("AppointmentsTab")
ac = AC()
cc = CC()
mailer = Mailer()
module_state: dict[str, Any] = {}
cfg: dict[str, Any] = (
    get_config()
)  # working_hours, opening_hour, rows, columns, minimum appointment duration
cfg["group_period"] = timedelta(hours=cfg["working_hours"] // cfg["rows"])


def add_subscription(node):
    ac.add_subscription(node)


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


def send_mail(appointments):
    mailer.send_email(appointments, debug=True)  # TODO change to live


def dict_to_customer(dict):
    return Customer(**dict)


def dict_to_appointment(dict):
    return Appointment(**dict)


class SubscriberInterface:
    def __init__(self):
        add_subscription(self)

    def subscriber_update(self):
        raise NotImplementedError


class AppointmentsTab(AppFrame, SubscriberInterface):

    appointments: list[Appointment]
    appointment_groups: dict[int, list[Appointment]]
    start_date: datetime
    group_period: timedelta
    end_date: datetime

    mail_panel: Grid
    side_panel: SidePanel

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
        self.mail_panel = Grid(self, AppointmentsTab.start_date)
        self.side_panel = SidePanel(self, style="primary.TFrame", width=400)

        self.mail_panel.pack(side=tk.LEFT, fill="both", expand=True, padx=10, pady=10)
        self.side_panel.pack(
            side=tk.RIGHT,
            fill="both",
            expand=True,
            padx=10,
            pady=10,
        )

    def subscriber_update(self):
        AppointmentsTab.appointments = fetch_appointments()
        print(*AppointmentsTab.appointments, sep="\n")
        AppointmentsTab.appointment_groups = ac.get_appointments_grouped_in_periods(
            AppointmentsTab.start_date, AppointmentsTab.group_period
        )


###

data_pipeline: dict[str, Any] = {}


class GridNavBar(ttk.Frame):
    move_left: ttk.Button
    move_right: ttk.Button

    def __init__(self, root: Grid, *args, **kwargs):
        super().__init__(root, *args, **kwargs)
        self.move_left = ttk.Button(self, text="Previous", command=root.move_left)
        self.move_right = ttk.Button(self, text="Next", command=root.move_right)
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
    rows: list[GridRow]
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
            self.rows.append(GridRow(self, start_index + i, start, period_duration))
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


class GridRow(ttk.Frame, SubscriberInterface):
    edit_buttons: list[AppointmentEditButton]
    add_button: AppointmentAddButton
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
        SubscriberInterface.__init__(self)
        ttk.Frame.__init__(self, root, *args, **kwargs)
        self.config(style="primary.TFrame")

        self.group_index = appointment_group_index
        self.period_start = period_start
        self.period_duration = period_duration
        self.period_end = period_start + period_duration
        self.text = ttk.Label(self, style="primary.TLabel")
        self.text.pack(fill="both", expand=True, padx=3, pady=3)
        self.draw()

    @property
    def appointments(self):
        return AppointmentsTab.appointment_groups[self.group_index]

    def subscriber_update(self):
        self.draw()

    def draw(self):
        start = self.period_start.strftime("%H:%M")
        end = self.period_end.strftime("%H:%M")
        self.text.config(
            text=(f"{self.group_index=}\n" f"Appointments: {len(self.appointments)}")
        )

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


class SidePanel(ttk.Frame):
    side_views: dict[str, SideView]  # search, previous_view
    search_bar: SearchBar
    active_view: SideView
    data_pipeline: dict[str, Any] = {}

    def __init__(self, root, *args, **kwargs):
        super().__init__(root, *args, **kwargs)
        SidePanel.update_data("self", self)
        self.side_views = {
            "alert": AlertsView(self),
            "appointment": AppointmentView(self),
            "search": SearchResultsView(self),
            "edit": EditAppointmentView(self),
            "add": AddAppointmentView(self),
        }
        self.active_view = self.side_views["alert"]
        self.search_bar = SearchBar(self)
        self.search_bar.pack(side=tk.BOTTOM, fill="x")
        self._select_view()

    def _select_view(self, view: str | None = None, caller=None, data=None):
        SidePanel.update_data("previous_view", self.active_view.name)
        SidePanel.update_data("caller", caller)
        SidePanel.update_data("caller_data", data)

        self.active_view.forget()
        if view is None:
            view = "alert"
        self.active_view = self.side_views[view]
        self.active_view.pack(side=tk.TOP, fill="both", expand=True)
        self.active_view.update_content()

    @classmethod
    def update_data(cls, key, value):
        cls.data_pipeline[key] = value

    @classmethod
    def fetch_data(cls, key) -> None | Any:
        return cls.data_pipeline.get(key)

    @classmethod
    def select_view(cls, view: str | None = None, caller=None, data=None):
        self = SidePanel.instance()
        if self is None:
            logger.log_warn("SidePanel instance failed to initialize")
            return
        self._select_view(view, caller, data)

    @classmethod
    def instance(cls) -> SidePanel | None:
        return SidePanel.data_pipeline.get("self")


class SideView(ttk.Frame):
    name: str = ""
    data: Any
    header: ttk.Label
    back_btn: ttk.Button

    def __init__(self, root: SidePanel, *args, **kwargs):
        super().__init__(root, *args, **kwargs)
        self.root = root
        self.config(style="primary.TFrame")

    def update_content(self):
        ...
        raise NotImplementedError

    def set_title(self, text: str):
        if hasattr(self, "header"):
            self.header.config(text=text)
            return
        self.header = ttk.Label(self, text=text)
        self.header.pack(side=tk.TOP, fill="x")

    @classmethod
    def add_back_btn(cls, widget):
        btnframe = ttk.Frame(widget)
        btnframe.pack(side=tk.BOTTOM, fill="x")
        button = ttk.Button(
            btnframe,
            text="Back",
            command=lambda: SidePanel.data_pipeline["self"].select_view("alert"),
        )
        button.pack(side=tk.RIGHT)


class AppointmentView(SideView):
    name: str = "appointment"


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
            self.forget()
            self._state = "inactive"
            return

        self._state = "active"
        self.appointment = appointment
        self.customer = appointment.customer
        self.update_content()

    def update_content(self):
        if self.appointment is None:
            self.root.pop_row(self)
            self._state = "inactive"
            return

        original_date = self.appointment.date
        extended_date = original_date + timedelta(minutes=10)
        now = datetime.now()

        if extended_date < now:
            self.root.pop_row(self)
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

        if self.customer:
            name = self.customer.name
        else:
            name = "     ---     "
        self.name_label.config(text=name)
        self.time_label.config(text=time)

    def send_email(self):
        if self.appointment:
            if self.customer and self.customer.email:
                send_mail([self.appointment])
            else:
                showerror("Customer doesn't have an email")

    def show_edit(self):
        SidePanel.select_view(
            "edit",
            "alertrow",
            {"appointment": self.appointment, "customer": self.customer},
        )


class AlertsView(SideView, SubscriberInterface):
    name: str = "alert"
    rows: list[AlertRow]
    appointments: list[Appointment]

    def __init__(self, root, *args, **kwargs):
        SubscriberInterface.__init__(self)
        super().__init__(root, *args, **kwargs)
        self.name = self.__class__.name
        self.set_title("Ειδοποιήσεις")
        self.appointments = []
        self.rows = []

    def update_content(self):
        self.appointments = ac.get_appointments_from_to_date(
            start=datetime.now(), end=datetime.now() + timedelta(days=7)
        )
        alerts_count = len(self.appointments)
        rows_count = len(self.rows)
        print(alerts_count, rows_count)

        if alerts_count > rows_count:
            for _ in range(alerts_count - rows_count):
                self.rows.append(AlertRow(self))

        if rows_count > alerts_count:
            for _ in range(rows_count - alerts_count):
                row = self.rows.pop()
                row.destroy()

        alerts_count = len(self.appointments)
        rows_count = len(self.rows)
        assert alerts_count == rows_count

        for row, appointment in zip(self.rows, self.appointments):
            row.set_appointment(appointment)
            row.pack(fill="x", pady=1, padx=1)

    def pop_row(self, row: AlertRow):
        row.forget()

    def subscriber_update(self):
        self.update_content()


class SearchResultsView(SideView):
    name: str = "search"
    periods: list[tuple[datetime, timedelta]]
    result_frame: ttk.Frame

    def __init__(self, root, *args, **kwargs):
        super().__init__(root, *args, **kwargs)
        self.name = self.__class__.name
        self.set_title("Αποτελέσματα")
        self.result_frame = ttk.Frame(self)
        self.add_back_btn(self)
        self.periods = []

    def update_content(self):
        print("content")
        self.periods = SidePanel.data_pipeline["search"]
        self.result_frame.destroy()
        self.result_frame = ttk.Frame(self)
        for period in self.periods:
            start = period[0].strftime("%d/%m: %H:%M")
            duration = period[1].total_seconds() // 60
            ttk.Button(
                self.result_frame,
                text=f"{start}-{duration} λεπτά",
                command=lambda: self.open_add_screen(period),
            ).pack(fill="x")
        self.result_frame.pack(fill="x")

    def open_add_screen(self, period):
        SidePanel.update_data("add_assist_date", period[0])
        self.root.select_view("add")


class EditAppointmentView(SideView):
    name: str = "edit"

    def __init__(self, root, *args, **kwargs):
        super().__init__(root, *args, **kwargs)
        self.name = self.__class__.name
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill="both", expand=True)
        self.add_back_btn(self)

        self.day_frame = ttk.Frame(self)
        self.hour_frame = ttk.Frame(self)
        self.minute_frame = ttk.Frame(self)
        self.customer_frame = ttk.Frame(self)
        self.day_frame.pack()
        self.hour_frame.pack()
        self.minute_frame.pack()
        self.customer_frame.pack()

        self.day_label = ttk.Label(self.day_frame, text="Ημέρα:")
        self.hour_label = ttk.Label(self.hour_frame, text="Ώρα:")
        self.minute_label = ttk.Label(self.minute_frame, text="Λεπτά:")
        self.customer_label = ttk.Label(self.customer_frame, text="Πελάτης:")

        self.day_label.pack(side=tk.LEFT, fill="x")
        self.hour_label.pack(side=tk.LEFT, fill="x")
        self.minute_label.pack(side=tk.LEFT, fill="x")
        self.customer_label.pack(side=tk.LEFT, fill="x")

        self.field_day = ttk.Entry(self.day_frame)
        self.field_hour = ttk.Entry(self.hour_frame)
        self.field_minute = ttk.Entry(self.minute_frame)
        self.field_customer = ttk.Entry(self.customer_frame)

        self.field_day.pack(side=tk.RIGHT, fill="x")
        self.field_hour.pack(side=tk.RIGHT, fill="x")
        self.field_minute.pack(side=tk.RIGHT, fill="x")
        self.field_customer.pack(side=tk.RIGHT, fill="x")

        self.add_button = tk.Button(self, text="Προσθήκη", command=self.edit)
        self.add_button.pack()

    def edit(self):
        date = datetime.now().replace(
            day=int(self.field_day.get()),
            hour=int(self.field_hour.get()),
            minute=int(self.field_minute.get() or 0),
            second=0,
            microsecond=0,
        )
        customer_input = self.field_customer.get()
        if customer_input:
            customer_id = int(customer_input)
        else:
            customer_id = None
        ac.create_appointment(Appointment(date=date, customer_id=customer_id))
        print("Added", date)
        SidePanel.select_view("alert")

    def update_content(self):
        pass


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
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill="both", expand=True)
        self.add_back_btn(self)

        self.day_frame = ttk.Frame(self)
        self.hour_frame = ttk.Frame(self)
        self.minute_frame = ttk.Frame(self)
        self.customer_frame = ttk.Frame(self)
        self.day_frame.pack()
        self.hour_frame.pack()
        self.minute_frame.pack()
        self.customer_frame.pack()

        self.day_label = ttk.Label(self.day_frame, text="Ημέρα:")
        self.hour_label = ttk.Label(self.hour_frame, text="Ώρα:")
        self.minute_label = ttk.Label(self.minute_frame, text="Λεπτά:")
        self.customer_label = ttk.Label(self.customer_frame, text="Πελάτης:")

        self.day_label.pack(side=tk.LEFT, fill="x")
        self.hour_label.pack(side=tk.LEFT, fill="x")
        self.minute_label.pack(side=tk.LEFT, fill="x")
        self.customer_label.pack(side=tk.LEFT, fill="x")

        self.field_day = ttk.Entry(self.day_frame)
        self.field_hour = ttk.Entry(self.hour_frame)
        self.field_minute = ttk.Entry(self.minute_frame)
        self.field_customer = ttk.Entry(self.customer_frame)

        self.field_day.pack(side=tk.RIGHT, fill="x")
        self.field_hour.pack(side=tk.RIGHT, fill="x")
        self.field_minute.pack(side=tk.RIGHT, fill="x")
        self.field_customer.pack(side=tk.RIGHT, fill="x")

        self.add_button = tk.Button(self, text="Προσθήκη", command=self.add)
        self.add_button.pack()

    def add(self):
        date = datetime.now().replace(
            day=int(self.field_day.get()),
            hour=int(self.field_hour.get()),
            minute=int(self.field_minute.get() or 0),
            second=0,
            microsecond=0,
        )
        customer_input = self.field_customer.get()
        if customer_input:
            customer_id = int(customer_input)
        else:
            customer_id = None
        ac.create_appointment(Appointment(date=date, customer_id=customer_id))
        print("Added", date)
        SidePanel.data_pipeline["self"].select_view("alert")

    def update_content(self):
        pass


class SearchBar(ttk.Frame):
    label: ttk.Label
    entry: ttk.Entry
    button: ttk.Button
    duration: timedelta
    affects: SearchResultsView
    search_results: list[tuple[datetime, timedelta]]

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.inputframe = ttk.Frame(self)
        self.label = ttk.Label(self.inputframe, text="Διάρκεια")
        self.entry = ttk.Entry(self.inputframe)
        self.button = ttk.Button(self, text="Εύρεση κενού χρόνου", command=self.search)
        self.label.pack(side=tk.LEFT)
        self.entry.pack(side=tk.RIGHT)
        self.inputframe.pack(side=tk.TOP, fill="x", expand=True)
        self.button.pack(side=tk.BOTTOM, fill="x")

    def search(self):
        self.duration = timedelta(minutes=int(self.entry.get()))
        self.search_results = ac.get_time_between_appointments(
            start_date=datetime.now(), minumum_free_period=self.duration
        )
        SidePanel.update_data("search", self.search_results)
        SidePanel.data_pipeline["self"].select_view("search")


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
