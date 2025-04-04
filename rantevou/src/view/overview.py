import tkinter as tk
from .navigation import GoToButton


class Overview(tk.Frame):
    def __init__(self, root):
        tk.Frame.__init__(self, root)
        self.root = root
        self.name = "overview"

    def initialize(self, frames):
        buttons = [
            GoToButton(self, name.title(), self.root, name)
            for name in frames
            if name != "overview"
        ]
        for i in range(0, 2):
            for j in range(0, 2):
                self.grid_columnconfigure(i, weight=1)
                self.grid_rowconfigure(j, weight=1)
        buttons[0].grid(row=0, column=0, sticky="nsew")
        buttons[1].grid(row=0, column=1, sticky="nsew")
        buttons[2].grid(row=1, column=0, stick="nsew")
        buttons[3].grid(row=1, column=1, sticky="nsew")
