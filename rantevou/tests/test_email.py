from rantevou.src.controller.mailer import Mailer
from rantevou.src.controller.appointments_controller import AppointmentControl


def test_mailer_works():
    mlr = Mailer()
    ac = AppointmentControl()
    aps = ac.get_appointments()
    mlr._send_email(aps, debug=True)
