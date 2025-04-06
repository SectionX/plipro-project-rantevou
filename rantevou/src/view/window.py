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
from collections import OrderedDict


class Window(tk.Tk):

    def __init__(self, title="Appointments App", width=800, height=600):
        super().__init__()
        self.geometry(f"{width}x{height}")
        self.title(title)
        self.AppContext = {}

    def initialize(self) -> None:
        """
        Συνδέει τα appframes στο overview το ορίζει ως αρχικό panel
        """
        self.children["!overview"].initialize()  # type: ignore
        self.windowframe = self.children["!overview"]
        self.windowframe.pack(fill="both", expand=True)

    def change_frame(self, frame_name) -> None:
        """
        Αλλάζει το ενεργό frame στο παράθυρο. Χρησιμοποείται από το widget
        GoToButton στο views/navigation.py
        """
        self.windowframe.forget()
        self.windowframe = self.children[f"!{frame_name}"]
        self.windowframe.pack(fill="both", expand=True)

    def run(self) -> None:
        """
        Εκκίνηση της tkinter εφαρμογής. Δημιουργεί την γραφική
        επιφάνεια και την αποδευσμέυει όταν τελειώσει.
        """
        self.mainloop()
