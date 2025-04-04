import tkinter as tk
from tkinter import ttk


class Appointments(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)


def create_appointments_view(parent):
    return Appointments(parent)
