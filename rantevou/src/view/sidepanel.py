"""
Βιβλιοθήκη για τα components που αφορούν το πλάγιο panel

SidePanel -> Κεντρικό αντικείμενο που ελέγχει τα υπόλοιπα. Προσάπτεται στο root window
AppointmentView -> Εμφάνιση πληροφοριών ραντεβού για μια χρονική περιόδο
SearchView -> Εμφάνιση αποτελεσμάτων μετά από αναζήτη για χρόνο μεταξύ ραντεβού
AlertView -> Εμφάνιση των προσεχών ραντεβού με δυνατότητα αποστολής email
AddAppointmentView -> Δημιουργία νέου ραντεβού
EditAppointmentView -> Διαχείριση υπάρχοντως ραντεβού
AddCustomerView -> Δημιουργία νέου πελάτη
EditCustomerView -> Διαχείριση υπάρχοντως πελάτη

Η εμφάνιση αυτών των view γίνεται μέσω της μεθόδου SidePanel.select_view
με πρώτη παράμετρο το όνομα του view

Αντιστοιχία ονομάτων
appointments | AppointmentView
search | SearchView
alert | AlertView
add | AddAppointmentView
edit | EditAppointmentView
addc | AddCustomerView
editc | EditCustomerView
"""

from __future__ import annotations

from typing import Any, Literal
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror

from ..controller import get_config
from ..controller.logging import Logger
from ..controller.mailer import Mailer
from ..controller.appointments_controller import AppointmentControl
from ..controller.customers_controller import CustomerControl
from ..model.types import Appointment, Customer

cfg = get_config()
ac = AppointmentControl()
cc = CustomerControl()
mailer = Mailer()
logger = Logger("sidepanel")


class SubscriberInterface:
    def __init__(self):
        ac.add_subscription(self)
        cc.add_subscription(self)

    def subscriber_update(self):
        raise NotImplementedError


class SidePanel(ttk.Frame):
    """
    Η βασική οντότητα. Σημαντικό χαρακτηριστικό ότι είναι φτιαγμένη
    ώστε να είναι μοναδική (singleton pattern) και διαχειρίζεται
    global state ώστε να μπορούν όλα τα υπόλοιπα αντικείμενα να
    επικοινωνούν σωστά.

    Βασικές μέθοδοι:
    SidePanel.instance() -> Επιστρέφει το ένα και μοναδικό αντικείμενο
    SidePanel.select_vew() -> API που επιτρέπει στα άλλα αντικείμενα να
                                ζητούν αλλαγή του panel
    SidePanel.update_data() -> API που επιτρέπει στα άλλα αντικείμενα να
                                στέλνουν πληροφορίες
    SidePanel.fetch_data() -> API που επιτρέπει στα άλλα αντικείμενα να
                                λάβουν τις αποθηκευμένες πληροφορίες

    Παράδειγμα, όταν πατάμε ένα κελί στο grid των ραντεβού, ζητάμε από το
    SidePanel να μας εμφανίσει το panel διαχείρησης αυτού του κελιού με τον
    εξής τρόπο

    SidePanel.select_view("appointments", caller=self, data=...)

    Όπου caller είναι το κελί, και data είναι τα ραντεβού που διαχειρίζεται
    το συγκεκριμένο κελί.

    Το SidePanel αποθηκεύει αυτά τα δεδομένα ως "caller":self, και
    "caller_data": ..., ώστε να μπορεί να εμφανίζει σχετικές πληροφορίες
    που αφορούν αυτό το κελί
    """

    _instance = None
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
            "addc": AddCustomerView(self),
            "editc": EditCustomerView(self),
        }
        self.active_view = self.side_views["alert"]
        self.search_bar = SearchBar(self)
        self.search_bar.pack(side=tk.BOTTOM, fill="x")
        self._select_view()

    def _select_view(self, view: str | None = None, caller=None, data=None):
        SidePanel.update_data("previous_view", self.active_view.name)
        SidePanel.update_data("previous_caller", SidePanel.fetch_data("caller"))
        SidePanel.update_data(
            "previous_caller_data", SidePanel.fetch_data("caller_data")
        )
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

    @classmethod
    def get_active_view(cls):
        sidepanel = cls.instance()
        if sidepanel is None:
            logger.log_error("Failed to fetch sidepanel instance")
            return None
        return sidepanel.active_view


class SideView(ttk.Frame):
    """
    Ο γονέας όλων των panels που εμφανίζονται στο SidePanel. Ορίζει τις βοηθητικές
    συναρτήσεις "set_title" και "add_back_button" που θέλουν να χρησιμοποιούν όλα
    τα panels.

    Κάθε παιδί πρέπει να υλοποιεί την μέθοδο "update_content" που καλεί το SidePanel
    όταν αλλάζει το panel μετά από εντολή κάποιου άλλου component όπως το παράδειγμα
    που δώσαμε στην επεξήγηση του SidePanel.

    Η συνήθης χρήση για την υλοποίηση είναι να λάβουμε τα στοιχεία από το SidePanel
    και να τα εμφανίσουμε. Π.χ.

    def update_content(self):
        caller_data = SidePanel.fetch_data("caller_data")
        label = ttk.Label(self, text=str(caller_data))
        label.pack()
    """

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
        SidePanel.select_view(
            "add",
            caller="appointments",
            data=(self.expiration_date - self.duration, self.duration),
        )

    def edit_appointment(self):
        SidePanel.select_view("edit", caller="appointments", data=self.appointment)


class AppointmentView(SideView):
    name: str = "appointments"
    add_button: ttk.Button
    edit_button: ttk.Button
    caller_data: list[Appointment]

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.name = self.__class__.name
        self.main_frame = ttk.Frame(
            self, style="primary.TFrame", borderwidth=3, relief="sunken"
        )
        self.set_title("Ραντεβού")
        self.main_frame.pack(fill="both", expand=True)
        self.add_back_btn(self)

    def update_content(self):
        for button in tuple(self.main_frame.children.values()):
            button.destroy()

        caller_data = SidePanel.fetch_data("caller_data")
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
                mailer.send_email(
                    [self.appointment], debug=True
                )  # TODO change for live
            else:
                showerror("Customer doesn't have an email")

    def show_edit(self):
        SidePanel.select_view(
            "edit",
            "alertrow",
            self.appointment,
        )


class AlertsView(SideView, SubscriberInterface):
    name: str = "alert"
    rows: list[AlertRow]
    appointments: list[Appointment]

    def __init__(self, root, *args, **kwargs):
        super().__init__(root, *args, **kwargs)
        SubscriberInterface.__init__(self)
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


class SearchResult(ttk.Button):

    def __init__(self, master, period: datetime, duration: timedelta, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.config(command=self.open_add_screen)
        self.period = period
        self.duration = duration

    def open_add_screen(self):
        SidePanel.select_view("add", caller="search", data=(self.period, self.duration))


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
        periods: list | Any | None
        user_input: timedelta | Any | None
        caller_data = SidePanel.fetch_data("caller_data")

        if not (isinstance(caller_data, tuple) and len(caller_data) == 2):
            raise Exception("Searchbar passed wrong data")

        periods, user_input = caller_data

        if not isinstance(periods, list):
            raise Exception("Results must be in a list")

        if not isinstance(user_input, timedelta):
            raise Exception("User input must be in timedelta")

        self.periods = periods
        self.user_input = user_input

        self.result_frame.destroy()
        self.result_frame = ttk.Frame(self)
        for period, duration in self.periods:
            start = period.strftime("%d/%m: %H:%M")
            duration_mins = int(duration.total_seconds() // 60)
            SearchResult(
                self.result_frame,
                period=period,
                duration=duration,
                text=f"{start}-{duration_mins} λεπτά",
            ).pack(fill="x")
        self.result_frame.pack(fill="x")


class EditAppointmentView(SideView):
    name: str = "edit"
    appointment: Appointment
    customer: Customer | None

    def __init__(self, root, *args, **kwargs):
        super().__init__(root, *args, **kwargs)
        self.name = self.__class__.name
        self.main_frame = ttk.Frame(self, borderwidth=3, relief="sunken")
        self.main_frame.pack(fill="both", expand=True)
        self.add_back_btn(self)

        self.appointment = Appointment()
        self.customer = None

        self.date_frame = ttk.Frame(self.main_frame)
        self.date_frame.pack()

        self.hour_frame = ttk.Frame(self.main_frame)
        self.hour_frame.pack()

        self.app_entry_day = ttk.Entry(self.date_frame, width=2)
        self.app_entry_day.pack(side=tk.LEFT)
        ttk.Label(self.date_frame, text="/").pack(side=tk.LEFT)
        self.app_entry_month = ttk.Entry(self.date_frame, width=2)
        self.app_entry_month.pack(side=tk.LEFT)
        ttk.Label(self.date_frame, text="/").pack(side=tk.LEFT)
        self.app_entry_year = ttk.Entry(self.date_frame, width=4)
        self.app_entry_year.pack(side=tk.LEFT)

        self.app_entry_hour = ttk.Entry(self.hour_frame, width=2)
        self.app_entry_hour.pack(side=tk.LEFT)
        ttk.Label(self.hour_frame, text=":").pack(side=tk.LEFT)
        self.app_entry_minute = ttk.Entry(self.hour_frame, width=2)
        self.app_entry_minute.pack(side=tk.LEFT)

        self.app_entry_duration = ttk.Entry(self.main_frame)
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
        self.delete_button = ttk.Button(
            self.main_frame, text="Delete", command=self.delete
        )
        self.delete_button.pack()

    def update_content(self):
        self.reset()
        caller_data = SidePanel.fetch_data("caller_data")
        logger.log_info(f"Showing data {caller_data} for editing")

        if caller_data is None:
            logger.log_warn("Failed to retrieve appointment data")
            return

        if not isinstance(caller_data, Appointment):
            logger.log_warn("Failed to retrieve appointment data")
            return

        self.appointment = caller_data
        if self.appointment is None:
            logger.log_warn("Failed to retrieve appointment data")
            raise ValueError

        self.customer = self.appointment.customer
        logger.log_info(f"Showing data {self.customer} for editing")

        date = self.appointment.date

        self.app_entry_year.insert(0, str(date.year))
        self.app_entry_month.insert(0, f"{date.month:02d}")
        self.app_entry_day.insert(0, f"{date.day:02d}")
        self.app_entry_hour.insert(0, f"{date.hour:02d}")
        self.app_entry_minute.insert(0, f"{date.minute:02d}")
        self.app_entry_duration.insert(
            0, str(int(self.appointment.duration.total_seconds() // 60))
        )

        if self.customer is None:
            self.cus_entry_name.put_placeholder()
            self.cus_entry_surname.put_placeholder()
            self.cus_entry_phone.put_placeholder()
            self.cus_entry_email.put_placeholder()
        else:
            self.cus_entry_name.insert(0, self.customer.name)
            if self.cus_entry_surname is not None:
                self.cus_entry_surname.insert(0, self.customer.surname)
            if self.cus_entry_phone is not None:
                self.cus_entry_phone.insert(0, self.customer.phone)
            if self.cus_entry_email is not None:
                self.cus_entry_email.insert(0, self.customer.email)

    def delete(self):
        # TODO Μετατροπή δεδομένων σε κατάλληλο τύπο και σύνδεση με την
        # βάση δεδομένων
        ac.delete_appointment(self.appointment)

    def save(self):
        # TODO Μετατροπή δεδομένων σε κατάλληλο τύπο και σύνδεση με την
        # βάση δεδομένων

        date = datetime(
            year=int(self.app_entry_year.get()),
            month=int(self.app_entry_month.get()),
            day=int(self.app_entry_day.get()),
            hour=int(self.app_entry_hour.get()),
            minute=int(self.app_entry_minute.get()),
        )

        new_appointment = Appointment(
            id=self.appointment.id,
            date=date,
            duration=timedelta(minutes=int(self.app_entry_duration.get())),
            is_alerted=self.appointment.is_alerted,
            customer_id=self.appointment.customer_id,
        )
        new_customer: Customer = Customer(
            name=self.cus_entry_name.get_without_placeholder(),
            surname=self.cus_entry_surname.get_without_placeholder(),
            phone=self.cus_entry_phone.get_without_placeholder(),
            email=self.cus_entry_email.get_without_placeholder(),
        )
        if self.customer is not None:
            new_customer.id = self.customer.id

        if new_customer.name == None:
            logger.log_info("Updating appointmenth without customer")
            result = ac.update_appointment(new_appointment)
        else:
            result = ac.update_appointment(new_appointment, new_customer)

        if not result:
            showerror("Something went wrong...")
            self.update_content()

    def reset(self):
        for k, v in self.__dict__.items():
            if isinstance(v, ttk.Entry):
                v.delete(0, tk.END)

    def populate_from_customer_tab(self):
        data = SidePanel.fetch_data("customer_data")
        if not isinstance(data, list):
            logger.log_error("Data from customer was wrong type")
            return

        id, name, surname, phone, email, *_ = data
        self.cus_entry_name.delete(0, tk.END)
        self.cus_entry_name.insert(0, name)
        self.cus_entry_surname.delete(0, tk.END)
        self.cus_entry_surname.insert(0, surname)
        self.cus_entry_phone.delete(0, tk.END)
        self.cus_entry_phone.insert(0, phone)
        self.cus_entry_email.delete(0, tk.END)
        self.cus_entry_email.insert(0, email)
        self.appointment.customer_id = int(id)


class EntryWithPlaceholder(ttk.Entry):

    def __init__(self, master, placeholder: str, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.placeholder = placeholder
        self.bind("<Button-1>", lambda x: self.clear())
        self.config(width=4)

    def put_placeholder(self):
        self.insert(0, self.placeholder)

    def clear(self):
        text = self.get()
        if text == self.placeholder:
            self.delete(0, tk.END)

    def get_without_placeholder(self):
        text = self.get()
        if text == self.placeholder:
            return None
        return text


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
        self.main_frame = ttk.Frame(self, borderwidth=3, relief="sunken")
        self.main_frame.pack(fill="both", expand=True)
        self.add_back_btn(self)

        self.appointment = None
        self.customer = None

        year, month, day, *_ = self.date_to_string(datetime.now())
        duration = "20"  # TODO να έρχεται από το config file

        self.date_frame = ttk.Frame(self.main_frame)
        self.date_frame.pack()

        self.app_entry_day = EntryWithPlaceholder(self.date_frame, placeholder="")
        self.app_entry_day.pack(side=tk.LEFT)
        ttk.Label(self.date_frame, text="/").pack(
            side=tk.LEFT,
        )
        self.app_entry_month = EntryWithPlaceholder(self.date_frame, placeholder="")
        self.app_entry_month.pack(side=tk.LEFT)
        ttk.Label(self.date_frame, text="/").pack(
            side=tk.LEFT,
        )
        self.app_entry_year = EntryWithPlaceholder(self.date_frame, placeholder="")
        self.app_entry_year.pack(side=tk.LEFT)

        self.hour_frame = ttk.Frame(self.main_frame)
        self.hour_frame.pack()

        self.app_entry_hour = EntryWithPlaceholder(self.hour_frame, placeholder="")
        self.app_entry_hour.pack(side=tk.LEFT)
        ttk.Label(self.hour_frame, text=":").pack(side=tk.LEFT)
        self.app_entry_minutes = EntryWithPlaceholder(self.hour_frame, placeholder="")
        self.app_entry_minutes.pack(side=tk.LEFT)

        self.app_entry_duration = EntryWithPlaceholder(
            self.main_frame, placeholder=duration
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

    def date_to_string(self, date: datetime) -> list[str]:
        datestring = date.strftime("%Y_%m_%d_%H_%M_%S")
        return datestring.split("_")

    def update_content(self):
        data = SidePanel.fetch_data("caller_data")
        logger.log_info(f"Showing appointment creation panel with data {data}")

        if not isinstance(data, tuple):
            logger.log_warn("Wrong data")
            return

        if not isinstance(data[0], datetime):
            logger.log_warn("Wrong data")
            return

        if not isinstance(data[1], timedelta):
            logger.log_warn("Wrong data")
            return

        date = data[0]
        duration = data[1]

        year, month, day, hour, minute, *_ = self.date_to_string(date)
        self.app_entry_year.placeholder = year
        self.app_entry_month.placeholder = month
        self.app_entry_day.placeholder = day
        self.app_entry_hour.placeholder = hour
        self.app_entry_minutes.placeholder = minute
        self.app_entry_duration.placeholder = str(int(duration.total_seconds() // 60))
        self.reset()

    def save(self):
        date = datetime(
            year=int(self.app_entry_year.get()),
            month=int(self.app_entry_month.get()),
            day=int(self.app_entry_day.get()),
            hour=int(self.app_entry_hour.get()),
            minute=int(self.app_entry_minutes.get()),
            second=0,
            microsecond=0,
        )
        duration = timedelta(minutes=int(self.app_entry_duration.get()))

        appointment = Appointment(date=date, duration=duration)
        customer = Customer(
            name=self.cus_entry_name.get_without_placeholder(),
            surname=self.cus_entry_surname.get_without_placeholder(),
            phone=self.cus_entry_phone.get_without_placeholder(),
            email=self.cus_entry_email.get_without_placeholder(),
        )
        ac.create_appointment(appointment, customer)

    def populate_from_customer_tab(self):
        customer_data = SidePanel.fetch_data("customer_data")
        if not isinstance(customer_data, list):
            logger.log_warn("Failed to communicate customer data")
            return

        if len(customer_data) < 5:
            logger.log_warn("Failed to communicate customer data")
            return

        self.cus_entry_name.delete(0, tk.END)
        self.cus_entry_surname.delete(0, tk.END)
        self.cus_entry_phone.delete(0, tk.END)
        self.cus_entry_email.delete(0, tk.END)

        self.cus_entry_name.insert(0, customer_data[1])
        self.cus_entry_surname.insert(0, customer_data[2])
        self.cus_entry_phone.insert(0, customer_data[3])
        self.cus_entry_email.insert(0, customer_data[4])

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
        user_input: int | str = self.entry.get()

        if isinstance(user_input, str):
            if user_input.isdigit():
                user_input = int(user_input)
            else:
                user_input = 0

        self.duration = timedelta(minutes=user_input)
        self.search_results = ac.get_time_between_appointments(
            start_date=datetime.now(), minumum_free_period=self.duration
        )
        SidePanel.select_view(
            "search", caller=self, data=(self.search_results, self.duration)
        )


class AddCustomerView(SideView):

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.name = "addc"
        self.main_frame = ttk.Frame(self, borderwidth=3, relief="sunken")

        self.set_title("Προσθήκη νέου πελάτη")
        self.main_frame.pack(fill="both", expand=True)
        self.add_back_btn(self)

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
        for entry in self.main_frame.winfo_children():
            if isinstance(entry, EntryWithPlaceholder):
                entry.delete(0, tk.END)
                entry.put_placeholder()

    def save(self):
        cc.create_customer(
            Customer(
                name=self.cus_entry_name.get_without_placeholder(),
                surname=self.cus_entry_surname.get_without_placeholder(),
                phone=self.cus_entry_phone.get_without_placeholder(),
                email=self.cus_entry_email.get_without_placeholder(),
            )
        )


class EditCustomerView(SideView):

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.name = "editc"
        self.main_frame = ttk.Frame(self, borderwidth=3, relief="sunken")

        self.set_title("Επεξεργασία νέου πελάτη")
        self.main_frame.pack(fill="both", expand=True)
        self.add_back_btn(self)

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
        if not isinstance(caller_data, list):
            logger.log_warn("Failed to communicate customer data")
            return

        if len(caller_data) < 5:
            logger.log_warn("Failed to communicate customer data")
            return

        self.cus_id = int(caller_data[0])
        if caller_data[1] is not None:
            self.cus_entry_name.insert(0, caller_data[1])
        if caller_data[2] is not None:
            self.cus_entry_surname.insert(0, caller_data[2])
        if caller_data[3] is not None:
            self.cus_entry_phone.insert(0, caller_data[3])
        if caller_data[4] is not None:
            self.cus_entry_email.insert(0, caller_data[4])

    def save(self):
        cc.update_customer(
            Customer(
                id=self.cus_id,
                name=self.cus_entry_name.get() or None,
                surname=self.cus_entry_surname.get() or None,
                phone=self.cus_entry_phone.get() or None,
                email=self.cus_entry_email.get() or None,
            )
        )

    def reset(self):
        self.cus_entry_name.delete(0, tk.END)
        self.cus_entry_surname.delete(0, tk.END)
        self.cus_entry_phone.delete(0, tk.END)
        self.cus_entry_email.delete(0, tk.END)
