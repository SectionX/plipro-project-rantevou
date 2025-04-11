from rantevou.src.controller.mailer import Mailer
from rantevou.src.controller.appointments_controller import AppointmentControl
from rantevou.src.controller.customers_controller import CustomerControl

mlr = Mailer()
ac = AppointmentControl()
cc = CustomerControl()

# from datetime import datetime, timedelta

# print(
#     *ac.get_appointment_grouped_in_periods(
#         datetime.now().replace(hour=9, minute=0, second=0, microsecond=0),
#         timedelta(hours=2),
#     ),
#     sep="\n",
# )
