import tkinter as tk


class PopUp(tk.Toplevel):
    def __init__(self, parent, *args, **kwargs):
        tk.Toplevel.__init__(self, parent, *args, **kwargs)
        self.AppContext = parent.AppContext


class Header(tk.Frame):
    """
    Header για όλα τα frames που κληρονομούν το AppFrame
    """

    def __init__(self, parent: tk.Frame, *args, **kwargs):
        tk.Frame.__init__(
            self, parent, *args, height=20, border=1, borderwidth=1, **kwargs
        )


class Footer(tk.Frame):
    """
    Footer για όλα τα frames που κληρονομούν το AppFrame
    """

    def __init__(self, parent: tk.Frame, root: tk.Tk, *args, **kwargs):
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

    def __init__(self, parent: tk.Frame, root: tk.Tk, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)


class AppFrame(tk.Frame):
    def __init__(self, root: tk.Tk):
        tk.Frame.__init__(self, root)
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
