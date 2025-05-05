from __future__ import annotations

from tkinter import ttk
from tkinter.messagebox import showerror

from .sidepanel import SidePanel
from .abstract_views import SideView

from ..controller.customers_controller import CustomerControl
from ..controller.logging import Logger
from ..controller.mailer import Mailer
from ..model.entities import Customer
from .forms import CustomerForm

logger = Logger("customer-manager")
mailer = Mailer()


class AddCustomerView(SideView):
    """
    View δημιουργίας νέου πελάτη
    """

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.name = "addc"
        self.main_frame = ttk.Frame(self, borderwidth=3, relief="sunken")
        self.main_frame.pack(fill="both", expand=True)

        self.set_title("Προσθήκη νέου πελάτη")
        self.customer_entry = CustomerForm(self.main_frame)
        self.customer_entry.pack(fill="x")
        self.save_button = ttk.Button(self.main_frame, text="Add", command=self.save)
        self.save_button.pack()

    def update_content(self, caller, caller_data):
        self.customer_entry.populate(None)

    def save(self):
        new_customer = self.customer_entry.get()
        success = CustomerControl().create_customer(new_customer)
        if not success:
            showerror(message="Failed to add new customer")
        else:
            self.sidepanel.go_back()


class EditCustomerView(SideView):
    """
    View επεξεργασίας πελάτη
    """

    def __init__(self, master: SidePanel, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.name = "editc"
        self.main_frame = ttk.Frame(self, borderwidth=3, relief="sunken")
        self.sidepanel = master

        self.set_title("Επεξεργασία νέου πελάτη")
        self.main_frame.pack(fill="both", expand=True)

        self.customer_entry = CustomerForm(self.main_frame)
        self.customer_entry.pack(fill="x")

        self.save_button = ttk.Button(self.main_frame, text="Save", command=self.save)
        self.save_button.pack()

    def update_content(self, caller, caller_data):
        if not isinstance(caller_data, Customer):
            logger.log_warn("Failed to communicate customer data")
            return

        self.customer_entry.populate(caller_data)

    def save(self):
        new_customer = self.customer_entry.get()
        success = CustomerControl().update_customer(new_customer)
        if not success:
            showerror(message="Failed to update customer")
        else:
            self.sidepanel.go_back()
