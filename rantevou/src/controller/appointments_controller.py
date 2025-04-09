from datetime import datetime, timedelta
from typing import NamedTuple
from .logging import Logger
from ..model.session import SessionLocal
from ..model.types import Appointment

# TODO: Η υλοποίηση σε αυτές τις συναρτήσεις είναι ενδεικτική
# TODO: Ιδανικά για κάθε συνάρτηση θέλουμε και διαγνωστικά logs
# TODO: Πρέπει να αλλαχθεί το πρόγραμμα ώστε κάθε φορά που ολοκληρώνονται οι
#       διαδικασιες του session, να κλείνει (session.close()). Ο λόγος που
#       έγινε έτσι ήταν θέμα ταχύτητας, δουλεύει, αλλά δημιουργεί και προβλήματα
#       μερικές φορές, ειδικά επειδή η sqlite δεν είναι ασύγχρονη.

logger = Logger("appointments_controller")


class AppointmentGroup(NamedTuple):
    order: int
    start_date: datetime
    end_date: datetime
    length: int
    appointments: tuple[Appointment, ...]


class AppointmentControl:
    """
    Διαχειρίζεται όλες τις ενέργειες που απαιτούν στοιχεία από
    το table Appointments
    """

    def __init__(self):
        self.session = SessionLocal()

    def get_appointments(self) -> list[Appointment]:
        """
        Επιστρέφει όλες τις εγγραφές από το table Appointments
        """
        return self.session.query(Appointment).all()

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

    def delete_appointment(self, appointment: Appointment | dict | int) -> bool:
        """
        Σβήνει μια εγγραφή από το table Appointments
        """
        if isinstance(appointment, int):
            full_appointment = (
                self.session.query(Appointment).filter_by(id=appointment).first()
            )
            if full_appointment:
                appointment = full_appointment
            else:
                return False

        if isinstance(appointment, dict):
            try:
                appointment = Appointment(**appointment)
            except Exception as e:
                logger.log_warn(str(e))
                return False

        self.session.delete(appointment)

        try:
            self.session.commit()
        except Exception as e:
            return False

        return True

    def update_appointment(self, appointment: Appointment | dict) -> bool:
        """
        Μεταβάλλει τα στοιχεία μιας εγγραφής στο table Appointments
        """
        if isinstance(appointment, dict):
            try:
                appointment = Appointment(**appointment)
            except Exception as e:
                logger.log_warn(str(e))
                return False

        old_appointment = (
            self.session.query(Appointment).filter_by(id=appointment.id).first()
        )
        if old_appointment:
            old_appointment.date = appointment.date
            old_appointment.customer_id = appointment.customer_id

        try:
            self.session.commit()
            logger.log_info(f"Update of {appointment} complete")
        except Exception as e:
            logger.log_warn(str(e))
            return False
        return True

    def get_appointment_by_id(self, id: int) -> Appointment | None:
        """
        Επιστρέφει μια εγγραφή με βάση το id από το table Appointments
        """
        return self.session.query(Appointment).filter_by(id=id).first()

    def validate_appointment(self, appointment: Appointment | dict) -> bool:
        """
        Ελέγχει ότι τα στοιχεία της εγγραφής ειναι σωστά και ότι
        δεν μπαίνει καινούριο ραντεβού σε περιόδο που είναι ήδη
        γεμάτη.
        """
        # TODO λείπει όλη η υλοποίηση
        return True

    def get_appointments_grouped_in_periods(
        self,
        start: datetime,
        period: timedelta,
        end: datetime | None = None,
        appointments: list[Appointment] | None = None,
    ):
        if not appointments:
            appointments = (
                self.session.query(Appointment).filter(Appointment.date >= start).all()
            )
        if not appointments:
            return None
        appointments.sort(key=lambda x: x.date)

        order = 0

        if end is None:
            end = appointments[-1].date

        buffer: list[Appointment | None] = []

        app_ptr = 0
        while start < end:
            start += period
            while app_ptr < len(appointments):
                if appointments[app_ptr].date < start:
                    buffer.append(appointments[app_ptr])
                    app_ptr += 1
                else:
                    yield AppointmentGroup(
                        order=order,
                        start_date=start - period,
                        end_date=start,
                        length=len(buffer),
                        appointments=tuple(buffer),
                    )
                    buffer.clear()
                    order += 1
                    break

    def get_free_periods(self):
        appointments = iter(
            self.session.query(Appointment)
            .filter(Appointment.date > datetime.now())
            .all()
        )
        start = next(appointments)
        for appointment in appointments:
            yield (
                start,
                start.time_between_appointments(appointment),
            )
            start = appointment
