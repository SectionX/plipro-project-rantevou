"""
Ορίζει το πλάγιο πάνελ με την μπάρα αναζήτησης.
"""

from __future__ import annotations

from typing import Any
import tkinter as tk
from tkinter import ttk
from collections import deque
from datetime import datetime, timedelta
from .abstract_views import SideView, Caller

from ..controller import get_config
from ..controller.logging import Logger
from ..controller.mailer import Mailer
from ..controller.appointments_controller import AppointmentControl


cfg = get_config()
mailer = Mailer()
logger = Logger("sidepanel")


class SidePanel(ttk.Notebook):
    """
    Το κεντρικό widget που διαχειρίζεται όλα τα side views. Οι δυο βασικές μέθοδοι
    είναι η register_view με την οποία δηλώνουμε όλα τα sideviews, και η select_view
    που είναι το API που επιτρέπει την επικοινωνία, μεταφέρει δεδομένα και αλλάζει
    τα sideviews ανάλογα με τις ανάγκες της καλούσας.
    """

    _instance = None
    views: dict[str, tuple[SideView, int]]
    view_index: int
    caller_stack: deque[Caller]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.views = {}
        self.config(style="side.TNotebook")
        self.view_index = 0
        self.caller_stack = deque(maxlen=10)
        self.back = False
        self.active_view: SideView

    def register_view(self, widget: SideView, name: str):
        """
        Τα widgets που δηλώνονται εδώ συνήσταται ή να κληρονομούν απο abstract_views.SideView
        ή να εφαρμόζουν την διεπαφή του (δηλαδή την μέθοδο .update_content)
        """
        self.views[name] = (widget, self.view_index)
        self.add(widget)
        self.view_index += 1

    def get_index(self, name: str):
        return self.views[name][1]

    def get_view(self, name: str):
        return self.views[name][0]

    def select_view(self, name: str, caller: Any | None = None, caller_data: Any | None = None):
        """
        Το API αλλαγής παραθύρων.

        * name - Το όνομα του sideview που θέλει να εμφανίσει η καλούσα
        * caller - Το αντικείμενο που καλει την select_view, προτίνεται να περαστεί ως self
        * caller_data - Τα δεδομένα που θέλει να περάσει η καλούσα στο sideview

        Σημαντικό τα caller_data να γίνονται validate από το καλώμενο SideView επειδή είναι
        αδύνατο να ορίσουμε τον τύπο τους.
        """
        self.active_view = self.get_view(name)
        self.active_view.update_content(caller, caller_data)
        self.select(self.get_index(name))
        if isinstance(caller, Caller) and not self.back:
            self.caller_stack.append(caller)
            self.back = False

    def go_back(self):
        """
        Λογική για backtracking. Πρόχειρα υλοποιημένη.
        """
        self.back = True
        if len(self.caller_stack) == 0:
            self.select_view("alerts")
            return
        caller = self.caller_stack.pop()
        caller.show_in_sidepanel()


class SearchBar(ttk.Frame):
    """
    Μπάρα αναζήτησης χρόνου μεταξύ ραντεβού. Χρειάζονται να υπάρχουν τουλάχιστον 2
    ραντεβού για να δουλέψει σωστά. Είναι χρήσιμη στην περίπτωση που ο χρήστης θέλει
    να βρεί ένα ορισμένο κενό χρόνο σε μια περίοδο με πολλά κλεισμένα ραντεβού.
    """

    label: ttk.Label
    entry: ttk.Entry
    button: ttk.Button
    duration: timedelta
    search_results: list[tuple[datetime, timedelta]]
    sidepanel: SidePanel

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.sidepanel = self.nametowidget(".!sidepanel")
        self.inputframe = ttk.Frame(self)
        self.label = ttk.Label(self.inputframe, text="Διάρκεια")
        self.entry = ttk.Entry(self.inputframe)
        self.button = ttk.Button(self, text="Εύρεση κενού χρόνου", command=self.search)
        self.label.pack(side=tk.LEFT)
        self.entry.pack(side=tk.RIGHT)
        self.inputframe.pack(side=tk.TOP, fill="x", expand=True)
        self.button.pack(side=tk.BOTTOM, fill="x")

        self.entry.bind("<Key>", lambda x: x.keysym == "Return" and self.search())

    def search(self):
        """
        Λαμβάνει τα δεδομένα από το μοντέλο και τα στέλνει στο SideView με όνομα "search"
        για να εμφανιστούν.

        Η .get_time_between_appointments είναι σχετικά αργή και χρήζει βελτίωσης, κυρίως
        να μεταφερθεί η αναζήτηση κατευθείαν στην βάση δεδομένων.
        """
        user_input: timedelta | str = self.entry.get()

        if isinstance(user_input, str):
            if user_input.isdigit():
                user_input = timedelta(minutes=int(user_input))
            else:
                user_input = timedelta(0)

        self.duration = user_input
        self.search_results = AppointmentControl().get_time_between_appointments(
            end_date=datetime.now() + timedelta(days=30), minumum_free_period=self.duration
        )
        self.sidepanel.select_view("search", caller=self, caller_data=(self.search_results, self.duration))
