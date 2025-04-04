import tkinter as tk

from .window import root
from .overview import create_overview


class Statistics(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

    def return_to_overview(self):
        root.change_frame(create_overview())


def create_statistics_view(parent=root):
    return Statistics(parent)
