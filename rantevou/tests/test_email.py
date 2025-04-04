from ..src.controller.mailer import Mailer
from ..src.model.customer import Customer
from ..src.model.appointment import Appointment
from datetime import datetime


# def test_email():
#     session = initialize_db()
#     with TestSession() as session:
#         appointments = session.query(Appointment).all()

#     mailer = Mailer()
#     mailer.send_email(appointments, debug=True)
