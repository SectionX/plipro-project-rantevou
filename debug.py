from rantevou.src.controller.logging import Logger
from rantevou import __main__

from sqlalchemy import func, select

from rantevou.src.model.types import Appointment
from rantevou.src.controller import AppointmentControl, CustomerControl, get_config
from rantevou.src.view.appointments import AppointmentsTab
from tkinter import Tk

from datetime import datetime, timedelta


from time import perf_counter

ac = AppointmentControl()
model = ac.model

start = perf_counter()

print(model.session.query(func.max(Appointment.id)).scalar())


# print(
#     len(
#         list(
#             ac.get_appointments_from_to_date(
#                 datetime.now(), datetime.now() + timedelta(days=30)
#             )
#         )
#     )
# )


print(perf_counter() - start)
