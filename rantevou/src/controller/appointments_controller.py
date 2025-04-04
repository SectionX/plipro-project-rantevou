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
        pass

    def get_appointment_by_id(self, id):
        return self.session.query(self.appointment).filter_by(id=id).first()
