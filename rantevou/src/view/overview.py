import tkinter as tk

from .window import root
from .customers import create_customer_view
from .appointments import create_appointments_view
from .statistics import create_statistics_view
from .alerts import create_alerts_view


class Overview(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

    def go_to_customers(self):
        pass

    def go_to_appointments(self):
        pass

    def go_to_statistics(self):
        pass

    def go_to_alerts(self):
        pass


def create_overview(parent=root):
    return Overview(parent)
