# TODO: Ιδανικά για κάθε συνάρτηση θέλουμε και διαγνωστικά logs

import pathlib
import smtplib
from threading import Thread
from email.mime.text import MIMEText

from ..model.session import SessionLocal
from ..model.customer import Customer
from ..model.appointment import Appointment
from .logging import Logger

PATH_TO_EMAIL = pathlib.Path(__file__).parent.parent.parent / "data" / "email_body.txt"

logger = Logger()


class Mailer:

    def start_server(self) -> None:
        """
        Αφήνω τα στοιχεία πρόσβασης στον κώδικα επειδή αυτό το email
        δεν θα χρησιμοποιηθεί για κάτι άλλο. Δίνω 10 ευρώ σε όποιον
        τα κλέψει!
        """
        self.server = smtplib.SMTP("smtp.gmail.com", 587)
        self.server.starttls()
        self.server.login(
            "plipro.hle55.team3@gmail.com", "lpri ryfl pdjr hlef"
        )  # App Password, δεν είναι ο πραγματικός κωδικός.

<<<<<<< HEAD
=======
    # TODO αλλαγή σε debug=False όταν ολοκληρωθεί και τεσταριστεί το πρόγραμμα
>>>>>>> dev-stouraitis
    def send_email(self, appointments, debug=False) -> None:
        """
        Ασύγχρονο κάλεσμα στην _send_email για να μην κλειδώνει το προγραμμα
        περιμένοντας την ανταπόκριση δικτύου.
        """
        Thread(target=self._send_email, args=(appointments, debug)).start()

    def _send_email(self, appointments, debug=False):
        """
        Βρίσκει τους πελάτες που αντιστοιχούν στα ραντεβού και τους
        στέλνει email
        """
        self.start_server()
        ids = (appointment.customer_id for appointment in appointments)

        with PATH_TO_EMAIL.open() as f:
            body = f.read()

        with SessionLocal() as session:
            result = (
                session.query(Customer, Appointment)
                .join(Appointment)
                .filter(Customer.id.in_(ids))
                .all()
            )

        # TODO πρέπει να γίνει σωστό format του appointment.date
        # TODO επίσης πρέπει να γραφτεί καλύτερο μήνυμα email
        customer: Customer
        appointment: Appointment
        for customer, appointment in result:
            email = MIMEText(body.format(customer.name, appointment.date))
            email["from"] = "plipro.hle55.team3@gmail.com"
            email["to"] = customer.email
            email["subject"] = "Φιλική Υπενθύμηση"
            if debug:
                logger.log_debug(body.format(customer.name, appointment.date))
            else:
                self.server.sendmail(
                    "plipro.hle55.team3@gmail.com",
                    customer.email,
                    email.as_string(),
                )

        self.server.quit()
