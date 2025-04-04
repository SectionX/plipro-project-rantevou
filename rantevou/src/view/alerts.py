import tkinter as tk


class Alerts(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)


def create_alerts_view(parent):
    return Alerts(parent)
