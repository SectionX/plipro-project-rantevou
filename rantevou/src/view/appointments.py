"""
appointments.py - Γραφικό περιβάλλον εμφάνισης, δημιουργίας και επεξεργασίας
                  των ραντεβού

Class Appointments - Το App Frame που εμπεριέχει όλη την λογική του γραφικού
                     περιβάλλοντος

Class AppointmentGroup - Για την καλύτερη εμφάνιση των στοιχείων, χωρίζουμε το
                         ωράριο λειτουργίας σε υποπεριόδους. Εμφανίζονται στον
                         χρήστη ώς ένα grid κουμπιών και το χρώμα τους υποδηλώνει
                         την πληρότητα της περιόδου σε ραντεβού

Class Appointment - Το widget που εμπεριέχει τα στοιχεία του ραντεβού,
"""

from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk
from .abstract_views import AppFrame
from ..model.types import Appointment, Customer
from ..controller.appointments_controller import AppointmentControl
from ..controller.customers_controller import CustomerControl

# for simulation purposes
import random

WEEK_DAYS = [
    "Sunday",
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
]

# TODO αυτά τα στοιχεία μπήκαν εδώ για διευκόλυνση της υλοποίησης αλλά θα
# πρέπει να σβηστούν και να μεταφερθούν στον controller. Επίσης θα πρέπει να
# διαβάζονται από ενα configuration file και να μην είναι σαν σταθερές στον
# κώδικα. Διορθώνοντας την λογική θα πρέπει να διορθωθούν και όλα τα class/methods
# που τα χρησιμοποιούν.
WORKING_HOURS = 8
OFFSET = 9
APPOINTMENT_LENGTH = 20


class AppointmentButton:
    """
    Superclass για όλα τα widgets του appointment App Frame. Κάθε
    ένα subclass θα πρέπει να υλοποιεί την συνάρτηση update_info και
    να ενημερώνει τα στοιχεία του με τα δεδομένα που βρίσκει στις μεταβλητές

    AppointmentButton.appointment_data
    AppointmentButton.customer_data
    """

    appointment_data: list[Appointment] = []
    customer_data: list[Customer] = []
    appointment_control = AppointmentControl()
    customer_control = CustomerControl()

    @classmethod
    def get_data_from_db(cls):
        """
        Σκοπός της μεθόδου είναι να επικοινωνήσει με τον controller
        και να λάβει στοιχεία από την βάση δεδομένων, αποθηκεύοντας
        τα ως Class Attribute. Αυτό ειναι σημαντικό, γιατί τα Class
        Attributes είναι κοινά σε όλα τα αντικείμενα που κληρονομούν
        από αυτό το Class
        """
        cls.appointment_data = cls.appointment_control.get_appointments()
        cls.customer_data = cls.customer_control.get_customers()

    def update_info(self):
        """
        Σκοπός της μεθόδου είναι να λαμβάνει τις απαραίτητες πληροφορίες
        απο την βάση δεδομένων και να αλλάζει τα χαρακτηριστικά της ανάλογα.
        """


class AppointmentGroup(tk.Button, AppointmentButton):

    # 5 levels from green to red
    color_grading = ["#FFFFFF", "#00FF00", "#00FF7F", "#FFFF00", "#FF7F00", "#FF0000"]

    def __init__(
        self, master, zero_day, day, hours, minutes, period_length, *args, **kwargs
    ):
        tk.Button.__init__(self, master, *args, **kwargs)
        self.appointment_control = AppointmentControl()
        self.config(bg="#f0f0f0", fg="#000000", activebackground="#f0f0f0")

        self.zero_day: datetime = zero_day
        self.period_start: datetime = self.zero_day + timedelta(
            days=day, hours=hours, minutes=minutes
        )
        self.period_end: datetime = self.period_start + timedelta(minutes=period_length)

        self.time_str = (
            f"{self.period_start.strftime('%H:%M')}-{self.period_end.strftime('%H:%M')}"
        )
        self["text"] = f"{self.time_str}"

        self.capacity = 6  # TODO make it dynamic

    def update_info(self):
        print("updating")
        appointments = random.randint(0, (2 * 60) // 20)
        self.config(bg=self.color_grading[appointments - 1])
        self.config(text=f"{appointments}/{self.capacity}\n" + self["text"])


class SingleAppointment(tk.Button, AppointmentButton):
    def __init__(self, master, *args, **kwargs):
        tk.Button.__init__(self, master, *args, **kwargs)
        self.appointment_control = AppointmentControl()
        self.customer_control = CustomerControl()
        self.config(bg="#f0f0f0", fg="#000000", activebackground="#f0f0f0")
        self.config(command=self.show_customer_data)

    def update_info(self):
        """
        Η συνάρτηση θα τρέχει την στιγμή δημιουργίας του widget και
        θα προσθέτει στο self["text"] σε μορφή

        *Όνομα Πελάτη* - *ωρα σε ΩΩ/ΛΛ*

        Να παίρνει στοιχεία από το Appointment.appointment_data και
        Appointment.customer_data
        """
        # TODO

    def show_customer_data(self):
        """
        Συνάρτηση που θα δημιουργεί ένα pop up με τα στοιχεία
        του πελάτη που σχετίζεται με το ραντεβού

        Όνομα, Επίθετο, Τηλέφωνο, Email και ένα κουμπί
        που αν πατηθεί στέλνει email.

        Να παίρνει στοιχεία από τις πληροφορίες που διαβάζει η
        update_info
        """
        popup = tk.Toplevel(self)
        # TODO
        popup.mainloop()


class Appointments(AppFrame):
    def __init__(self, root):
        super().__init__(root)
        self.zero_day = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        self.initialize_columns()

    def update_info(self):
        """
        H συνάρτηση ζητάει από όλα τα παιδιά της να ενημερώσουν
        τα στοιχεία τους τρέχοντας την δική τους μέθοδο update_info()

        Η find_children είναι ήδη υλοποιημένη στο AppFrame Class
        """
        children = self.get_all_children(self)
        for child in children:
            child.update_info()

    def initialize_one_header(self, day):
        self.day_header = tk.Label(
            self.appointment_slots_column, text=WEEK_DAYS[day % 7]
        )
        self.pack(side=tk.TOP, fill="both", expand=True)
        self.date_header = tk.Label(
            self.appointment_slots_column,
            height=2,
            text=self.zero_day.strftime("%d/%m"),
        )
        self.date_header.pack(side=tk.TOP, fill="both", expand=True)

    def initialize_one_appointmentgroup(
        self, zero_day, day, hours, minutes, period_length
    ):
        period_widget = AppointmentGroup(
            self.appointment_slots_column,
            zero_day,
            day,
            hours,
            minutes,
            period_length,
            command=lambda: self.create_appointment_group_popup("group"),
        )
        period_widget.pack(side=tk.TOP, fill="both", expand=True)

    def initialize_one_appointmentgroup_column(self, day_index):
        self.initialize_one_header(day_index)
        for i in range(0, self.working_minutes, self.period):
            self.initialize_one_appointmentgroup(
                self.zero_day,
                day_index,
                hours=i // 60 + OFFSET,
                minutes=i % 60,
                period_length=self.period,
            )

    def initialize_columns(self):
        self.working_minutes = WORKING_HOURS * 60
        self.period = self.working_minutes // 4

        for day_index, day_name in enumerate(WEEK_DAYS):
            self.appointment_slots_column = tk.Frame(self)
            self.appointment_slots_column.pack(side=tk.LEFT, fill="both", expand=True)
            self.initialize_one_appointmentgroup_column(day_index)

    def create_appointment_group_popup(self, appointment_group):
        AppointmentButton.get_data_from_db()
        group = tk.Toplevel()
        group.geometry("250x400")
        group.title("Appointments")
        for i in range(self.period // APPOINTMENT_LENGTH):
            appointment = SingleAppointment(group)
            appointment.update_info()
            appointment.pack(side=tk.TOP, fill="both", expand=True)

        group.mainloop()
