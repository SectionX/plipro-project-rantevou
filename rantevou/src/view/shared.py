# Πειραματική αλλαγή
from time import sleep
from tkinter import StringVar, IntVar
from threading import Thread
from datetime import datetime, timedelta

from ..model.entities import Appointment, Customer
from ..controller import get_config

cfg = get_config()["view_settings"]
min_duration = cfg["minimum_appointment_duration"]


# class StringVar:

#     def __init__(self):
#         self.value = ""

#     def get(self):
#         return self.value

#     def set(self, value):
#         self.value = str(value)

#     def __str__(self):
#         return self.value


# class IntVar:

#     def __init__(self):
#         self.value = 0

#     def get(self):
#         return self.value

#     def set(self, value):
#         self.value = int(value)

#     def __str__(self):
#         return str(self.value)


loading_text: StringVar = StringVar()


def __load():
    global loading_text
    dots = ["", "", ""]
    dot_pointer = 0

    while True:
        sleep(0.5)
        if dot_pointer == 3:
            dots[0] = ""
            dots[1] = ""
            dots[2] = ""
            dot_pointer = 0
            continue

        dots[dot_pointer] = "."
        loading_text.set("".join(dots))
        dot_pointer += 1


Thread(target=__load, daemon=True).start()

__appointment_id: int | None = None
__appointment_customer_id: int | None = None
__appointment_employee_id: int | None = None
form_appointment_year: IntVar = IntVar()
form_appointment_month: IntVar = IntVar()
form_appointment_day: IntVar = IntVar()
form_appointment_hour: IntVar = IntVar()
form_appointment_minute: IntVar = IntVar()
form_appointment_duration: IntVar = IntVar()

__customer_id: int | None = None
form_customer_name: StringVar = StringVar()
form_customer_surname: StringVar = StringVar()
form_customer_phone: StringVar = StringVar()
form_customer_email: StringVar = StringVar()

searchbar_time_between: IntVar = IntVar()
searchbar_customer: StringVar = StringVar()


def set_appointment(appointment: Appointment | None) -> None:
    """
    Γεμίζει τα πεδία της φόρμας με τα στοιχεία του ραντεβού

    Args:
        appointment (Appointment)
    """
    global __appointment_id
    global __appointment_customer_id
    global __appointment_employee_id
    global form_appointment_year
    global form_appointment_month
    global form_appointment_day
    global form_appointment_hour
    global form_appointment_minute
    global form_appointment_duration

    if appointment is None:
        __appointment_id = None
        __appointment_customer_id = None
        __appointment_employee_id = None

        form_appointment_year.set(0)
        form_appointment_month.set(0)
        form_appointment_day.set(0)
        form_appointment_hour.set(0)
        form_appointment_minute.set(0)
        form_appointment_duration.set(0)
        return

    __appointment_id = appointment.id
    __appointment_customer_id = appointment.customer_id
    __appointment_employee_id = appointment.employee_id

    form_appointment_year.set(appointment.date.year or 0)
    form_appointment_month.set(appointment.date.month or 0)
    form_appointment_day.set(appointment.date.day or 0)
    form_appointment_hour.set(appointment.date.hour or 0)
    form_appointment_minute.set(appointment.date.minute or 0)
    form_appointment_duration.set(int(appointment.duration.total_seconds() // 60) or 0)


def get_appointment() -> Appointment:
    """
    Παίρνει τα στοιχεία από την φόρμα σε μορφή SQL object

    Returns:
        Appointment: _description_
    """
    global __appointment_id
    global __appointment_customer_id
    global __appointment_employee_id
    global form_appointment_year
    global form_appointment_month
    global form_appointment_day
    global form_appointment_hour
    global form_appointment_minute
    global form_appointment_duration

    date = datetime(
        year=form_appointment_year.get(),
        month=form_appointment_month.get(),
        day=form_appointment_day.get(),
        hour=form_appointment_hour.get(),
        minute=form_appointment_minute.get(),
    )
    appointment = Appointment(
        date=date,
        duration=timedelta(minutes=form_appointment_duration.get()),
        id=__appointment_id,
        customer_id=__appointment_customer_id,
        employee_id=__appointment_employee_id,
    )

    return appointment


def reset_appointment() -> None:
    """
    Επαναφέρει τα πεδία στα defaults (τωρινή ημερομηνία και ώρα)
    """
    global __appointment_id
    global __appointment_customer_id
    global __appointment_employee_id
    global form_appointment_year
    global form_appointment_month
    global form_appointment_day
    global form_appointment_hour
    global form_appointment_minute
    global form_appointment_duration

    __appointment_id = None
    __appointment_customer_id = None
    __appointment_employee_id = None

    now = datetime.now()

    form_appointment_year.set(now.year)
    form_appointment_month.set(now.month)
    form_appointment_day.set(now.day)
    form_appointment_hour.set(now.hour)
    form_appointment_minute.set(now.minute)
    form_appointment_duration.set(min_duration)


def set_customer(customer: Customer | None) -> None:
    """
    Γεμίζει τα πεδία της φόρμας με τα στοιχεία του πελάτη

    Args:
        customer (Customer)
    """
    global __customer_id
    global form_customer_name
    global form_customer_surname
    global form_customer_phone
    global form_customer_email

    if customer is None:
        __customer_id = None
        form_customer_name.set("")
        form_customer_surname.set("")
        form_customer_phone.set("")
        form_customer_email.set("")
        return

    __customer_id = customer.id
    form_customer_name.set(customer.name or "")
    form_customer_surname.set(customer.surname or "")
    form_customer_phone.set(customer.phone or "")
    form_customer_email.set(customer.email or "")


def get_customer() -> Customer:
    """
    Παίρνει τα στοιχεία από την φόρμα σε μορφή SQL object

    Returns:
        customer (Customer)
    """
    global __customer_id
    global form_customer_name
    global form_customer_surname
    global form_customer_phone
    global form_customer_email

    customer = Customer(
        id=__customer_id,
        name=form_customer_name.get(),
        surname=form_customer_surname.get(),
        phone=form_customer_phone.get(),
        email=form_customer_email.get(),
    )

    return customer


def reset_customer() -> None:
    """
    Επαναφέρει τα κείμενα στην αρχική μορφή (άδειο)
    """
    global __customer_id
    global form_customer_name
    global form_customer_surname
    global form_customer_phone
    global form_customer_email

    __customer_id = None
    form_customer_name.set("")
    form_customer_surname.set("")
    form_customer_phone.set("")
    form_customer_email.set("")
