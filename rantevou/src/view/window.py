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
from .appointments import Appointments
from .customers import Customers
from .statistics import Statistics
from .alerts import Alerts


class Window(tk.Tk):

    def __init__(self, title="Appointments App", width=800, height=600):
        super().__init__()
        self.geometry(f"{width}x{height}")
        self.title(title)
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill="both", expand=True)
        self.tabs.add(Appointments(self.tabs), text="Appointments")
        self.tabs.add(Customers(self.tabs), text="Customers")
        self.tabs.add(Statistics(self.tabs), text="Statistics")
        self.tabs.add(Alerts(self.tabs), text="Alerts")
