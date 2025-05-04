from __future__ import annotations


import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import askyesno
from typing import Any, Literal, Protocol, runtime_checkable
from .abstract_views import AppFrame
from .sidepanel import SidePanel
from ..model.entities import Customer
from ..controller.customers_controller import CustomerControl
from ..controller.logging import Logger
from ..controller import SubscriberInterface
from ..controller import get_config

config = get_config()

logger = Logger("customers-view")


@runtime_checkable
class PopulateFromCustomer(Protocol):
    """
    Διεπαφή για τα widgets που εισάγουν αυτόματα (διπλό κλικ) στοιχεία πελατών
    στις φόρμες ραντεβού.
    """

    def populate_from_customer_tab(self, customer_data: Any | None): ...


class SearchBar(ttk.Frame):
    """
    Αναζήτηση πελατών. Η λογική του αλγορίθμου είναι ότι ψάχνει όλα τα πεδία
    που αρχίζουν από την συμβολοσειρά που πληκτρολογεί ο χρήστης.

    Έχουν γίνει πολλές βελτιστοποιήσεις.
    * Αναζήτηση κατα την πληκτρολόγηση με βελτιστοποιήσεις που μειώνουν τον φόρτο
    και το κλείδωμα της γραφικής επιφάνειας χωρίς χρήση threading.

    * Collation: Αν και η sqlite έχει θέματα με unicode, η υποστηρίζει πλήρη
    case insensitive και accent insensitive αναζήτηση.

    * Delay που μεγαλώνει με βάση το πλήθος των πελατών στην βάση δεδομένων, ώστε
    να γίνονται λιγότερες αναζητήσεις κατα την πληκτρολόγηση.

    * Pagination που μειώνει δραστικά τους χρόνους rendering και τις ανάγκες μνήμης,
    υλοποιημένο απευθείας στο μοντέλο με μέθοδο "query composition". Δηλαδή το
    query φτιάχνεται δυναμικά ανάλογα με τις ανάγκες της καλούσας.

    * Ελεγμένο για 300,000 πελάτες.
    """

    searchbar: ttk.Entry
    customers: list[Customer]
    sheet: CustomerSheet

    def __init__(self, master, sheet: CustomerSheet, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.sheet = sheet
        self.searchbar = ttk.Entry(self)
        self.searchbar.bind("<Key>", self.search)
        self.searchbar.bind("<Visibility>", lambda x: self.searchbar.focus())
        self.searchbar.pack()
        self.search_results: list[Customer] | None = None
        self.cancel_id: str | None = None

    def search(self, event: tk.Event, execute=False):
        """
        Εφαρμόζει ένα loop με χρήση της .after που περιμένει για μερικά millisec
        πριν στείλει το query στην βάση δεδομένων. To delay αυξάνεται δυναμικά
        με βάση το πλήθος των εγγεγραμένων πελατών.
        """
        if self.cancel_id and not execute:
            self.after_cancel(self.cancel_id)
            self.cancel_id = None

        if not execute:
            if event.keysym == "Escape":
                self.searchbar.delete(0, tk.END)
                self.sheet.reset()
                self.sheet.populate_sheet()
                self.searchbar.delete(0, tk.END)
                return

            self.key_sequence = self.searchbar.get()

            self.cancel_id = self.after(
                50 + self.sheet.max_page // 100,
                lambda: self.search(event, execute=True),
            )
            return

        self.sheet.current_page = 1
        self.sheet.search_query = self.searchbar.get()
        self.sheet.populate_sheet()


class CustomerSheet(ttk.Treeview, SubscriberInterface):
    """
    Εμφάνιση των πελατών σε μορφή τύπου worksheet. Υποστηρίζει λειτουργία
    αυτόματης συμπλήρωσης φόρμας ραντεβού με στοιχεία πελάτη. Έχει γίνει
    σελιδοποίηση στις 100 εγγραφές ανα σελίδα επειδή το rendering είναι
    σχετικά αργό.
    """

    column_names: list[str]
    focus_values: list[Any] | Literal[""]
    focus_column_index: int
    sidepanel: SidePanel
    pagination: Pagination

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        SubscriberInterface.__init__(self)

        self.sidepanel = self.nametowidget(".!sidepanel")
        self.page_length = config["view_settings"]["page_length"]
        self.current_page = 1
        self.customers, self.max_page = self.get_customer_page()

        self.search_query = ""
        self.sorted_by = ""
        self.descending = False

        self.focus_values = []
        self.focus_column_index = 0
        self.search_data = None
        self.column_names = Customer.field_names()
        self["columns"] = self.column_names
        self.bind("<Button-1>", self.get_focus_values)
        self.bind("<Double-Button-1>", self.populate_appointment_view)

        for i, name in enumerate(self.column_names):
            self.heading(name, text=name.title(), command=lambda: self.sort(reverse=False))
        self.column("#0", width=0, stretch=tk.NO)
        self.column("id", width=0, stretch=tk.NO)

        self.page = 0

        self.populate_sheet()
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.yview, style="Vertical.TScrollbar")
        self.scrollbar.pack(side="right", fill="y")
        self.configure(yscrollcommand=self.scrollbar.set)

    def reset(self):
        self.current_page = 1
        self.search_query = ""
        self.sorted_by = ""
        self.descending = False

    def get_customer_page(self) -> tuple[list[Customer], int]:
        """
        Βοηθητική συνάρτηση αρχικοποίησης.
        """
        return CustomerControl().get_customers(page_length=self.page_length, page_number=self.current_page)

    def go_left(self):
        self.current_page = self.pagination.current_page
        self.populate_sheet()

    def go_right(self):
        self.current_page = self.pagination.current_page
        self.populate_sheet()

    def subscriber_update(self):
        """
        Εφαρμογή του subscriber pattern. Καλείται από το μοντελο όταν γίνεται
        μια σημαντική αλλαγή στα δεδομένα.
        """
        self.pagination.reset()
        self.reset()
        self.current_page = 1
        self.customers, self.max_page = self.get_customer_page()
        self.populate_sheet()

    def populate_sheet(self):
        """
        Η κεντρική συνάρτηση του customer tab. Ορίζει την δημιουργία του query
        στην βάση δεδομένων βάση του πως αλλάζουν την κατάσταση της τα υπόλοιπα
        widget.

        Προτιμήθηκε να σβήνει και να ξαναγράφει τα κελιά από το να γράφει πάνω
        στα υπάρχοντα επειδή θα γίνει ιδιαίτερα πολύπλοκη η λογική με τόσα κινητά
        μέρη.

        Εφόσον είναι περιορισμένη στις 100 εγγραφές ανα σελίδα είναι αρκετά
        αποδοτική.
        """
        self.customers, self.max_page = CustomerControl().get_customers(
            page_number=self.current_page,
            page_length=self.page_length,
            search_query=self.search_query,
            sorted_by=self.sorted_by,
            descending=self.descending,
        )

        self.delete(*self.get_children())
        for customer in self.customers:
            values = customer.values
            values = [value or "" for value in values]
            self.insert("", "end", values=values)

    def get_focus_values(self, event: tk.Event):
        """
        Βοηθητική συνάρτηση που καταγράφει το τελευταίο κελί που πατήθηκε
        ανα πάσα στιγμή ώστε να απλοποιηθούν οι αλγόριθμοι στα υπόλοιπα στοιχεία
        """
        row = self.identify_row(event.y)
        column = self.identify_column(event.x)
        self.focus_values = self.item(row)["values"]
        self.focus_column_index = int(column[1:]) - 1

    def sort(self, reverse):
        """
        Sort με βάση την στήλη. Υποστηρίζει αύξουσα και φθήνουσα ταξινόμηση
        και ενεργοποιείται στο πάτημα του column header.
        """
        colname = self.column_names[self.focus_column_index]
        self.sorted_by = colname
        self.descending = reverse
        self.populate_sheet()
        self.heading(colname, command=lambda: self.sort(not reverse))

    def populate_appointment_view(self, *args):
        """
        Συνάρτηση διεπαφής που γράφει αυτόματα τα στοιχεία του πελάτη
        στις φόρμες εισαγωγής/επεξεργασίας
        """
        side_view = self.sidepanel.active_view
        if isinstance(side_view, PopulateFromCustomer):
            try:
                side_view.populate_from_customer_tab(self.focus_values)
            except:
                logger.log_error(f"Failed to communicate with {side_view}")


class ManagementBar(ttk.Frame):
    """
    Φέρει τα κουμπιά εισαγωγής και επεξεργασίας πελατών.
    """

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
        self.add_button = ttk.Button(self.button_frame, text="Add", command=self.add_customer)
        self.edit_button = ttk.Button(self.button_frame, text="Edit", command=self.edit_customer)
        self.del_button = ttk.Button(self.button_frame, text="Delete", command=self.del_customer)

        self.button_frame.pack()
        self.add_button.pack(side=tk.LEFT)
        self.edit_button.pack(side=tk.LEFT)
        self.del_button.pack(side=tk.LEFT)

    def add_customer(self):
        self.sidepanel.select_view("addc", caller=self, caller_data=None)

    def edit_customer(self):
        self.sidepanel.select_view("editc", caller=self, caller_data=self.sheet.focus_values)

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
    """
    Φέρει τα κουμπιά αλλαγής σελίδας και την απαραίτητη λογική.
    """

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
        """
        Συνάρτηση αρχικοποίησης λόγω import conflict. Καλείται από το
        CustomersTab.
        """
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


class CustomersTab(AppFrame):
    """
    Το κεντρικό widget που αρχικοποιεί και εμφανίζει όλα τα στοιχεία
    του customer tab.
    """

    def __init__(self, root, *args, **kwargs):
        super().__init__(root, *args, **kwargs)

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
