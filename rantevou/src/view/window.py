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
from .appointments import Appointments
from .customers import Customers
from .statistics import Statistics
from .alerts import Alerts


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
        self.tabs.add(Appointments(self.tabs), text="Appointments")
        self.tabs.add(Customers(self.tabs), text="Customers")
        self.tabs.add(Statistics(self.tabs), text="Statistics")
        self.tabs.add(Alerts(self.tabs), text="Alerts")

        style = ttk.Style(self)
        style.theme_use("alt")
        style.configure(
            "TLabel", background="lightyellow", foreground="brown", font=("Arial", 12)
        )
        style.configure(
            "TButton", background="lightblue", foreground="black", font=("Arial", 10)
        )
        style.configure(
            "TEntry", fieldbackground="white", foreground="black", font=("Arial", 10)
        )
        style.configure(
            "TNotebook",
            background="lightyellow",
            foreground="brown",
            font=("Arial", 12),
        )
        style.configure(
            "TTreeview", fieldbackground="white", foreground="black", font=("Arial", 10)
        )
        style.configure("TFrame", background="lightgrey")
        style.configure(
            "TFrame",
            background="lightyellow",
            foreground="brown",
            font=("Arial", 12),
        )
        style.configure(
            "TNotebook.tab",
            background="lightyellow",
            foreground="brown",
            font=("Arial", 12),
        )
