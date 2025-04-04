import tkinter as tk


class Window(tk.Tk):

    def __init__(self, title="Appointments App", width=800, height=600):
        super().__init__()
        self.geometry(f"{width}x{height}")
        self.title(title)

    def initialize_frames(self, frame_dict):
        self.children = frame_dict
        overview = next(iter(self.children.values()))
        overview.initialize()  # type: ignore

        self.windowframe = self.children["overview"]
        self.windowframe.pack(fill="both", expand=True)

    def change_frame(self, frame_name):
        self.windowframe.forget()
        self.windowframe = self.children[frame_name]
        self.windowframe.pack(fill="both", expand=True)

    def run(self):
        self.mainloop()
        self.destroy()
