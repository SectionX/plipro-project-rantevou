from tkinter import ttk
import tkinter as tk

from datetime import datetime, timedelta
from typing import Sequence


class AppointmentEntry(tk.Tk):
    values: Sequence | None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("600x300")
        e1 = tk.Entry(
            self, width=2, borderwidth=1, highlightcolor="red", relief="raised"
        )
        e2 = tk.Label(
            self,
            width=1,
            borderwidth=1,
            text="/",
            highlightcolor="red",
            relief="raised",
        )
        e3 = tk.Entry(
            self, width=2, borderwidth=1, highlightcolor="red", relief="raised"
        )
        e4 = tk.Label(
            self,
            width=1,
            borderwidth=1,
            text="/",
            highlightcolor="red",
            relief="raised",
        )
        e5 = tk.Entry(
            self, width=4, borderwidth=1, highlightcolor="red", relief="raised"
        )

        e6 = tk.Entry(
            self, width=2, borderwidth=1, highlightcolor="red", relief="raised"
        )
        e7 = tk.Label(
            self,
            width=1,
            borderwidth=1,
            text=":",
            highlightcolor="red",
            relief="raised",
        )
        e8 = tk.Entry(
            self, width=2, borderwidth=1, highlightcolor="red", relief="raised"
        )

        e9 = tk.Label(self, borderwidth=1, highlightcolor="red", relief="raised")
        e0 = tk.Entry(self, borderwidth=1, highlightcolor="red", relief="raised")

        self.grid_anchor("n")
        i = 0
        e1.grid(row=0, column=0, columnspan=2, sticky="we")
        e2.grid(row=0, column=2, sticky="we")
        e3.grid(row=0, column=3, columnspan=2, sticky="we")
        e4.grid(row=0, column=5, sticky="we")
        e5.grid(row=0, column=6, columnspan=4, sticky="we")

        e6.grid(row=1, column=2, columnspan=2, sticky="we")
        e7.grid(row=1, column=4, sticky="we")
        e8.grid(row=1, column=5, columnspan=2, sticky="we")

        e9.grid(row=2, column=0, columnspan=4, sticky="we")
        e0.grid(row=2, column=4, columnspan=6, sticky="we")


AppointmentEntry().mainloop()
