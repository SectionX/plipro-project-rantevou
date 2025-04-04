import tkinter as tk
from .navigation import GoToButton
from .window import Window
from .abstract_views import AppFrame


class Overview(tk.Frame):
    def __init__(self, root: Window):
        tk.Frame.__init__(self, root)
        self.root = root
        self.name = "overview"

    def initialize(self, frame_names: list[str]) -> None:
        """
        Αρχικοποιεί το overview δημιουργόντας τα κουμπιά
        πλοήγησης.
        """
        buttons = [
            GoToButton(self, name.title(), self.root, name)
            for name in frame_names
            if name != "overview"
        ]

        # Σετάρει τα grids ώστε να γεμίζουν όλο τον χώρο
        for i in range(0, 2):
            for j in range(0, 2):
                self.grid_columnconfigure(i, weight=1)
                self.grid_rowconfigure(j, weight=1)

        # Σετάρει τα κουμπια στο grid και αλλάζει την γεωμετρία τους
        # ώστε να γεμίζουν όλο τον χώρο
        buttons[0].grid(row=0, column=0, sticky="nsew")
        buttons[1].grid(row=0, column=1, sticky="nsew")
        buttons[2].grid(row=1, column=0, stick="nsew")
        buttons[3].grid(row=1, column=1, sticky="nsew")
