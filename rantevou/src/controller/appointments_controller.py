from .logging import logger

from ..model.session import SessionLocal
from ..model.appointment import Appointment


class AppointmentControl:
    def __init__(self):
        self.session = SessionLocal()
        self.appointment = Appointment

    def get_appointments(self):
        return self.session.query(self.appointment).all()

    def create_appointment(self, appointment):
        self.session.add(appointment)
        self.session.commit()

    def delete_appointment(self, appointment):
        self.session.delete(appointment)
        self.session.commit()

    def update_appointment(self, appointment):
        old_appointment = (
            self.session.query(Appointment).filter_by(id=appointment.id).first()
        )
        if old_appointment:
            old_appointment.date = appointment.date
            old_appointment.customer_id = appointment.customer_id
        self.session.commit()

    def get_appointment_by_id(self, id):
        return self.session.query(self.appointment).filter_by(id=id).first()
