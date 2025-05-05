from tkinter import ttk
from ..controller.logging import Logger
from ..model.entities import Appointment, Customer

from .shared import (
    form_appointment_year,
    form_appointment_month,
    form_appointment_day,
    form_appointment_hour,
    form_appointment_minute,
    form_appointment_duration,
    set_appointment,
    get_appointment,
    reset_appointment,
)

from .shared import (
    form_customer_name,
    form_customer_surname,
    form_customer_phone,
    form_customer_email,
    set_customer,
    get_customer,
    reset_customer,
)

logger = Logger("entry")


class AppointmentForm(ttk.Frame):
    """
    Φόρμα εισαγωγής/επεξεργασίας ραντεβού
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.anchor("nw")
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        self.columnconfigure(2, weight=2)
        self.columnconfigure(3, weight=2)

        self.app_label_date = ttk.Label(self, text="Date")
        self.app_entry_day = ttk.Entry(self, width=2, textvariable=form_appointment_day)
        self.app_entry_month = ttk.Entry(self, width=2, textvariable=form_appointment_month)
        self.app_entry_year = ttk.Entry(self, width=4, textvariable=form_appointment_year)

        self.app_label_time = ttk.Label(self, text="Time")
        self.app_entry_hour = ttk.Entry(self, width=2, textvariable=form_appointment_hour)
        self.app_entry_minute = ttk.Entry(self, width=2, textvariable=form_appointment_minute)

        self.app_label_duration = ttk.Label(self, text="Duration")
        self.app_entry_duration = ttk.Entry(self, width=2, textvariable=form_appointment_duration)

        self.app_label_date.grid(row=0, column=0, sticky="e", padx=3)
        self.app_entry_day.grid(row=0, column=1, sticky="we")
        self.app_entry_month.grid(row=0, column=2, sticky="we")
        self.app_entry_year.grid(row=0, column=3, sticky="we")

        self.app_label_time.grid(row=1, column=0, sticky="e", padx=3)
        self.app_entry_hour.grid(row=1, column=1, sticky="we")
        self.app_entry_minute.grid(row=1, column=2, sticky="we")

        self.app_label_duration.grid(row=2, column=0, sticky="e", padx=3)
        self.app_entry_duration.grid(row=2, column=1, sticky="we")

    def get(self) -> Appointment:
        return get_appointment()

    def populate(self, appointment: Appointment):
        reset_appointment()
        set_appointment(appointment)


class CustomerForm(ttk.Frame):
    """
    Φορμα εγγραφής/επεξεργασίας πελάτη
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.cus_label_name = ttk.Label(self, text="Name")
        self.cus_label_surname = ttk.Label(self, text="Surname")
        self.cus_label_phone = ttk.Label(self, text="Phone")
        self.cus_label_email = ttk.Label(self, text="email")

        self.cus_entry_name = ttk.Entry(self, textvariable=form_customer_name)
        self.cus_entry_surname = ttk.Entry(self, textvariable=form_customer_surname)
        self.cus_entry_phone = ttk.Entry(self, textvariable=form_customer_phone)
        self.cus_entry_email = ttk.Entry(self, textvariable=form_customer_email)

        for i in range(2):
            self.columnconfigure(i, weight=1)

        self.cus_label_name.grid(column=0, row=0, sticky="nse")
        self.cus_label_surname.grid(column=0, row=1, sticky="nse")
        self.cus_label_phone.grid(column=0, row=2, sticky="nse")
        self.cus_label_email.grid(column=0, row=3, sticky="nse")

        self.cus_entry_name.grid(column=1, row=0, sticky="nse")
        self.cus_entry_surname.grid(column=1, row=1, sticky="nse")
        self.cus_entry_phone.grid(column=1, row=2, sticky="nse")
        self.cus_entry_email.grid(column=1, row=3, sticky="nse")

    def get(self):
        return get_customer()

    def populate(self, customer: Customer | None):
        reset_customer()
        set_customer(customer)
