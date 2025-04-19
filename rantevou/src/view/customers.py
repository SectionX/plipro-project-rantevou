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
from ..controller.logging import Logger
from ..controller import SubscriberInterface

##profiling
from time import perf_counter

logger = Logger("customers-view")


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
        self.search_results: list[Customer] | None = None
        self.cancel_id: str | None = None

    def search(self, event: tk.Event, execute=False):
        if self.cancel_id and not execute:
            self.after_cancel(self.cancel_id)
            self.cancel_id = None

        if not execute:
            symbol = event.keysym
            char = event.char

            if symbol == "Escape":
                self.key_sequence = []
                CustomersTab.customers = (
                    CustomerControl().model.session.query(Customer).all()
                )
                self.sheet.populate_sheet()
                self.searchbar.delete(0, tk.END)
                return

            if symbol == "BackSpace":
                self.key_sequence.pop()
                if self.search_results is not None and len(self.search_results) == len(
                    CustomersTab.customers
                ):
                    self.search_results = None
                    self.sheet.populate_sheet()
            else:
                self.key_sequence.append(char)

            self.cancel_id = self.after(
                50 + len(CustomersTab.customers) // 1000,
                lambda: self.search(event, execute=True),
            )
            return

        self.search_results = CustomerControl().search("".join(self.key_sequence))
        self.sheet.populate_sheet(self.search_results)


class CustomerSheet(ttk.Treeview, SubscriberInterface):
    column_names: list[str]
    focus_values: list[Any] | Literal[""]
    focus_column_index: int
    sidepanel: SidePanel
    pagination: Pagination

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        SubscriberInterface.__init__(self)
        self.sidepanel = self.nametowidget(".!sidepanel")
        self.current_page = 1
        self.max_page = len(CustomersTab.customers)
        self.focus_values = []
        self.focus_column_index = 0
        self.search_data = None
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

        self.page = 0

        self.populate_sheet()

    def go_left(self):
        self.current_page = self.pagination.current_page
        self.populate_sheet(self.search_data)

    def go_right(self):
        self.current_page = self.pagination.current_page
        self.populate_sheet(self.search_data)

    def subscriber_update(self):
        self.current_page = 1
        self.max_page = len(CustomersTab.customers)
        self.pagination.reset()
        self.populate_sheet()

    def populate_sheet(self, search_data: list[Customer] | None = None):
        page_left_limit = (self.current_page - 1) * 100
        page_right_limit = (self.current_page) * 100

        if search_data is None:
            self.search_data = None
            data = CustomersTab.customers
        else:
            self.search_data = search_data
            data = search_data

        self.delete(*self.get_children())
        for customer in data[page_left_limit:page_right_limit]:
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
        if self.search_data is not None:
            self.search_data.sort(key=lambda x: x.__dict__[colname], reverse=reverse)
            self.populate_sheet(self.search_data)
        else:
            CustomersTab.customers.sort(
                key=lambda x: x.__dict__[colname], reverse=reverse
            )
            self.populate_sheet()
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
            CustomerControl().delete_customer(Customer(id=id))


class Pagination(ttk.Frame):
    sheet: CustomerSheet

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, *kwargs)
        self.current_page = 1
        self.button_frame = ttk.Frame(self)
        self.button_frame.pack()
        self.left_button = ttk.Button(
            self.button_frame,
            text="<",
            command=self.go_left,
            width=3,
        )
        self.right_button = ttk.Button(
            self.button_frame,
            text=">",
            command=self.go_right,
            width=3,
        )
        self.page_label = ttk.Label(
            self.button_frame,
            text=str(self.current_page),
            width=3,
            anchor="n",
        )

        self.left_button.pack(side=tk.LEFT)
        self.page_label.pack(side=tk.LEFT)
        self.right_button.pack(side=tk.LEFT)

    def set_sheet(self, sheet: CustomerSheet):
        self.sheet = sheet

    def go_left(self):
        if self.current_page == 1:
            return

        self.current_page -= 1
        self.page_label.config(text=str(self.current_page))

        self.sheet.go_left()

    def go_right(self):
        if self.current_page == self.sheet.max_page:
            return

        self.current_page += 1
        self.page_label.config(text=str(self.current_page))

        self.sheet.go_right()

    def reset(self):
        self.current_page = 1
        self.max_page = self.sheet.max_page


class CustomersTab(AppFrame, SubscriberInterface):
    customers: list[Customer]

    def __init__(self, root, *args, **kwargs):
        super().__init__(root, *args, **kwargs)
        SubscriberInterface.__init__(self)
        self.customers = CustomerControl().get_customers()
        CustomersTab.customers = self.customers

        self.customer_sheet = CustomerSheet(self)
        self.page_bar = Pagination(self)
        self.page_bar.set_sheet(self.customer_sheet)
        self.customer_sheet.pagination = self.page_bar

        self.search_bar = SearchBar(self, self.customer_sheet)
        self.management_bar = ManagementBar(self, self.customer_sheet)

        self.search_bar.pack(fill="x")
        self.customer_sheet.pack(fill="both", expand=True)
        self.page_bar.pack(fill="x")
        self.management_bar.pack(fill="x")

    def subscriber_update(self):
        CustomersTab.customers = CustomerControl().get_customers()
