from datetime import datetime, timedelta, date, time
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
WORKING_HOURS = 8
OFFSET = 9
APPOINTMENT_LENGTH = 20


def find_children(root):
    target = []
    stack = [root]
    while stack:
        child = stack.pop()
        if isinstance(child, AppointmentButton):
            target.append(child)
        stack.extend(child.winfo_children())

    return target


class AppointmentButton:
    """
    Ο σκοπός αυτού του άδειου class είναι να λειτουργήσει σαν
    φίλτρο. Έτσι μπορούμε σε μια λίστα από tk Widgets να πουμε
    filter(lambda x: isinstance(x, AppointmentButton), list_of_widgets).

    Θεωρώ ότι είναι πιο καθαρό από τους getters του tk.
    """

    appointment_data: list[Appointment] = []
    customer_data: list[Customer] = []
    appointment_control = AppointmentControl()
    customer_control = CustomerControl()

    @classmethod
    def update_data(cls):
        """
        Σκοπός της μεθόδου είναι να επικοινωνήσει με τον controller
        και να λάβει στοιχεία από την βάση δεδομένων, αποθηκεύοντας
        τα ως Class Attribute. Αυτό ειναι σημαντικό, γιατί τα Class
        Attributes είναι κοινά σε όλα τα αντικείμενα που κληρονομούν.
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
        self.date_str = date.strftime(zero_day + timedelta(days=day), "%d/%m")
        self.time_str = (
            f"{hours}:{minutes:02d}-{hours + period_length//60}:{minutes:02d}"
        )
        self["text"] = f"{self.date_str}\n{self.time_str}"

        self.capacity = 6  # TODO make it dynamic

    def update_info(self):
        print("updating")
        appointments = random.randint(0, (2 * 60) // 20)
        self.config(bg=self.color_grading[appointments - 1])
        self.config(text=f"{appointments}/{self.capacity}\n" + self["text"])


class Appointment(tk.Button, AppointmentButton):
    def __init__(self, master, *args, **kwargs):
        tk.Button.__init__(self, master, *args, **kwargs)
        self.appointment_control = AppointmentControl()
        self.customer_control = CustomerControl()
        self.config(bg="#f0f0f0", fg="#000000", activebackground="#f0f0f0")

    def update_info(self):
        pass


class Appointments(AppFrame):
    def __init__(self, root, name="appointments"):
        super().__init__(root, name)
        self.zero_day = date.today()

        self.initialize_appointment_slots_column()
        self.initialize()
        self.__simulate()

    def __simulate(self):
        print("simulating")
        children = find_children(self.body)
        for child in children:
            child.update_info()

    def initialize_one_header(self, day):
        self.day_header = tk.Label(
            self.appointment_slots_column, height=2, text=WEEK_DAYS[day % 7]
        )
        self.pack(side=tk.TOP, fill="both", expand=True)

    def initialize_one_period(self, zero_day, day, hours, minutes, period_length):
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

    def initialize_appointment_slots_column(self):
        self.working_minutes = WORKING_HOURS * 60
        self.period = self.working_minutes // 4

        for day_index, day_name in enumerate(WEEK_DAYS):
            self.appointment_slots_column = tk.Frame(self.body)
            self.initialize_one_header(day_index)

            for i in range(0, self.working_minutes, self.period):
                hours = i // 60 + OFFSET
                minutes = i % 60
                self.initialize_one_period(
                    self.zero_day, day_index, hours, minutes, self.period
                )

            self.appointment_slots_column.pack(side=tk.LEFT, fill="both", expand=True)

    def create_appointment_group_popup(self, appointment_group):
        AppointmentGroup.update_data()
        group = tk.Toplevel()
        group.geometry("250x400")
        group.title("Appointments")
        for i in range(self.period // APPOINTMENT_LENGTH):
            appointment = Appointment(group)
            appointment.update_data()
            appointment.pack(side=tk.TOP, fill="both", expand=True)

        group.mainloop()
