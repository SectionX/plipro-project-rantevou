import tkinter as tk
from tkinter import ttk


class Appointments(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        go_to_overview = tk.Button(
            self,
            text="Return to Overview",
            command=lambda: parent.change_frame("overview"),
        )
        go_to_overview.pack()


def create_appointments_view(parent):
    return Appointments(parent)
