from ..model.session import SessionLocal
from ..model.types import Appointment

# TODO: Η υλοποίηση σε αυτές τις συναρτήσεις είναι ενδεικτική
# TODO: Ιδανικά για κάθε συνάρτηση θέλουμε και διαγνωστικά logs
# TODO: Πρέπει να αλλαχθεί το πρόγραμμα ώστε κάθε φορά που ολοκληρώνονται οι
#       διαδικασιες του session, να κλείνει (session.close()). Ο λόγος που
#       έγινε έτσι ήταν θέμα ταχύτητας, δουλεύει, αλλά δημιουργεί και προβλήματα
#       μερικές φορές, ειδικά επειδή η sqlite δεν είναι ασύγχρονη.


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

<<<<<<< HEAD
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
=======
    def create_appointment(self, appointment: Appointment | dict) -> None:
        """
        Προσθέτει καινούρια εγγραφή στο table Appointments
        """
        # TODO Η υλοποίηση είναι ενδεικτική. Θέλουμε να υποστηρίζει
        # και Appointment Class και dictionary ως παράμετρο

        if not self.validate_appointment(appointment):
            raise ValueError
        self.session.add(appointment)
        self.session.commit()

    def delete_appointment(self, appointment: Appointment | dict | int) -> None:
        """
        Σβήνει μια εγγραφή από το table Appointments
        """
        # TODO Η υλοποίηση είναι ενδεικτική. Θέλουμε να υποστηρίζει
        # Appointment Class, dictionary ή integer (id)ως παράμετρο
        self.session.delete(appointment)
        self.session.commit()

    def update_appointment(self, appointment: Appointment | dict) -> None:
        """
        Μεταβάλλει τα στοιχεία μιας εγγραφής στο table Appointments
        """
        # TODO Η υλοποίηση είναι ενδεικτική. Θέλουμε να υποστηρίζει
        # Appointment Class και dictionary ως παράμετρο
>>>>>>> dev-stouraitis
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

    def validate_appointment(self, appointment: Appointment | dict) -> bool:
        """
        Ελέγχει ότι τα στοιχεία της εγγραφής ειναι σωστά και ότι
        δεν μπαίνει καινούριο ραντεβού σε περιόδο που είναι ήδη
        γεμάτη.
        """
        # TODO λείπει όλη η υλοποίηση
        return True
