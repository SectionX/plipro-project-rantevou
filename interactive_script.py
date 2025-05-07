from rantevou.src.model.appointment import AppointmentModel, Appointment
from time import perf_counter
from rantevou.src.controller.logging import Logger

Logger.level = 4

model = AppointmentModel()
session = model.session


start = perf_counter()
for _ in range(1000):
    model.get_appointments()
print(perf_counter() - start)


start = perf_counter()
for _ in range(1000):
    session.query(Appointment).all()
print(perf_counter() - start)
