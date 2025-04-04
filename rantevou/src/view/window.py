import tkinter as tk
from .overview import create_overview


class Window(tk.Tk):
    def __init__(self, title="Appointments App", width=800, height=600):
        super().__init__()
        self.title(title)
        self.geometry(f"{width}x{height}")

        self.windowframe = create_overview(self)
        self.windowframe.pack(fill="both", expand=True)

    def change_frame(self, frame):
        self.windowframe.destroy()
        self.windowframe = frame
        self.windowframe.pack(fill="both", expand=True)

    def run(self):
        self.mainloop()


root = Window()
