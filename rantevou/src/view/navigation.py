import tkinter as tk


class GoToButton(tk.Button):
    def __init__(self, parent, text, root, frame_name):
        tk.Button.__init__(
            self,
            parent,
            text=text,
            command=lambda: root.change_frame(frame_name),
        )
