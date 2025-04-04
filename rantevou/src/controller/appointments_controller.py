from ..model.session import SessionLocal
from ..model.appointment import Appointment


class AppointmentControl:
    """
    Διαχειρίζεται όλες τις ενέργειες που απαιτούν στοιχεία από
    το table Appointments
    """

    def __init__(self):
        self.session = SessionLocal()
        self.appointment = Appointment

    def get_appointments(self) -> list[Appointment]:
        """
        Επιστρέφει όλες τις εγγραφές από το table Appointments
        """
        return self.session.query(self.appointment).all()

    def create_appointment(self, appointment: Appointment) -> None:
        """
        Προσθέτει καινούρια εγγραφή στο table Appointments
        """
        self.session.add(appointment)
        self.session.commit()

    def delete_appointment(self, appointment: Appointment) -> None:
        """
        Σβήνει μια εγγραφή από το table Appointments
        """
        self.session.delete(appointment)
        self.session.commit()

    def update_appointment(self, appointment: Appointment) -> None:
        """
        Μεταβάλλει τα στοιχεία μιας εγγραφής στο table Appointments
        """
        old_appointment = (
            self.session.query(Appointment).filter_by(id=appointment.id).first()
        )
        if old_appointment:
            old_appointment.date = appointment.date
            old_appointment.customer_id = appointment.customer_id
        self.session.commit()

    def get_appointment_by_id(self, id) -> Appointment | None:
        """
        Επιστρέφει μια εγγραφή με βάση το id από το table Appointments
        """
        return self.session.query(self.appointment).filter_by(id=id).first()
