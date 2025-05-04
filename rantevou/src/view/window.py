"""
Ορίζει το κεντρικό (top level) παράθυρο της εφαρμογής πάνω στο οποίο υπάρχουν όλα
τα σχετικά widgets της εφαρμογής.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any
from .appointments import AppointmentsTab
from .customers import CustomersTab
from .statistics import Statistics
from .sidepanel import SidePanel, SearchBar
from ..controller import get_config

from .alerts import AlertsView
from .appointment_managment import EditAppointmentView, AddAppointmentView
from .appointment_search import SearchResultsView
from .appointment_view import AppointmentView
from .customer_managment import AddCustomerView, EditCustomerView

cfg = get_config()

color1 = cfg["color_pallete"]["background"]
color2 = cfg["color_pallete"]["foreground"]
color3 = cfg["color_pallete"]["fieldbackground"]

# standard colors
sbackground = color1
sforeground = color2
sfieldbackground = color3

# primary colors
pbackground = color3
pforeground = color1
pfieldbackground = color2


class Notebook(ttk.Notebook):
    """
    Ένα state object στην περίπτωση που χρειαστεί στο μέλλον
    """

    data: dict[str, Any] = {}


def create_window() -> Window:
    """
    Window factory για να μην μπλέκονται τα imports με τις αρχικοποιήσεις
    """
    return Window()


class Window(tk.Tk):
    """
    To top level παράθυρο. Αποτελείται από το main panel με tabs, το sidepanel που δείχνει διαχειριστικές
    ενέργειες και λεπτομερείς πληροφορίες, και το search bar που ψάχνει για κενά ραντεβού.
    """

    def __init__(self, title: str = "Appointments App", width: int = 1400, height: int = 600):
        super().__init__()

        # Βασικές αρχικοποιήσεις
        self.geometry(f"{width}x{height}")
        self.config(background=sbackground)
        self.style_config()
        self.title(title)

        # Αρχικοποιήσεις των κεντρικών widget
        self.tabs = Notebook(self)
        self.side_panel = SidePanel(self)
        self.search_bar = SearchBar(self)

        self.tabs.add(AppointmentsTab(self.tabs), text="Appointments")
        self.tabs.add(CustomersTab(self.tabs), text="Customers")
        self.tabs.add(Statistics(self.tabs), text="Statistics")

        # Η register_view είναι παρόμοια της .add με λίγη έξτρα λογική.
        self.side_panel.register_view(AlertsView(self.side_panel), "alerts")
        self.side_panel.register_view(EditAppointmentView(self.side_panel), "edit")
        self.side_panel.register_view(AppointmentView(self.side_panel), "appointments")
        self.side_panel.register_view(AddAppointmentView(self.side_panel), "add")
        self.side_panel.register_view(SearchResultsView(self.side_panel), "search")
        self.side_panel.register_view(AddCustomerView(self.side_panel), "addc")
        self.side_panel.register_view(EditCustomerView(self.side_panel), "editc")
        # TODO εδώ προσθέτουμε το καινούριο CustomerView, προτινεται το όνομα "customer"
        self.side_panel.select_view("alerts")

        # Δήλωση διαστάσεων και τοποθέτηση των widget
        for i in range(2):
            self.rowconfigure(0, weight=1)
        for i in range(4):
            self.columnconfigure(0, weight=1)

        self.tabs.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=10)
        self.side_panel.grid(row=0, column=1, sticky="nse", padx=10)
        self.search_bar.grid(row=1, column=1, sticky="se", padx=10)
        self.config(padx=10, pady=20)

        # Κάνει τα F-keys να αλλάζουν το tab. Πρόχειρη υλοποίηση. Μπορεί να βελτιωθεί.
        self.bind_all(
            "<Key>",
            lambda x: (self.tabs.select(int(x.keysym[1:]) - 1) if x.keysym.startswith("F") else None),
        )

    def style_config(self):

        # Standard
        style = ttk.Style(self)
        style.theme_use("alt")
        style.configure(
            "TButton",
            background=sbackground,
            foreground=sforeground,
        )
        style.configure(
            "TLabel",
            background=sbackground,
            foreground=sforeground,
        )
        style.configure(
            "TFrame",
            background=sbackground,
        )

        # Tabs
        style.configure(
            "TNotebook",
            background=sbackground,
        )
        style.configure(
            "TNotebook.Tab",
            background=sforeground,
            foreground=sbackground,
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", "lightblue")],
            foreground=[("selected", "black")],
        )
        style.configure(
            "TEntry",
            fieldbackground=sfieldbackground,
        )
        style.configure(
            "Treeview.Heading",
            background=sbackground,
            foreground=sforeground,
        )

        # Customer sheet
        style.configure(
            "Treeview",
            background=sbackground,
            foreground=sforeground,
            fieldbackground=sbackground,
        )

        style.configure(
            "Vertical.TScrollbar",
            background=sbackground,
            bordercolor=sbackground,
            troughcolor=sfieldbackground,
            arrowcolor="white",
        )

        # Appointment grid
        style.configure(
            "primary.TButton",
            background=pbackground,
            foreground=pforeground,
        )
        style.configure(
            "primary.TLabel",
            background=pbackground,
            foreground=pforeground,
        )
        style.configure(
            "primary.TFrame",
            background=pbackground,
        )

        # Buttons
        style.configure(
            "low.TLabel",
            background=cfg["buttons"]["low"],
        )
        style.configure(
            "medium.TLabel",
            background=cfg["buttons"]["medium"],
        )
        style.configure(
            "high.TLabel",
            background=cfg["buttons"]["high"],
        )
        style.configure(
            "max.TLabel",
            background=cfg["buttons"]["max"],
        )
        style.configure(
            "low.TButton",
            background=cfg["buttons"]["low"],
        )
        style.configure(
            "medium.TButton",
            background=cfg["buttons"]["medium"],
        )
        style.configure(
            "high.TButton",
            background=cfg["buttons"]["high"],
        )
        style.configure(
            "max.TButton",
            background=cfg["buttons"]["max"],
        )
        style.configure(
            "edit.TButton",
            background=cfg["buttons"]["max"],
        )
        style.configure(
            "add.TButton",
            background=cfg["buttons"]["medium"],
        )

        # Sidepanel
        style.layout("side.TNotebook.Tab", [])
