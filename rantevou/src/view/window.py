import tkinter as tk
from .overview import create_overview
from .appointments import create_appointments_view


class Window(tk.Tk):

    create_frame = {
        "overview": create_overview,
        "appointments": create_appointments_view,
    }

    def __init__(self, title="Appointments App", width=800, height=600):
        super().__init__()
        self.title(title)
        self.geometry(f"{width}x{height}")

        self.windowframe = create_overview(self)
        self.windowframe.pack(fill="both", expand=True)

    def change_frame(self, frame_name):
        self.windowframe.destroy()
        self.windowframe = self.create_frame[frame_name](self)
        self.windowframe.pack(fill="both", expand=True)

    def run(self):
        self.mainloop()
