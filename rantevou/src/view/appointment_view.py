from __future__ import annotations

from tkinter import ttk
from datetime import datetime, timedelta

from . import abstract_views
from .sidepanel import SidePanel
from .exceptions import *

from ..model.entities import Appointment
from ..controller.logging import Logger


logger = Logger("appointment-view")


class AppointmentViewButton(ttk.Button):
    """
    Τα κουμπιά που εμφανίζονται στο sidepanel όταν ο χρήστης πατήσει
    σε κάποια περίοδο στο Grid.
    """

    appointment: Appointment

    def __init__(
        self,
        master,
        *args,
        **kwargs,
    ):
        super().__init__(master, *args, **kwargs)
        self.sidepanel: SidePanel = master.master.sidepanel

    def set(self, appointment: Appointment):
        """
        Καλείται από το sideview για να ενημερώσει τα στοιχεία του κουμπιού.
        """
        self.appointment = appointment
        if appointment.id:
            text = f"{appointment.date.strftime('%H:%M')}-{appointment.end_date.strftime('%H:%M')}"
            self.config(text=text, style="edit.TButton", command=self.edit_appointment)
        else:
            self.config(style="add.TButton")
            self.create_add_button()

    def create_add_button(self):
        """
        Αυτή η συνάρτηση είναι σχετική για τις περιόδους χωρίς κλεισμένο ραντεβού.
        Εμφανίζει τις κατάλληλες πληροφορίες στον χρήστη και αυτοκαταστρέφεται εάν
        έχει περάσει η ώρα και ημερομηνία της σχετικής περιόδου.

        Εδώ υπήρχε ένα πολύ περίεργο bug που μου πήρε κάποια ώρα να το εντοπίσω και
        ακόμα δημιουργεί artifacts. Φαίνεται πως το tkinter έχει κάποιο πρόβλημα να
        διαχειριστεί την καταστροφή του widget αμέσως μετά την δημιουργία του.

        Για αυτό τον σκοπό χρησιμοποιήθηκαν οι .after μέθοδοι που φαινομενικά λύνουν
        το πρόβλημα επειδή ξαναβάζουν το widget στο event loop.
        """
        date = self.appointment.date
        duration = self.appointment.duration
        end_date = self.appointment.end_date

        time_to_expire = end_date - datetime.now()
        if time_to_expire < timedelta(0):
            time_to_expire = timedelta(0)

        if end_date < datetime.now():
            self.after(0, self.destroy)
            return

        if duration == timedelta(0):
            self.after(0, self.destroy)
            return

        start = date.strftime("%H:%M")
        minutes = f"{int(duration.total_seconds() // 60)} λεπτά"

        self.config(
            text=f"{start}: {minutes}",
            command=self.add_appointment,
        )

    def add_appointment(self):
        self.sidepanel.select_view(
            "add",
            caller=self,
            caller_data=(self.appointment.date, self.appointment.duration),
        )

    def edit_appointment(self):
        self.sidepanel.select_view("edit", caller=self, caller_data=self.appointment)


class AppointmentView(abstract_views.SideView):
    """
    To View που εμφανίζεται στο sidepanel όταν ο χρήστης πάτησει
    σε κάποια περίοδο στο Grid.
    """

    name: str = "appointments"
    add_button: ttk.Button
    edit_button: ttk.Button
    caller_data: list[Appointment]

    def __init__(self, master: SidePanel, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.name = self.__class__.name
        self.sidepanel = master
        self.main_frame = ttk.Frame(self, style="primary.TFrame", borderwidth=3, relief="sunken")
        self.set_title("Ραντεβού")
        self.main_frame.pack(fill="both", expand=True)
        self.back_btn.config(command=master.go_back)

    def update_content(self, caller, caller_data):
        """
        Συνάρτηση που καλείται από το SidePanel στο click event. Η πολύπλοκη λογική
        είναι επειδή πρέπει να μετράει τα κουμπιά και να τα συγκρίνει με το πλήθος δεδομένων
        και να τα κατανέμει/επεξεργάζεται με τον πιο αποδοτικό τρόπο.

        Αυτή η βελτιστοποίηση προτιμήθηκε αντί απλής κατάστροφής των widget επειδή η
        δημιουργία κουμπιών είναι σχετικά αργή και φαινόταν άσχημα στο μάτι. Ακόμα και τώρα
        είναι πολύ εμφανές, ακόμα και όταν αλλάζει το πλήθος των κουμπιών κατα 1.
        """
        if not isinstance(caller_data, list):
            raise ViewWrongDataError(self, caller, caller_data)

        if len(caller_data) == 0:
            return

        if not isinstance(caller_data[0], Appointment):
            raise ViewWrongDataError(self, caller, caller_data[0])

        buttons: list[AppointmentViewButton] = []
        for widget in self.main_frame.children.values():
            if isinstance(widget, AppointmentViewButton):
                buttons.append(widget)

        app_len = len(caller_data)
        but_len = len(buttons)
        diff = app_len - but_len

        if diff > 0:
            for i in range(diff):
                AppointmentViewButton(self.main_frame).pack(fill="x")
        else:
            for _ in range(-diff):
                buttons.pop().destroy()

        buttons.clear()
        for widget in self.main_frame.children.values():
            if isinstance(widget, AppointmentViewButton):
                buttons.append(widget)

        for button, appointment in zip(buttons, caller_data, strict=True):
            button.set(appointment)
