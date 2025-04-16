"""
Ορίζει το κεντρικό παράθυρο της εφαρμογής πάνω στο οποίο υπάρχουν όλα
τα σχετικά frames της εφαρμογής (με frame εννοούμε τα παράθυρα που αφορούν
την κάθε ξεχωριστή λειτουργία της εφαρμογής)

Η "αρχική σελίδα" της εφαρμογής είναι η Overview, όπως ορίζεται στο views/overview.py
και φέρει κουμπιά που καλούν τα συγκεκριμένα frames. Πχ το κουμπί "Appointments"
ανοίγει το frame της εφαρμογής "Appointments". Το πρόγραμμα την αναγνωρίζει και
την διαχειρίζεται αυτόματα.
"""

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
    data: dict[str, Any] = {}


class Window(tk.Tk):

    def __init__(
        self, title: str = "Appointments App", width: int = 1400, height: int = 600
    ):
        super().__init__()
        self.geometry(f"{width}x{height}")
        self.config(background=sbackground)
        self.style_config()
        self.title(title)
        self.tabs = Notebook(self)
        self.side_panel = SidePanel(self, width=250)
        self.search_bar = SearchBar(self)

        self.tabs.add(AppointmentsTab(self.tabs), text="Appointments")
        self.tabs.add(CustomersTab(self.tabs), text="Customers")
        self.tabs.add(Statistics(self.tabs), text="Statistics")

        # Κάνει τα F-keys να αλλάζουν το tab. Πρόχειρη υλοποίηση. Μπορεί να βελτιωθεί
        # δραστικά.
        self.bind_all(
            "<Key>",
            lambda x: (
                self.tabs.select(int(x.keysym[1:]) - 1)
                if x.keysym.startswith("F")
                else None
            ),
        )

        self.side_panel.register_view(AlertsView(self.side_panel), "alerts")
        self.side_panel.register_view(EditAppointmentView(self.side_panel), "edit")
        self.side_panel.register_view(AppointmentView(self.side_panel), "appointments")
        self.side_panel.register_view(AddAppointmentView(self.side_panel), "add")
        self.side_panel.register_view(SearchResultsView(self.side_panel), "search")
        self.side_panel.register_view(AddCustomerView(self.side_panel), "addc")
        self.side_panel.register_view(EditCustomerView(self.side_panel), "editc")
        # TODO εδώ προσθέτουμε το καινούριο CustomerView, προτινεται το όνομα "customer"
        self.side_panel.select_view("alerts")

        self.grid_rowconfigure(0, weight=4)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2, minsize=250)

        self.tabs.grid(column=0, row=0, rowspan=2, sticky="nsew")
        self.side_panel.grid(column=1, row=0, stick="nse", pady=10, padx=5)
        self.search_bar.grid(column=1, row=1, stick="nse", pady=10, padx=10)

    def style_config(self):
        # standard

        style = ttk.Style(self)
        style.theme_use("alt")
        style.configure("TButton", background=sbackground, foreground=sforeground)
        style.configure("TLabel", background=sbackground, foreground=sforeground)
        style.configure("TFrame", background=sbackground)
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
        style.configure("TEntry", fieldbackground=sfieldbackground)
        style.configure(
            "Treeview.Heading", background=sbackground, foreground=sforeground
        )
        style.configure("Treeview", background=sbackground, foreground=sforeground)

        # appointment grid
        style.configure(
            "primary.TButton", background=pbackground, foreground=pforeground
        )
        style.configure(
            "primary.TLabel", background=pbackground, foreground=pforeground
        )
        style.configure("primary.TFrame", background=pbackground)

        # buttons

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
        style.configure("edit.TButton", background=cfg["buttons"]["max"])
        style.configure("add.TButton", background=cfg["buttons"]["medium"])

        style.configure("placeholder.TEntry", foreground="red")

        style.layout("side.TNotebook.Tab", [])
