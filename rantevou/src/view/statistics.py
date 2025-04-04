import tkinter as tk


class Statistics(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

    def return_to_overview(self):
        pass


def create_statistics_view(parent):
    return Statistics(parent)
