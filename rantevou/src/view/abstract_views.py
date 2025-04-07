import tkinter as tk
<<<<<<< HEAD
from .navigation import GoToButton
from .window import Window
=======
>>>>>>> dev-stouraitis


class PopUp(tk.Toplevel):
    def __init__(self, parent, *args, **kwargs):
        tk.Toplevel.__init__(self, parent, *args, **kwargs)
        self.AppContext = parent.AppContext


class Header(tk.Frame):
    """
    Header για όλα τα frames που κληρονομούν το AppFrame
    """

<<<<<<< HEAD
    def __init__(self, parent: tk.Frame, root: Window, *args, **kwargs):
=======
    def __init__(self, parent: tk.Frame, *args, **kwargs):
>>>>>>> dev-stouraitis
        tk.Frame.__init__(
            self, parent, *args, height=20, border=1, borderwidth=1, **kwargs
        )


class Footer(tk.Frame):
    """
    Footer για όλα τα frames που κληρονομούν το AppFrame
    """

<<<<<<< HEAD
    def __init__(self, parent: tk.Frame, root: Window, *args, **kwargs):
=======
    def __init__(self, parent: tk.Frame, root: tk.Tk, *args, **kwargs):
>>>>>>> dev-stouraitis
        tk.Frame.__init__(
            self, parent, *args, height=100, border=1, borderwidth=1, **kwargs
        )
        tk.Button(self, text="Back to Overview", command=parent.pack_forget).pack(
            side=tk.RIGHT
        )


class BodyFrame(tk.Frame):
    """
    Άδειο frame στο οποίο φέρει την επιχειρησιακή λογική του
    κάθε AppFrame. Προγραμματίζεται στην μέθοδο body_logic του
    AppFrame.
    """

<<<<<<< HEAD
    def __init__(self, parent: tk.Frame, root: Window, *args, **kwargs):
=======
    def __init__(self, parent: tk.Frame, root: tk.Tk, *args, **kwargs):
>>>>>>> dev-stouraitis
        tk.Frame.__init__(self, parent, *args, **kwargs)


class AppFrame(tk.Frame):
<<<<<<< HEAD
    def __init__(self, root: Window, name: str):
        tk.Frame.__init__(self, root)
        self.name = name
        self.root = root
        self.AppContext = root.AppContext
=======
    def __init__(self, root: tk.Tk):
        tk.Frame.__init__(self, root)
        """
        Σκοπός της κλάσσης είναι να κληρονομεί μερικά χαρακτηριστικά
        που θέλουμε να υπάρχουν σε όλα τα panels, όπως header/footer.
        
        Επίσης μπορούμε να υλοποιήσουμε λογική που λείπει από το tk.
        """
>>>>>>> dev-stouraitis

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

<<<<<<< HEAD
    def initialize_header(self) -> None:
        self.header.pack(fill="x")

    def initialize_footer(self) -> None:
        self.footer.pack(fill="x")

    def initialize_body(self) -> None:
        self.body.pack(fill="both", expand=True)

    def initialize(self):
        self.initialize_header()
        self.initialize_body()
        self.initialize_footer()
=======
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
>>>>>>> dev-stouraitis
