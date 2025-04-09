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

logger = Logger("Mailer")


class Mailer:

    def start_server(self) -> None:
        """
        Αφήνω τα στοιχεία πρόσβασης στον κώδικα επειδή αυτό το email
        δεν θα χρησιμοποιηθεί για κάτι άλλο. Δίνω 10 ευρώ σε όποιον
        τα κλέψει!
        """
        logger.log_info("Connecting to smtp")
        self.server = smtplib.SMTP("smtp.gmail.com", 587)
        self.server.starttls()
        self.server.login(
            "plipro.hle55.team3@gmail.com", "lpri ryfl pdjr hlef"
        )  # App Password, δεν είναι ο πραγματικός κωδικός.

    # TODO αλλαγή σε debug=False όταν ολοκληρωθεί και τεσταριστεί το πρόγραμμα
    def send_email(self, appointments, debug=False) -> None:
        """
        Ασύγχρονο κάλεσμα στην _send_email για να μην κλειδώνει το προγραμμα
        περιμένοντας την ανταπόκριση δικτύου.
        """
        logger.log_info(f"Sending emails to {len(appointments)} recipients")
        Thread(target=self._send_email, args=(appointments, debug), daemon=True).start()
        import time

        time.sleep(5)

    def _send_email(self, appointments: list[Appointment], debug=False):
        """
        Βρίσκει τους πελάτες που αντιστοιχούν στα ραντεβού και τους
        στέλνει email
        """
        print(appointments)
        if debug:
            logger.log_info("Debug mode enabled, emails won't reach the recipient")
        self.start_server()
        with PATH_TO_EMAIL.open() as f:
            body = f.read()

        # TODO πρέπει να γίνει σωστό format του appointment.date
        # TODO επίσης πρέπει να γραφτεί καλύτερο μήνυμα email
        for appointment in appointments:
            customer = appointment.get_customer()
            if customer is None:
                continue
            date = appointment.date.strftime("%d/%m και ώρα %H:%M")
            logger.log_info(f"Mailing to {customer.email}")

            email = MIMEText(body.format(customer.name, date))
            email["from"] = "plipro.hle55.team3@gmail.com"
            email["to"] = customer.email
            email["subject"] = "Φιλική Υπενθύμηση"

            if debug:
                logger.log_info(body.format(customer.name, date))
            else:
                self.server.sendmail(
                    "plipro.hle55.team3@gmail.com",
                    customer.email,
                    email.as_string(),
                )

        self.server.quit()
