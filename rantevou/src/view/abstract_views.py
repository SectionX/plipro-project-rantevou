"""
Συλλογή από class και interface που εξυπηρετούν τα διάφορα widgets
της εφαρμογής. Πολλά από αυτά είναι απομεινάρια από τις πρώτες υλοποιήσεις
και δεν έχουν κάποια χρησιμότητα πλέον.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any, Protocol


class PopUp(tk.Toplevel):
    """
    Δημιουργεί ένα pop-up. Παλιά υλοποίηση που δεν χρησιμοποιείται
    πλέον.
    """

    def __init__(self, parent, *args, **kwargs):
        tk.Toplevel.__init__(self, parent, *args, **kwargs)
        self.AppContext = parent.AppContext


class Header(ttk.Frame):
    """
    Header για όλα τα frames που κληρονομούν το AppFrame
    """

    def __init__(self, parent: tk.Frame, *args, **kwargs):
        super().__init__(parent, *args, height=20, border=1, borderwidth=1, **kwargs)


class Footer(ttk.Frame):
    """
    Footer για όλα τα frames που κληρονομούν το AppFrame
    """

    def __init__(self, parent: tk.Frame, root: tk.Tk, *args, **kwargs):
        super().__init__(parent, *args, height=100, border=1, borderwidth=1, **kwargs)
        tk.Button(self, text="Back to Overview", command=parent.pack_forget).pack(side=tk.RIGHT)


class BodyFrame(ttk.Frame):
    """
    Άδειο frame στο οποίο φέρει την επιχειρησιακή λογική του
    κάθε AppFrame. Προγραμματίζεται στην μέθοδο body_logic του
    AppFrame.
    """

    def __init__(self, parent: tk.Frame, root: tk.Tk, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)


class AppFrame(ttk.Frame):
    def __init__(self, root, *args, **kwargs):
        super().__init__(root, *args, **kwargs)
        """
        Σκοπός της κλάσσης είναι να κληρονομεί μερικά χαρακτηριστικά
        που θέλουμε να υπάρχουν σε όλα τα panels, όπως header/footer.
        
        Επίσης μπορούμε να υλοποιήσουμε λογική που λείπει από το tk.
        """

    def get_all_children(self, root=None, filter=None):
        """
        Αργόριθμος αναζήτησης δέντρου για την εύρεση όλων των
        παιδιών του κάποιου root node. Μετά από πολύ αναζήτηση
        φαίνεται ότι το tk δεν έχει κάποια σχετική μέθοδο.

        Υλοποίηση με stack για να γλυτώσουμε την αναδρομή που
        είναι εξαιρετικά αργή στην Python.
        """
        if root is None:
            root = self

        stack = [root]
        self.all_children = []

        while stack:
            child = stack.pop()
            if filter is None:
                self.all_children.append(child)
            else:
                if filter(child):
                    self.all_children.append(child)
            stack.extend(child.winfo_children())

        return self.all_children


class EntryWithPlaceholder(ttk.Entry):
    """
    Αναβάθμιση του βασικού Entry widget να δείχνει placeholder κείμενο
    στον χρήστη.
    """

    def __init__(self, master, placeholder: str, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.placeholder = placeholder
        self.bind("<Button-1>", lambda x: self.clear())
        self.config(width=4)

    def put_placeholder(self):
        self.insert(0, self.placeholder)

    def clear(self):
        text = self.get()
        if text == self.placeholder:
            self.delete(0, tk.END)

    def get_without_placeholder(self):
        text = self.get()
        if text == self.placeholder:
            return None
        return text


class SideView(ttk.Frame):
    """
    Ο γονέας όλων των panels που εμφανίζονται στο SidePanel. Ορίζει τις βοηθητικές
    συναρτήσεις "set_title" και "add_back_button" που θέλουν να χρησιμοποιούν όλα
    τα panels.

    Κάθε παιδί πρέπει να υλοποιεί την μέθοδο "update_content" που καλεί το SidePanel
    όταν αλλάζει το panel μετά από εντολή κάποιου άλλου component όπως το παράδειγμα
    που δώσαμε στην επεξήγηση του SidePanel.

    Η συνήθης χρήση για την υλοποίηση είναι να λάβουμε τα στοιχεία από το SidePanel
    και να τα εμφανίσουμε. Π.χ.

    def update_content(self):
        caller_data = SidePanel.fetch_data("caller_data")
        label = ttk.Label(self, text=str(caller_data))
        label.pack()
    """

    name: str = ""
    data: Any
    header: ttk.Label
    back_btn: ttk.Button
    sidepanel: SidePanel

    def __init__(self, root, *args, **kwargs):
        super().__init__(root, *args, **kwargs)
        self.root = root
        self.config(style="primary.TFrame")
        self.sidepanel = self.nametowidget(".!sidepanel")

        btnframe = ttk.Frame(self)
        btnframe.pack(side=tk.BOTTOM, fill="x")
        self.back_btn = ttk.Button(btnframe, text="Back", command=self.sidepanel.go_back)
        self.back_btn.pack(side=tk.RIGHT)

    def update_content(self, caller: Any | None, caller_data: Any | None):
        ...
        raise NotImplementedError

    def set_title(self, text: str):
        if hasattr(self, "header"):
            self.header.config(text=text)
            return
        self.header = ttk.Label(self, text=text)
        self.header.pack(side=tk.TOP, fill="x")


class Caller(tk.Widget):
    """
    Κλάσση διεπαφής για όλα τα widgets που καλούν sideviews
    στο sidepanel.
    """

    def __init__(self):
        self.sidepanel: SidePanel = self.nametowidget(".!sidepanel")

    def show_in_sidepanel(self): ...


# Τύποι (μη ολοκληρωμένη υλοποίηση)


class SidePanel(Protocol):
    def select_view(self, name: str, caller: Any | None = None, caller_data: Any | None = None):
        pass

    def go_back(self):
        pass


class AlertsView(SideView):
    pass


class AppointmentView(SideView):
    pass


class EditCustomerView(SideView):
    pass


class AddCustomerView(SideView):
    pass


class SearchResultsView(SideView):
    pass


class EditAppointmentView(SideView):
    pass


class AddAppointmentView(SideView):
    pass
