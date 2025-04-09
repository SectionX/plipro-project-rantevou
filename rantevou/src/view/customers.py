# TODO
# Θέλει πολλά refactors αλλα δουλεύει όπως πρέπει προς το παρών.
#
# Θα πρέπει να προσθεθεί κώδικας που συνδέεται με το Mailer αλλά δεν
# είμαι σίγουρος αν είναι καλύτερα να γίνει εδώ ή σε κάποιο άλλο module.
#
# Αν και δουλεύει σωστά σκοπέυω να το ξαναγράψω ώστε να διαβάζεται πιο εύκολα
# Ο λόγος που είναι τόσο χαοτικό είναι επειδή ήταν η πρώτη μου απόπειρα με να
# φτιάξω gui με κάποια πολυπλοκότητα μέσω tkinter. Το αντίστοιχο για τα ραντεβού
# είναι σαφώς πολύ πιο οργανωμένο, και θα προσπαθήσω να μιμηθώ εδώ ότι έκανα εκεί
# όσο αφορά το object oriented κομμάτι.
# - Στουραϊτης

import tkinter as tk
from tkinter import ttk
from tkinter.font import Font
from tkinter.messagebox import showerror, showinfo, askyesno
from typing import Iterator

from .abstract_views import AppFrame
from ..controller.customers_controller import CustomerControl


class Customers(AppFrame):
    def __init__(self, root):
        super().__init__(root)

        # Σύνδεση με την βάση μέσω του controller.
        self.controller = CustomerControl()
        self.customers = self.controller.get_customers()

        # Δημιουργία των βασικών widget
        self.searchbar = ttk.Entry(self, width=30)
        self.searchbar.focus()
        self.tree = ttk.Treeview(self)

        self.searchbar.pack()
        self.tree.pack(fill="both", expand=True)

        self.button_bar = ttk.Frame(self)
        self.button_bar.pack()

        self.add_button = ttk.Button(
            self.button_bar, text="Add Customer", command=self.create_customer
        )

        self.delete_button = ttk.Button(
            self.button_bar, text="Delete Customer", command=self.delete_customer
        )

        self.edit_button = ttk.Button(
            self.button_bar,
            text="Edit Customer",
            command=lambda: self.update_customer(initialize=True),
        )

        self.add_button.pack(side=tk.LEFT)
        self.delete_button.pack(side=tk.LEFT)
        self.edit_button.pack(side=tk.LEFT)
        self.initialize_tree()

        # Δεν είμαι σίγουρος πιο widget παίρνει τον έλεγχο μετά την καταστροφή
        # των pop up, γιαυτό απλά έβαλα event listeners στα πάντα. Θα το βελτιώσω
        # σε δεύτερο χρόνο.
        self.bind("<Key>", self.search)
        self.searchbar.bind("<KeyRelease>", lambda _: self.search())
        self.bind("<Key>", self.search)
        self.tree.bind("<Key>", self.search)
        self.tree.bind("<ButtonRelease-1>", self._tree_click_handler)
        self.tree.bind("<Button-1>", self.tree_identify)

    ####################################################################
    ##
    ##  Εδώ είναι όλες οι μέθοδοι που αφορούν το treeview widget.
    ##  Callbacks, ανίχνευση στοιχείων με βάση το mouse click,
    ##  sort, search και την αρχικοποίηση όλων των στοιχείων του.
    ##
    ##

    def tree_identify(self, event):
        """
        Λογγάρει το τελευταίο ενεργό κελί του treeview. Είναι
        αντίστοιχο με την εντολή self.tree.item(self.tree.focus())
        """
        self.row_focus = self.tree.identify_row(event.y)
        self.column_focus = self.tree.identify_column(event.x)
        self.value_focus = self.tree.item(self.row_focus)["values"]

    def sort(self):
        """
        Κώδικας που κάνει σορτ όταν γίνει mouse click στο header μιας
        στήλης. Το μόνο που κάνει αυτός ο κώδικας είναι να θυμάται αν
        πρέπει να κάνει αύξων ή φθίνων sort.
        """

        # Τα column indices έχουν σχήμα ονομασίας #1, #2, #3
        # οπότε αφαιρούμε την δίεση και το κάνουμε 0-βάση
        column_index = int(self.column_focus[1:]) - 1

        # Κάνει reset το sort_state των άλλων στηλών.
        column = self.tree.heading(column_index)["text"].lower()
        for i in range(len(self.sort_state)):
            if i != column_index:
                self.sort_state[i] = False
            else:
                self.sort_state[i] = not self.sort_state[i]

        # Αποφασίζει αν θα κάνει αύξων ή φθίνων sort
        reverse = True
        if self.sort_state[column_index]:
            reverse = False

        self.customers.sort(key=lambda x: getattr(x, column), reverse=reverse)
        self.reset_tree()

    def search(self, event=None):
        """
        Ο κώδικας για την μπάρα αναζήτησης. Γράφτηκε έτσι ώστε να δίνει
        δυναμικά τα αποτελέσματα καθώς ο χρήστης πληκτρολογεί. Επίσης είναι
        ρυθμισμένο ώστε να παίνει το focus όταν ο χρήστης πληκτρολογεί οπου
        δήποτε στο Frame.
        """

        # Εστιάζει στην μπάρα αναζήτησης κατα την πληκτρολόγηση ανεξαρτήτου
        # θέσεως.
        if self.searchbar != self.searchbar.focus_get():
            self.searchbar.focus()
            self.searchbar.insert("end", event.char)

        # Αναζήτηση
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

    def initialize_tree(self):
        """
        Αρχικοποιήσεις των στοιχείων του treeview και άλλου state που
        χρειάζεται για την ορθή λειτουργία.

        sort_state -> Θυμάται αν το τελευταίο sort ήταν φθήνων η αύξων
        maxlen-> Το μέγιστο μήκος των στοιχείων ανα στήλη για δυναμικό resize
        """
        # font = Font()
        # em = font.measure("m")
        self.sort_state = [False, False, False, False, False]
        self.tree["columns"] = ("id", "name", "surname", "phone", "email")
        self.maxlen = [10, 10, 10, 10, 10]

        for customer in self.customers:
            for i, name in enumerate(self.tree["columns"]):
                if len(str(getattr(customer, name))) > self.maxlen[i]:
                    self.maxlen[i] = len(str(getattr(customer, name)))

        for i in range(-1, 5):

            # Αυτά τα if είναι για να κρύψουν τα στοιχεία #0 και id. (width=0)
            # To #0 είναι του treeview, το id του Customer.
            if i < 0:
                self.tree.column("#0", width=0, stretch=False)
                self.tree.heading("#0", text="", anchor="w")
            elif i == 0:
                self.tree.column("id", width=0, stretch=False)
                self.tree.heading("id", text="id", anchor="w")
            else:

                # Το πλάτος της στήλης υπολογίζεται με βάση τις μεγαλύτερες
                # εγγραφές ανα στήλη.
                self.tree.column(
                    self.tree["columns"][i], width=self.maxlen[i] * 11, stretch=False
                )
                self.tree.heading(
                    self.tree["columns"][i],
                    text=self.tree["columns"][i].title(),
                    anchor="w",
                )

        self.populate_tree()

    def reset_tree(self, filter=None, hard_reset=False):
        """
        Αδειάζει το δέντρο για ανανέωση των στοιχείων
        όταν κάνει sort/search/update κλπ
        """
        self.focus()
        self.tree.delete(*self.tree.get_children())

        # Με το hard_reset flag ξανακάνει query από την βάση
        # δεδομένων. Χρήσιμο αν έχει προστεθεί κάποιος καινούριος
        # πελάτης, επειδή πρέπει να μπει στην βάση δεδομένων για
        # να πάρει id.
        if hard_reset:
            self.customers = self.controller.get_customers()
        self.populate_tree(filter)

    def populate_tree(self, filter=None):
        """
        Γεμίζει το δέντρο που άδειασε η reset_tree. Το filter
        απλά δεν επιτρέπει αθέμητη ανανέωση κάποιων στοιχείων,
        πχ στην περίπτωση που έχουμε διαγραφή πελάτη.
        """
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
        """
        Ορίζει την περιοχή που το mouse click τρέχει την sort
        """
        # To mouse click στο column header, δεν επιστρέφει value. Έτσι
        # προσδιορίζουμε τον χώρο.
        self.tree_identify(event)
        if not self.value_focus:
            self.sort()

    # Create Customer
    def open_customer_pop_up(self, prefill={}, edit_mode=False):
        """
        Δημιουργεί ένα pop up που επιτρέπει την επεξεργασία/προσθήκη
        πελατών. Έχει ελαφρώς διαφορετική συμπεριφορά ανάλογα ποιος
        το καλέι (create_customer, update_customer)
        """
        self.popup = tk.Toplevel(self)
        name_entry = ttk.Entry(self.popup, name="name")
        surname_entry = ttk.Entry(self.popup, name="surname")
        phone_entry = ttk.Entry(self.popup, name="phone")
        email_entry = ttk.Entry(self.popup, name="email")

        self.popup.title("Add Customer")
        self.popup.geometry("250x400")

        # Η prefill απλά βάζει γεμίζει τα ttk.Entry widgets με κάποια
        # default πληροφορία που την ορίζει η καλλούσα
        name_entry.insert(0, prefill.get("name") or "Enter name...")
        surname_entry.insert(0, prefill.get("surname") or "Enter surname...")
        phone_entry.insert(0, prefill.get("phone") or "Enter phone...")
        email_entry.insert(0, prefill.get("email") or "Enter email...")

        # Εδώ γίνεται η επιλογή μεταξύ λειτουργίας create και update.
        if edit_mode:
            callback = self.update_customer
        else:
            callback = self.create_customer
        email_entry.bind("<Return>", lambda _: callback(initialize=False))
        button = ttk.Button(
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
        """
        Δημιουργεί εναν νεον πελατη. Κάνει validate τα στοιχεία πρώτα
        και ζητάει επανάληψη της εγγραφης.
        """
        # Επειδή θα γίνει επανάληψη με αναδρομή, αυτό το flag σταματάει
        # το πρόγραμμα από το να φτιάξει νέο popup.
        if initialize:
            self.open_customer_pop_up(prefill)

        # Παίρνουμε τα δεδομένα από τα ttk.Entries του popup.
        children = self.popup.winfo_children()
        entries = filter(lambda x: isinstance(x, ttk.Entry), children)

        customer = {}
        for entry in entries:
            customer[entry.winfo_name()] = entry.get()  # type: ignore

        # Ελέγχουμε αν τα δεδομένα είναι συμβατά με την οντότητα Customer
        # Αν όχι ξανακάνουμε την διαδικασία από την αρχή.
        if not self.controller.validate_customer(customer):
            showerror("Error", "Make sure to include all fields")
            self.popup.destroy()
            self.create_customer(customer)
            return

        # Αποδέσμευση μνήμης, ενημέρωση βάσης και ανανέωση του treeview.
        self.popup.destroy()
        showinfo("Success", "Customer added successfully")
        self.controller.create_customer(customer, threaded=False)
        self.reset_tree(hard_reset=True)

    def delete_customer(self):
        """
        Σβήσιμο του επιλεγμένου πελάτη. Ρωτάει πριν ολοκληρώσει την
        διαγραφή.
        """

        # Απλός αλγόριθμος που απλά σβήνει μια εγγραφή με βάση το id
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
        """
        Αλλάζει τα στοιχεία του πελατη. Κάνει validate τα στοιχεία πρώτα
        και ζητάει επανάληψη της εγγραφης.
        """
        # Το μόνο που κάνει αυτό το κομμάτι είναι να αρχικοποιήσει το pop-up
        # με τα στοιχεία του επιλεγμένου πελάτη.
        if initialize:
            prefill = dict(zip(self.tree["columns"][1:], self.value_focus[1:]))
            self.open_customer_pop_up(prefill, edit_mode=True)

        # Ίδια διαδικασία με create.
        entries: Iterator[ttk.Entry] = filter(
            lambda x: isinstance(x, ttk.Entry), self.popup.winfo_children()  # type: ignore
        )

        customer = {}
        for entry in entries:
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
