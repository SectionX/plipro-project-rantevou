from __future__ import annotations

from typing import Any, Literal
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror

from ..controller.logging import Logger
from ..controller.mailer import Mailer
from ..controller.appointments_controller import AppointmentControl
from ..controller.customers_controller import CustomerControl
from ..model.types import Appointment, Customer

ac = AppointmentControl()
cc = CustomerControl()
mailer = Mailer()
logger = Logger("sidepanel")


class SubscriberInterface:
    def __init__(self):
        ac.add_subscription(self)

    def subscriber_update(self):
        raise NotImplementedError


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
            "appointments": AppointmentView(self),
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
            text="Go to Alerts",
            command=lambda: SidePanel.select_view("alert"),
        )
        button.pack(side=tk.RIGHT)


class AppointmentViewButton(ttk.Button):
    appointment: Appointment | None

    def __init__(self, master, *args, appointment: Appointment | None = None, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.appointment = appointment
        if self.appointment:
            self.config(text=str(self.appointment.date), command=self.edit_appointment)
        else:
            self.config(text="+", command=self.add_appointment)

    def add_appointment(self):
        SidePanel.select_view(
            "add", caller="appointments", data={"appointment": self.appointment}
        )

    def edit_appointment(self):
        SidePanel.select_view(
            "edit", caller="appointments", data={"appointment": self.appointment}
        )


class AppointmentView(SideView):
    name: str = "appointments"
    add_button: ttk.Button
    edit_button: ttk.Button
    caller_data: list[Appointment]

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.name = self.__class__.name
        self.main_frame = ttk.Frame(self)
        self.set_title("Ραντεβού")
        self.main_frame.pack(fill="both", expand=True)
        self.add_back_btn(self)

    def update_content(self):
        buttons = list(self.main_frame.children.values())
        while buttons:
            button = buttons.pop()
            button.destroy()

        caller_data = SidePanel.fetch_data("caller_data")
        try:
            if caller_data:
                for appointment in caller_data:
                    AppointmentViewButton(
                        self.main_frame, appointment=appointment
                    ).pack(fill="x")
        except Exception as e:
            logger.log_warn(f"Error with caller's data: {str(e)}")

        AppointmentViewButton(self.main_frame, appointment=None).pack(fill="x")


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
                mailer.send_email([self.appointment])
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
        SidePanel.select_view("add")


class EditAppointmentView(SideView):
    name: str = "edit"
    appointment: Appointment | None
    customer: Customer | None

    def __init__(self, root, *args, **kwargs):
        super().__init__(root, *args, **kwargs)
        self.name = self.__class__.name
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill="both", expand=True)
        self.add_back_btn(self)

        self.appointment = None
        self.customer = None

        self.app_entry_date = ttk.Entry(self.main_frame)
        self.app_entry_date.pack(fill="x")
        self.app_entry_duration = ttk.Entry(self.main_frame)
        self.app_entry_duration.pack(fill="x")
        self.app_entry_is_alerted = ttk.Entry(self.main_frame)
        self.app_entry_is_alerted.pack(fill="x")
        self.cus_entry_name = ttk.Entry(self.main_frame)
        self.cus_entry_name.pack(fill="x")
        self.cus_entry_surname = ttk.Entry(self.main_frame)
        self.cus_entry_surname.pack(fill="x")
        self.cus_entry_phone = ttk.Entry(self.main_frame)
        self.cus_entry_phone.pack(fill="x")
        self.cus_entry_email = ttk.Entry(self.main_frame)
        self.cus_entry_email.pack(fill="x")
        self.save_button = ttk.Button(self.main_frame, text="Save", command=self.save)
        self.save_button.pack()

    def update_content(self):
        self.reset()
        caller_data = SidePanel.fetch_data("caller_data")
        if caller_data is None:
            logger.log_warn("Failed to retrieve appointment data")
            return

        self.appointment = caller_data["appointment"]
        if self.appointment is None:
            logger.log_warn("Failed to retrieve appointment data")
            raise ValueError

        try:
            self.customer = caller_data["customer"]
        except:
            logger.log_warn("Failed to retrieve customer data, querying database...")
            self.customer = self.appointment.customer

        self.app_entry_date.insert(0, str(self.appointment.date))
        self.app_entry_duration.insert(0, str(self.appointment.duration))
        self.app_entry_is_alerted.insert(0, str(self.appointment.is_alerted))

        if self.customer is None:
            self.cus_entry_name.insert(0, "Customer name")
            self.cus_entry_surname.insert(0, "Customer surname")
            self.cus_entry_phone.insert(0, "Customer phone")
            self.cus_entry_email.insert(0, "Customer email")
        else:
            self.cus_entry_name.insert(0, self.customer.name)
            self.cus_entry_surname.insert(0, self.customer.surname)
            self.cus_entry_phone.insert(0, self.customer.phone)
            self.cus_entry_email.insert(0, self.customer.email)

    def save(self):
        # TODO Μετατροπή δεδομένων σε κατάλληλο τύπο και σύνδεση με την
        # βάση δεδομένων
        new_appointment = Appointment(
            date=self.app_entry_date.get(),
            duration=self.app_entry_duration.get(),
            is_alerted=self.app_entry_is_alerted.get(),
        )
        new_customer = Customer(
            name=self.cus_entry_name.get(),
            surname=self.cus_entry_surname.get(),
            phone=self.cus_entry_phone.get(),
            email=self.cus_entry_email.get(),
        )
        print(new_appointment, new_customer)

    def reset(self):
        for k, v in self.__dict__.items():
            if isinstance(v, ttk.Entry):
                v.delete(0, tk.END)


class EntryWithPlaceholder(ttk.Entry):

    def __init__(self, master, placeholder: str, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.placeholder = placeholder
        self.bind("<Button-1>", lambda x: self.clear())

    def put_placeholder(self):
        self.insert(0, self.placeholder)

    def clear(self):
        text = self.get()
        if text == self.placeholder:
            self.delete(0, tk.END)


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

        self.appointment = None
        self.customer = None

        self.app_entry_date = EntryWithPlaceholder(self.main_frame, placeholder="date")
        self.app_entry_date.pack(fill="x")
        self.app_entry_duration = EntryWithPlaceholder(
            self.main_frame, placeholder="duration"
        )
        self.app_entry_duration.pack(fill="x")
        self.cus_entry_name = EntryWithPlaceholder(self.main_frame, placeholder="name")
        self.cus_entry_name.pack(fill="x")
        self.cus_entry_surname = EntryWithPlaceholder(
            self.main_frame, placeholder="surname"
        )
        self.cus_entry_surname.pack(fill="x")
        self.cus_entry_phone = EntryWithPlaceholder(
            self.main_frame, placeholder="phone number"
        )
        self.cus_entry_phone.pack(fill="x")
        self.cus_entry_email = EntryWithPlaceholder(
            self.main_frame, placeholder="email address"
        )
        self.cus_entry_email.pack(fill="x")
        self.save_button = ttk.Button(self.main_frame, text="Save", command=self.save)
        self.save_button.pack()

    def update_content(self):
        self.reset()

    def save(self):
        # TODO -> Make it save the data to db
        print(
            self.app_entry_date.get(),
            self.app_entry_duration.get(),
            self.cus_entry_name.get(),
            self.cus_entry_surname.get(),
            self.cus_entry_phone.get(),
            self.cus_entry_email.get(),
            sep="\n",
        )

    def populate_customer(self):
        pass

    def reset(self):
        for k, v in self.__dict__.items():
            if isinstance(v, EntryWithPlaceholder):
                v.delete(0, tk.END)
                v.put_placeholder()


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
