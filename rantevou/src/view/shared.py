"""
Πειραματική αλλαγή με δήλωση global tk μεταβλητές για χρήση σε φόρμες.

Η χρήση τους είναι λίγο επικίνδυνη λόγω import conflicts, partial initializations
και dependencies. Επίσης ο κώδικας είναι πολύ προχειρογραμμένος. Επειδή δουλεύει,
αν και χρειάστηκαν ραψίματα, το αφήνω όπως έχει προς το παρών.

Το βασικό πρόβλημα είναι ότι όλες οι tk μεταβλητές είναι εσωτερικά συνδεδεμένες
με το tcl runtime, οπότε δεν επιτρέπεται να αρχικοποιηθούν εκτός context.

Επίσης η __load δεν δουλεύει επειδή τρέχει σε διαφορετικό thread, άγνωστο στο tk.
Την αφήνω για λόγους ιστορικού μέχρι να σκεφτώ κάποιο καλύτερο τρόπο να εφαρμόσω
loading text χωρίς να πρέπει να προγραμματίσω κάθε component ξεχωριστά.

Εν ολίγης, για όποιον θέλει να χρησιμοποιήσει τα functions σε αυτό το module,
ο τρόπος είναι

Για απλή μεταφορά δεδομένων σε forms
>>> from rantevou.src.shared import set_appointment, ...
>>> from rantevou.src.model.entities import Appointment
>>> from datetime import datetime, timedelta
>>> appointment = Appointment(date=datetime.now(), duration=timedelta(minutes=20))
>>> set_appointment(appointment)

Για την κατασκευή forms
>>> import tkinter as tk
>>> root = tk.Tk() # Σημαντική η σειρά αν είναι σε νέο tk app.
>>> from rantevou.src.shared import from_appointment_year, ...
>>> entry = tk.Entry(root, textvariable=from_appointment_year)

"""

from time import sleep
from tkinter import StringVar, IntVar
from threading import Thread
from datetime import datetime, timedelta

from ..model.entities import Appointment, Customer
from ..controller import get_config

cfg = get_config()["view_settings"]
min_duration = cfg["minimum_appointment_duration"]


loading_text: StringVar = StringVar()


def __load():
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
__appointment_alerted: bool = False
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
    global __appointment_alerted
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
    __appointment_alerted = appointment.is_alerted

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
    global __appointment_alerted
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
        is_alerted=__appointment_alerted,
    )

    return appointment


def reset_appointment() -> None:
    """
    Επαναφέρει τα πεδία στα defaults (τωρινή ημερομηνία και ώρα)
    """
    global __appointment_id
    global __appointment_customer_id
    global __appointment_employee_id
    global __appointment_alerted
    global form_appointment_year
    global form_appointment_month
    global form_appointment_day
    global form_appointment_hour
    global form_appointment_minute
    global form_appointment_duration

    __appointment_id = None
    __appointment_customer_id = None
    __appointment_employee_id = None
    __appointment_alerted = False

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
