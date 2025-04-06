import tkinter as tk
from .navigation import GoToButton
from .window import Window
from .abstract_views import AppFrame


class Overview(tk.Frame):
    def __init__(self, root: Window):
        tk.Frame.__init__(self, root)
        self.root = root
        self.AppContext = root.AppContext
        self.name = "overview"

    def initialize(self) -> None:
        """
        Αρχικοποιεί το overview δημιουργόντας τα κουμπιά
        πλοήγησης.
        """
        appframes = filter(
            lambda x: isinstance(x, AppFrame), self.root.winfo_children()
        )

        buttons = [
            GoToButton(self, frame.name.title(), self.root, frame.name)  # type: ignore
            for frame in appframes
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
