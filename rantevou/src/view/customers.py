from __future__ import annotations
from unicodedata import normalize

import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import askyesno
from typing import Any, Literal, Protocol, runtime_checkable
from .abstract_views import AppFrame
from .sidepanel import SidePanel
from ..model.types import Customer
from ..controller.customers_controller import CustomerControl
from ..controller.appointments_controller import AppointmentControl
from ..controller.logging import Logger
from threading import Thread, Semaphore

semaphore = Semaphore(1)

cc = CustomerControl()
ac = AppointmentControl()
logger = Logger("customers-view")


class SubscriberInterface:
    def __init__(self):
        ac.add_subscription(self)
        cc.add_subscription(self)

    def subscriber_update(self):
        raise NotImplementedError


@runtime_checkable
class PopulateFromCustomer(Protocol):
    def populate_from_customer_tab(self, customer_data: Any | None): ...


def check_values(values, keysequence):
    for value in values:
        value = normalize("NFKD", str(value)).lower().replace("́", "")
        if value.startswith(keysequence):
            return True
    return False


class SearchBar(ttk.Frame):
    searchbar: ttk.Entry
    customers: list[Customer]
    sheet: CustomerSheet
    key_sequence: list[str]

    def __init__(self, master, sheet: CustomerSheet, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.sheet = sheet
        self.key_sequence = []
        self.searchbar = ttk.Entry(self)
        self.searchbar.bind("<Key>", self.search)
        self.searchbar.bind("<Visibility>", lambda x: self.searchbar.focus())
        self.searchbar.pack()
        self.thread: Thread | None = None

    def search(self, event: tk.Event):
        self.after(0, lambda: self._search(event))

    def _search(self, event: tk.Event):
        symbol = event.keysym
        char = event.char

        if symbol == "Escape":
            self.key_sequence = []
            self.sheet.populate_sheet()
            self.searchbar.delete(0, tk.END)
            return

        if symbol == "BackSpace":
            self.key_sequence.pop()
            self.sheet.populate_sheet()
        else:
            self.key_sequence.append(char)

        keysequence = "".join(self.key_sequence).lower()

        children = self.sheet.get_children()
        if len(children) == 0:
            return

        end_ptr = len(children) - 1

        for i, item in enumerate(children):

            values = self.sheet.item(item)["values"]
            if i == end_ptr:
                if not check_values(values, keysequence):
                    self.sheet.delete(item)
                break

            if check_values(values, keysequence):
                continue

            while end_ptr > i:
                swap_values = self.sheet.item(children[end_ptr])["values"]
                self.sheet.item(item, values=swap_values)
                self.sheet.delete(children[end_ptr])
                end_ptr -= 1

                if check_values(swap_values, keysequence):
                    break


class CustomerSheet(ttk.Treeview, SubscriberInterface):
    column_names: list[str]
    focus_values: list[Any] | Literal[""]
    focus_column_index: int
    sidepanel: SidePanel

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        SubscriberInterface.__init__(self)
        self.sidepanel = self.nametowidget(".!sidepanel")
        self.focus_values = []
        self.focus_column_index = 0
        self.column_names = Customer.field_names()
        self["columns"] = self.column_names
        self.bind("<Button-1>", self.get_focus_values)
        self.bind("<Double-Button-1>", self.populate_appointment_view)

        for i, name in enumerate(self.column_names):
            self.heading(
                name, text=name.title(), command=lambda: self.sort(reverse=False)
            )
        self.column("#0", width=0, stretch=tk.NO)
        self.column("id", width=0, stretch=tk.NO)

        self.populate_sheet()

    def subscriber_update(self):
        self.populate_sheet()

    def populate_sheet(self):
        self.delete(*self.get_children())
        for customer in CustomersTab.customers:
            values = customer.values
            values = [value or "" for value in values]
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

    def populate_appointment_view(self, *args):
        side_view = self.sidepanel.active_view
        if isinstance(side_view, PopulateFromCustomer):
            try:
                side_view.populate_from_customer_tab(self.focus_values)
            except:
                logger.log_error(f"Failed to communicate with {side_view}")


class ManagementBar(ttk.Frame):
    add_button: ttk.Button
    edit_button: ttk.Button
    del_button: ttk.Button
    sheet: CustomerSheet
    sidepanel: SidePanel

    def __init__(self, master, sheet: CustomerSheet, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.sidepanel = self.nametowidget(".!sidepanel")
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
        self.sidepanel.select_view("addc", caller=self, caller_data=None)
        # TODO update treeview instead of reloading

    def edit_customer(self):
        self.sidepanel.select_view(
            "editc", caller=self, caller_data=self.sheet.focus_values
        )

    def del_customer(self):
        id = int(self.sheet.focus_values[0])
        name = self.sheet.focus_values[1]
        surname = self.sheet.focus_values[2]

        confirmation = askyesno(
            "Deletion Confirmation",
            f"Are you sure you want to delete customer {name} {surname}",
        )

        if confirmation:
            cc.delete_customer(Customer(id=id))


class CustomersTab(AppFrame, SubscriberInterface):
    customers: list[Customer] = cc.get_customers()

    def __init__(self, root, *args, **kwargs):
        super().__init__(root, *args, **kwargs)
        SubscriberInterface.__init__(self)

        self.customer_sheet = CustomerSheet(self)
        self.search_bar = SearchBar(self, self.customer_sheet)
        self.management_bar = ManagementBar(self, self.customer_sheet)

        self.search_bar.pack(fill="x")
        self.customer_sheet.pack(fill="both", expand=True)
        self.management_bar.pack(fill="x")

    def subscriber_update(self):
        CustomersTab.customers = cc.get_customers()
