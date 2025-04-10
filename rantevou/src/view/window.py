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
from .customers import Customers
from .statistics import Statistics
from .alerts import Alerts

# standard colors

sbackground = "#313131"
sforeground = "#fcfcfc"
sfieldbackground = "lightblue"

# primary colors
pbackground = "lightblue"
pforeground = "#313131"
pfieldbackground = "#fcfcfc"
# secondary colors


class Notebook(ttk.Notebook):
    data: dict[str, Any] = {}


class Window(tk.Tk):

    def __init__(
        self, title: str = "Appointments App", width: int = 1100, height: int = 600
    ):
        super().__init__()
        self.geometry(f"{width}x{height}")
        self.title(title)
        self.tabs = Notebook(self)
        self.tabs.pack(fill="both", expand=True)
        self.tabs.add(AppointmentsTab(self.tabs), text="Appointments")
        self.tabs.add(Customers(self.tabs), text="Customers")
        self.tabs.add(Statistics(self.tabs), text="Statistics")
        self.tabs.add(Alerts(self.tabs), text="Alerts")

        style = ttk.Style(self)

        # standard

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

        # appointment sidepanel
