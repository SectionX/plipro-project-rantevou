import tkinter as tk
from tkinter import ttk
from tkinter.font import Font
from tkinter.messagebox import showerror, showinfo, askyesno
from typing import Iterator

from .abstract_views import AppFrame
from ..controller.customers_controller import CustomerControl


class Customers(AppFrame):
    def __init__(self, root, name="customers"):
        super().__init__(root, name)
        self.controller = CustomerControl()
        self.customers = self.controller.get_customers()
        self.current_selected_id: int = -1
        self.current_selected_row: list = []
        self.edit_panel_is_open = False
        self.body.configure(background="grey")
        self.action_panel = None

        self.searchbar = tk.Entry(self.body, width=30)
        self.searchbar.focus()
        self.tree = ttk.Treeview(self.body)

        self.searchbar.pack()
        self.tree.pack(fill="both", expand=True)

        self.button_bar = tk.Frame(self.body)
        self.button_bar.pack()

        self.add_button = tk.Button(
            self.button_bar, text="Add Customer", command=self.create_customer
        )

        self.delete_button = tk.Button(
            self.button_bar, text="Delete Customer", command=self.delete_customer
        )

        self.edit_button = tk.Button(
            self.button_bar,
            text="Edit Customer",
            command=lambda: self.update_customer(initialize=True),
        )

        self.add_button.pack(side=tk.LEFT)
        self.delete_button.pack(side=tk.LEFT)
        self.edit_button.pack(side=tk.LEFT)
        self.initialize()
        self.initialize_tree()

        self.bind("<Key>", self.search)
        self.searchbar.bind("<KeyRelease>", lambda _: self.search())
        self.body.bind("<Key>", self.search)
        self.tree.bind("<Key>", self.search)
        self.tree.bind("<ButtonRelease-1>", self._tree_click_handler)
        self.tree.bind("<Button-1>", self.tree_identify)

    def tree_identify(self, event):
        self.row_focus = self.tree.identify_row(event.y)
        self.column_focus = self.tree.identify_column(event.x)
        self.value_focus = self.tree.item(self.row_focus)["values"]
        print(self.value_focus)

    def initialize_tree(self):
        font = Font()
        em = font.measure("m")
        self.sort_state = [False, False, False, False, False]

        self.tree["columns"] = ("id", "name", "surname", "phone", "email")
        self.tree.column("#0", width=0, stretch=False)
        self.tree.column("id", width=0 * em, stretch=False)
        self.tree.column("name", width=9 * em, stretch=False)
        self.tree.column("surname", width=10 * em, stretch=False)
        self.tree.column("phone", width=8 * em, stretch=False)
        self.tree.column("email", width=20 * em, stretch=True)
        self.tree.heading("#0", text="", anchor="w")
        self.tree.heading("id", text="ID", anchor="w")
        self.tree.heading("name", text="Name", anchor="w")
        self.tree.heading("surname", text="Surname", anchor="w")
        self.tree.heading("phone", text="Phone", anchor="w")
        self.tree.heading("email", text="Email", anchor="w")

        self.populate_tree()

    def reset_tree(self, filter=None, hard_reset=False):
        self.focus()
        self.tree.delete(*self.tree.get_children())
        if hard_reset:
            self.customers = self.controller.get_customers()
        self.populate_tree(filter)

    def populate_tree(self, filter=None):
        for customer in self.customers:
            if filter is None or (filter and filter(customer)):
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        customer.id,
                        customer.name,
                        customer.surname,
                        customer.phone,
                        customer.email,
                    ),
                )

    def _tree_click_handler(self, event):
        self.tree_identify(event)
        print(self.row_focus, self.column_focus)
        if not self.value_focus:
            self.sort()

    def sort(self):
        column_index = int(self.column_focus[1:]) - 1
        column = self.tree.heading(column_index)["text"].lower()
        for i in range(len(self.sort_state)):
            if i != column_index:
                self.sort_state[i] = False
            else:
                self.sort_state[i] = not self.sort_state[i]

        reverse = True
        if self.sort_state[column_index]:
            reverse = False

        self.customers.sort(key=lambda x: getattr(x, column), reverse=reverse)
        self.reset_tree()

    def search(self, event=None):
        print(self.searchbar.focus_get())
        if self.searchbar != self.searchbar.focus_get():
            self.searchbar.focus()
            self.searchbar.insert("end", event.char)
        self.tree.delete(*self.tree.get_children())
        search_string = self.searchbar.get().lower()
        for customer in self.customers:
            for key, value in customer.__dict__.items():
                if search_string in str(value).lower():
                    self.tree.insert(
                        "",
                        "end",
                        values=(
                            customer.id,
                            customer.name,
                            customer.surname,
                            customer.phone,
                            customer.email,
                        ),
                    )
                    break

    # Create Customer
    def open_customer_pop_up(self, prefill={}, edit_mode=False):
        self.popup = tk.Toplevel(self.body)
        name_entry = tk.Entry(self.popup, name="name")
        surname_entry = tk.Entry(self.popup, name="surname")
        phone_entry = tk.Entry(self.popup, name="phone")
        email_entry = tk.Entry(self.popup, name="email")

        self.popup.title("Add Customer")
        self.popup.geometry("250x400")
        name_entry.insert(0, prefill.get("name") or "Enter name...")
        surname_entry.insert(0, prefill.get("surname") or "Enter surname...")
        phone_entry.insert(0, prefill.get("phone") or "Enter phone...")
        email_entry.insert(0, prefill.get("email") or "Enter email...")

        if edit_mode:
            callback = self.update_customer
        else:
            callback = self.create_customer
        email_entry.bind("<Return>", lambda _: callback(initialize=False))
        button = tk.Button(
            self.popup,
            text="Add",
            command=lambda: callback(initialize=False),
        )

        name_entry.pack()
        surname_entry.pack()
        phone_entry.pack()
        email_entry.pack()
        button.pack()

        self.popup.mainloop()

    def create_customer(self, prefill={}, initialize=True):
        if initialize:
            self.open_customer_pop_up(prefill)

        entries: Iterator[tk.Entry] = filter(
            lambda x: isinstance(x, tk.Entry), self.popup.winfo_children()
        )

        customer = {}
        for entry in entries:
            print(entry, entry.winfo_name(), entry.get())
            customer[entry.winfo_name()] = entry.get()

        if not self.controller.validate_customer(customer):
            showerror("Error", "Make sure to include all fields")
            self.popup.destroy()
            self.create_customer(customer)
            return

        self.popup.destroy()
        showinfo("Success", "Customer added successfully")
        self.controller.create_customer(customer, threaded=False)
        self.reset_tree(hard_reset=True)

    def delete_customer(self):
        values = self.tree.item(self.tree.focus())["values"]
        user_response = askyesno(
            message="Are you sure you want to delete this customer?"
        )
        if user_response:
            self.controller.delete_customer(customer=int(values[0]), threaded=False)
            self.reset_tree(hard_reset=True)
        else:
            showinfo("Canceled", "Customer deletion canceled")

    def update_customer(self, prefill={}, initialize=True):
        if initialize:
            prefill = dict(zip(self.tree["columns"][1:], self.value_focus[1:]))
            self.open_customer_pop_up(prefill, edit_mode=True)

        entries: Iterator[tk.Entry] = filter(
            lambda x: isinstance(x, tk.Entry), self.popup.winfo_children()
        )

        customer = {}
        for entry in entries:
            print(entry, entry.winfo_name(), entry.get())
            customer[entry.winfo_name()] = entry.get()

        if not self.controller.validate_customer(customer):
            showerror("Error", "Make sure to include all fields")
            self.popup.destroy()
            self.update_customer(customer)
            return

        customer["id"] = self.value_focus[0]
        self.popup.destroy()
        showinfo("Success", "Customer updated successfully")
        self.controller.update_customer(customer, threaded=False)
        self.reset_tree(hard_reset=True)
