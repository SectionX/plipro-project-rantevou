import tkinter as tk


class Customers(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)


def create_customer_view(parent):
    return Customers(parent)
