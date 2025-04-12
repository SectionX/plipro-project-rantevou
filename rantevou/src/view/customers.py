from __future__ import annotations
from unicodedata import normalize

import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import askyesno
from typing import Any, Literal
from .abstract_views import AppFrame
from .sidepanel import SidePanel, AddAppointmentView
from ..model.types import Customer
from ..controller.customers_controller import CustomerControl
from ..controller.logging import Logger

cc = CustomerControl()
logger = Logger("customers-view")


class SubscriberInterface:
    def __init__(self):
        cc.add_subscriber(self)

    def subscriber_update(self):
        raise NotImplementedError


class SearchBar(ttk.Frame):
    searchbar: ttk.Entry
    customers: list[Customer]
    sheet: CustomerSheet

    def __init__(self, master, sheet: CustomerSheet, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.sheet = sheet
        self.searchbar = ttk.Entry(self)
        self.searchbar.pack()

    def search(self): ...


class CustomerSheet(ttk.Treeview, SubscriberInterface):
    column_names: list[str]
    focus_values: list[Any] | Literal[""]
    focus_column_index: int

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        SubscriberInterface.__init__(self)
        self.focus_values = []
        self.focus_column_index = 0
        self.column_names = cc.get_customer_fields()
        self["columns"] = self.column_names
        self.bind("<Button-1>", self.get_focus_values)
        self.bind("<Double-Button-1>", self.populate_add_appointment_view)

        for i, name in enumerate(self.column_names):
            self.heading(
                name, text=name.title(), command=lambda: self.sort(reverse=False)
            )
        self.column("#0", width=0, stretch=tk.NO)
        self.column("id", width=0, stretch=tk.NO)

        self.populate_sheet()

    def subscriber_update(self):
        print("updating")
        self.delete(*self.get_children())
        self.populate_sheet()

    def populate_sheet(self):
        for customer in CustomersTab.customers:
            values = customer.values
            values[-1] = len(values[-1])
            self.insert("", "end", values=values)

    def get_focus_values(self, event: tk.Event):
        row = self.identify_row(event.y)
        column = self.identify_column(event.x)
        self.focus_values = self.item(row)["values"]
        self.focus_column_index = int(column[1:]) - 1

    def sort(self, reverse):
        colname = self.column_names[self.focus_column_index]
        data = [(item, self.item(item)["values"]) for item in self.get_children()]
        data.sort(
            key=lambda x: normalize("NFKD", str(x[1][self.focus_column_index])),
            reverse=reverse,
        )
        for index, (item, _) in enumerate(data):
            self.move(item, "", index)
        self.heading(colname, command=lambda: self.sort(not reverse))

    def populate_add_appointment_view(self, *args):
        SidePanel.update_data("customer_data", self.focus_values)
        sidepanel = SidePanel.instance()
        if sidepanel is None:
            logger.log_warn("Failed to communicate with SidePanel")
            return

        if sidepanel.active_view != sidepanel.side_views["add"]:
            return

        view = sidepanel.side_views["add"]
        if isinstance(view, AddAppointmentView):
            view.populate_from_customer_tab()
        else:
            logger.log_warn('Failed to communicate with "add" view')


class ManagementBar(ttk.Frame):
    add_button: ttk.Button
    edit_button: ttk.Button
    del_button: ttk.Button
    sheet: CustomerSheet

    def __init__(self, master, sheet: CustomerSheet, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.sheet = sheet
        self.button_frame = ttk.Frame(self)
        self.add_button = ttk.Button(
            self.button_frame, text="Add", command=self.add_customer
        )
        self.edit_button = ttk.Button(
            self.button_frame, text="Edit", command=self.edit_customer
        )
        self.del_button = ttk.Button(
            self.button_frame, text="Delete", command=self.del_customer
        )

        self.button_frame.pack()
        self.add_button.pack(side=tk.LEFT)
        self.edit_button.pack(side=tk.LEFT)
        self.del_button.pack(side=tk.LEFT)

    def add_customer(self):
        print(cc.model.subscribers)
        SidePanel.select_view("addc")
        # TODO update treeview instead of reloading

    def edit_customer(self):
        print(cc.model.subscribers)
        SidePanel.select_view("editc", caller=self, data=self.sheet.focus_values)

    def del_customer(self):
        print(cc.model.subscribers)
        id = int(self.sheet.focus_values[0])
        name = self.sheet.focus_values[1]
        surname = self.sheet.focus_values[2]

        confirmation = askyesno(
            "Deletion Confirmation",
            f"Are you sure you want to delete customer {name} {surname}",
        )

        if confirmation:
            cc.delete_customer(int(self.sheet.focus_values[0]))


class CustomersTab(AppFrame, SubscriberInterface):
    customers: list[Customer] = cc.get_customers()

    def __init__(self, root):
        super().__init__(root)
        SubscriberInterface.__init__(self)

        self.customer_sheet = CustomerSheet(self)
        self.search_bar = SearchBar(self, self.customer_sheet)
        self.management_bar = ManagementBar(self, self.customer_sheet)

        self.search_bar.pack(fill="x")
        self.customer_sheet.pack(fill="both", expand=True)
        self.management_bar.pack(fill="x")

    def subscriber_update(self):
        CustomersTab.customers = cc.get_customers()
