from rantevou.src.controller.logging import Logger
from rantevou import __main__


from rantevou.src.controller import AppointmentControl, CustomerControl, get_config
from rantevou.src.view.appointments import AppointmentsTab
from tkinter import Tk

root = Tk()
AppointmentsTab(root)

root.mainloop()
