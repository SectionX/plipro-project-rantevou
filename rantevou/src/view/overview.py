import tkinter as tk


class Overview(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        go_to_appointments = tk.Button(
            self,
            text="Appointments",
            command=lambda: parent.change_frame("appointments"),
        )
        go_to_appointments.pack()


def create_overview(parent):
    return Overview(parent)
