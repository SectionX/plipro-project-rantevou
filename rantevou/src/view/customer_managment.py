# from __future__ import annotations

# import tkinter as tk
# from tkinter import ttk
# from tkinter.messagebox import showerror
# from datetime import datetime, timedelta
# from typing import Literal

# from . import sidepanel
# from .abstract_views import EntryWithPlaceholder
# from . import abstract_views

# from ..model.types import Appointment, Customer
# from ..controller.appointments_controller import AppointmentControl
# from ..controller.customers_controller import CustomerControl
# from ..controller.logging import Logger
# from ..controller.mailer import Mailer


# cc = CustomerControl()
# ac = AppointmentControl()
# logger = Logger("customer-manager")
# mailer = Mailer()


# class AddCustomerView(abstract_views.SideView):

#     def __init__(self, master, *args, **kwargs):
#         super().__init__(master, *args, **kwargs)
#         self.name = "addc"
#         self.main_frame = ttk.Frame(self, borderwidth=3, relief="sunken")

#         self.set_title("Προσθήκη νέου πελάτη")
#         self.main_frame.pack(fill="both", expand=True)
#         self.add_back_btn(self)

#         self.cus_entry_name = EntryWithPlaceholder(self.main_frame, placeholder="name")
#         self.cus_entry_name.pack(fill="x")
#         self.cus_entry_surname = EntryWithPlaceholder(
#             self.main_frame, placeholder="surname"
#         )
#         self.cus_entry_surname.pack(fill="x")
#         self.cus_entry_phone = EntryWithPlaceholder(
#             self.main_frame, placeholder="phone number"
#         )
#         self.cus_entry_phone.pack(fill="x")
#         self.cus_entry_email = EntryWithPlaceholder(
#             self.main_frame, placeholder="email address"
#         )
#         self.cus_entry_email.pack(fill="x")
#         self.save_button = ttk.Button(self.main_frame, text="Save", command=self.save)
#         self.save_button.pack()

#     def update_content(self):
#         for entry in self.main_frame.winfo_children():
#             if isinstance(entry, EntryWithPlaceholder):
#                 entry.delete(0, tk.END)
#                 entry.put_placeholder()

#     def save(self):
#         cc.create_customer(
#             Customer(
#                 name=self.cus_entry_name.get_without_placeholder(),
#                 surname=self.cus_entry_surname.get_without_placeholder(),
#                 phone=self.cus_entry_phone.get_without_placeholder(),
#                 email=self.cus_entry_email.get_without_placeholder(),
#             )
#         )


# class EditCustomerView(abstract_views.SideView):

#     def __init__(self, master, *args, **kwargs):
#         super().__init__(master, *args, **kwargs)
#         self.name = "editc"
#         self.main_frame = ttk.Frame(self, borderwidth=3, relief="sunken")

#         self.set_title("Επεξεργασία νέου πελάτη")
#         self.main_frame.pack(fill="both", expand=True)
#         self.add_back_btn(self)

#         self.cus_entry_name = ttk.Entry(self.main_frame)
#         self.cus_entry_name.pack(fill="x")
#         self.cus_entry_surname = ttk.Entry(self.main_frame)
#         self.cus_entry_surname.pack(fill="x")
#         self.cus_entry_phone = ttk.Entry(self.main_frame)
#         self.cus_entry_phone.pack(fill="x")
#         self.cus_entry_email = ttk.Entry(self.main_frame)
#         self.cus_entry_email.pack(fill="x")
#         self.save_button = ttk.Button(self.main_frame, text="Save", command=self.save)
#         self.save_button.pack()

#     def update_content(self):
#         self.reset()
#         caller_data = sidepanel.SidePanel.fetch_data("caller_data")
#         if not isinstance(caller_data, list):
#             logger.log_warn("Failed to communicate customer data")
#             return

#         if len(caller_data) < 5:
#             logger.log_warn("Failed to communicate customer data")
#             return

#         self.cus_id = int(caller_data[0])
#         if caller_data[1] is not None:
#             self.cus_entry_name.insert(0, caller_data[1])
#         if caller_data[2] is not None:
#             self.cus_entry_surname.insert(0, caller_data[2])
#         if caller_data[3] is not None:
#             self.cus_entry_phone.insert(0, caller_data[3])
#         if caller_data[4] is not None:
#             self.cus_entry_email.insert(0, caller_data[4])

#     def save(self):
#         cc.update_customer(
#             Customer(
#                 id=self.cus_id,
#                 name=self.cus_entry_name.get() or None,
#                 surname=self.cus_entry_surname.get() or None,
#                 phone=self.cus_entry_phone.get() or None,
#                 email=self.cus_entry_email.get() or None,
#             )
#         )

#     def reset(self):
#         self.cus_entry_name.delete(0, tk.END)
#         self.cus_entry_surname.delete(0, tk.END)
#         self.cus_entry_phone.delete(0, tk.END)
#         self.cus_entry_email.delete(0, tk.END)
