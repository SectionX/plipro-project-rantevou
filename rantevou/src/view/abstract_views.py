import tkinter as tk
from .navigation import GoToButton


class Header(tk.Frame):
    def __init__(self, parent, root, *args, **kwargs):
        tk.Frame.__init__(
            self, parent, *args, height=20, border=1, borderwidth=1, **kwargs
        )


class Footer(tk.Frame):
    def __init__(self, parent, root, *args, **kwargs):
        tk.Frame.__init__(
            self, parent, *args, height=100, border=1, borderwidth=1, **kwargs
        )
        GoToButton(self, "Back to Overview", root, "overview").pack(side=tk.RIGHT)


class BodyFrame(tk.Frame):
    def __init__(self, parent, root, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)


class AppFrame(tk.Frame):
    def __init__(self, root, name):
        tk.Frame.__init__(self, root)
        self.name = name
        self.root = root

        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        self.header = Header(self.container, self.root)
        self.header.pack(fill="x")

        self.body = BodyFrame(self.container, self.root, background="white")
        self.body.pack(fill="both", expand=True)

        self.footer = Footer(self.container, self.root)
        self.footer.pack(fill="x")
