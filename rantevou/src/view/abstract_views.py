from abc import abstractmethod
import tkinter as tk
from .navigation import GoToButton
from .window import Window


class Header(tk.Frame):
    """
    Header για όλα τα frames που κληρονομούν το AppFrame
    """

    def __init__(self, parent: tk.Frame, root: Window, *args, **kwargs):
        tk.Frame.__init__(
            self, parent, *args, height=20, border=1, borderwidth=1, **kwargs
        )


class Footer(tk.Frame):
    """
    Footer για όλα τα frames που κληρονομούν το AppFrame
    """

    def __init__(self, parent: tk.Frame, root: Window, *args, **kwargs):
        tk.Frame.__init__(
            self, parent, *args, height=100, border=1, borderwidth=1, **kwargs
        )
        GoToButton(self, "Back to Overview", root, "overview").pack(side=tk.RIGHT)


class BodyFrame(tk.Frame):
    """
    Άδειο frame στο οποίο φέρει την επιχειρησιακή λογική του
    κάθε AppFrame. Προγραμματίζεται στην μέθοδο body_logic του
    AppFrame.
    """

    def __init__(self, parent: tk.Frame, root: Window, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)


class AppFrame(tk.Frame):
    def __init__(self, root: Window, name: str):
        tk.Frame.__init__(self, root)
        self.name = name
        self.root = root

        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        self.header = Header(self.container, self.root)
        self.body = BodyFrame(self.container, self.root, background="white")
        self.footer = Footer(self.container, self.root)

        self.initialize_header()
        self.initialize_body()
        self.initialize_footer()

    def initialize_header(self) -> None:
        self.header.pack(fill="x")

    def initialize_footer(self) -> None:
        self.footer.pack(fill="x")

    def initialize_body(self) -> None:
        self.body_logic()
        self.body.pack(fill="both", expand=True)

    @abstractmethod
    def body_logic(self):
        raise NotImplementedError
