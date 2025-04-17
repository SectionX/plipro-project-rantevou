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

from typing import Any, Protocol, runtime_checkable
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror
from collections import deque
from datetime import datetime, timedelta
from .abstract_views import SideView, Caller

from ..controller import get_config
from ..controller.logging import Logger
from ..controller.mailer import Mailer
from ..controller.appointments_controller import AppointmentControl
from ..controller.customers_controller import CustomerControl


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


class SidePanel(ttk.Notebook):

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
        self.views[name] = (widget, self.view_index)
        self.add(widget)
        self.view_index += 1

    def get_index(self, name: str):
        return self.views[name][1]

    def get_view(self, name: str):
        return self.views[name][0]

    def select_view(
        self, name: str, caller: Any | None = None, caller_data: Any | None = None
    ):
        self.active_view = self.get_view(name)
        self.active_view.update_content(caller, caller_data)
        self.select(self.get_index(name))
        if isinstance(caller, Caller) and not self.back:
            self.caller_stack.append(caller)
            self.back = False

    def go_back(self):
        self.back = True
        if len(self.caller_stack) == 0:
            self.select_view("alerts")
            return
        caller = self.caller_stack.pop()
        caller.show_in_sidepanel()


# class SidePanel(ttk.Frame):
#     """
#     Η βασική οντότητα. Σημαντικό χαρακτηριστικό ότι είναι φτιαγμένη
#     ώστε να είναι μοναδική (singleton pattern) και διαχειρίζεται
#     global state ώστε να μπορούν όλα τα υπόλοιπα αντικείμενα να
#     επικοινωνούν σωστά.

#     Βασικές μέθοδοι:
#     SidePanel.instance() -> Επιστρέφει το ένα και μοναδικό αντικείμενο
#     SidePanel.select_vew() -> API που επιτρέπει στα άλλα αντικείμενα να
#                                 ζητούν αλλαγή του panel
#     SidePanel.update_data() -> API που επιτρέπει στα άλλα αντικείμενα να
#                                 στέλνουν πληροφορίες
#     SidePanel.fetch_data() -> API που επιτρέπει στα άλλα αντικείμενα να
#                                 λάβουν τις αποθηκευμένες πληροφορίες

#     Παράδειγμα, όταν πατάμε ένα κελί στο grid των ραντεβού, ζητάμε από το
#     SidePanel να μας εμφανίσει το panel διαχείρησης αυτού του κελιού με τον
#     εξής τρόπο

#     SidePanel.select_view("appointments", caller=self, data=...)

#     Όπου caller είναι το κελί, και data είναι τα ραντεβού που διαχειρίζεται
#     το συγκεκριμένο κελί.

#     Το SidePanel αποθηκεύει αυτά τα δεδομένα ως "caller":self, και
#     "caller_data": ..., ώστε να μπορεί να εμφανίζει σχετικές πληροφορίες
#     που αφορούν αυτό το κελί
#     """

#     _instance = None
#     side_views: dict[str, SideView]  # search, previous_view
#     search_bar: SearchBar
#     active_view: SideView
#     data_pipeline: dict[str, Any] = {}

#     def __init__(self, root, *args, **kwargs):
#         super().__init__(root, *args, **kwargs)
#         SidePanel.update_data("self", self)
#         self.side_views = {
#             "alert": AlertsView(self),
#             "appointments": AppointmentView(self),
#             "search": SearchResultsView(self),
#             "edit": EditAppointmentView(self),
#             "add": AddAppointmentView(self),
#             "addc": AddCustomerView(self),
#             "editc": EditCustomerView(self),
#         }
#         self.active_view = self.side_views["alert"]
#         self.search_bar = SearchBar(self)
#         self.search_bar.pack(side=tk.BOTTOM, fill="x")
#         self.caller_stack: deque[Caller] = deque(maxlen=10)
#         self._select_view()

#     def _return(self):
#         caller = self.caller_stack.pop()
#         caller.show_in_sidepanel()

#     def _select_view(self, view: str | None = None, caller=None, data=None):
#         if isinstance(caller, Caller):
#             self.caller_stack.append(caller)

#         if caller == SidePanel.fetch_data("caller"):
#             SidePanel.update_data("caller_data", data)
#             self.active_view.update_content()

#         SidePanel.update_data("previous_view", self.active_view.name)
#         SidePanel.update_data("previous_caller", SidePanel.fetch_data("caller"))
#         SidePanel.update_data(
#             "previous_caller_data", SidePanel.fetch_data("caller_data")
#         )
#         SidePanel.update_data("caller", caller)
#         SidePanel.update_data("caller_data", data)

#         self.active_view.forget()
#         if view is None:
#             view = "alert"
#         self.active_view = self.side_views[view]
#         self.active_view.pack(side=tk.TOP, fill="both", expand=True)
#         self.active_view.update_content()

#     @classmethod
#     def update_data(cls, key, value):
#         cls.data_pipeline[key] = value

#     @classmethod
#     def fetch_data(cls, key) -> None | Any:
#         return cls.data_pipeline.get(key)

#     @classmethod
#     def select_view(cls, view: str | None = None, caller=None, data=None):
#         self = SidePanel.instance()
#         if self is None:
#             logger.log_warn("SidePanel instance failed to initialize")
#             return
#         self._select_view(view, caller, data)

#     @classmethod
#     def instance(cls) -> SidePanel | None:
#         return SidePanel.data_pipeline.get("self")

#     @classmethod
#     def get_active_view(cls):
#         sidepanel = cls.instance()
#         if sidepanel is None:
#             logger.log_error("Failed to fetch sidepanel instance")
#             return None
#         return sidepanel.active_view

#     @classmethod
#     def go_back(cls):
#         instance = SidePanel.instance()
#         if instance is None:
#             raise Exception("Failure to initialize SidePanel")
#         instance._return()


class SearchBar(ttk.Frame):
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

    def search(self):
        user_input: timedelta | str = self.entry.get()

        if isinstance(user_input, str):
            if user_input.isdigit():
                user_input = timedelta(minutes=int(user_input))
            else:
                user_input = timedelta(0)

        self.duration = user_input
        self.search_results = ac.get_time_between_appointments(
            minumum_free_period=self.duration
        )
        self.sidepanel.select_view(
            "search", caller=self, caller_data=(self.search_results, self.duration)
        )
