import pathlib
import smtplib
from email.mime.text import MIMEText
from ..model.session import SessionLocal
from ..model.customer import Customer
from ..model.appointment import Appointment

PATH_TO_EMAIL = pathlib.Path(__file__).parent.parent.parent / "data" / "email_body.txt"


class Mailer:

    def __init__(self):
        """
        Αφήνω τα στοιχεία πρόσβασης στον κώδικα επειδή αυτό το email
        δεν θα χρησιμοποιηθεί για κάτι άλλο. Δίνω 10 ευρώ σε όποιον
        τα κλέψει!
        """

    def start_server(self):
        self.server = smtplib.SMTP("smtp.gmail.com", 587)
        self.server.starttls()
        self.server.login(
            "plipro.hle55.team3@gmail.com", "lpri ryfl pdjr hlef"
        )  # App Password

    def send_email(self, appointments, debug=False):
        self.start_server()
        ids = (appointment.customer_id for appointment in appointments)

        with PATH_TO_EMAIL.open() as f:
            body = f.read()

        with SessionLocal() as session:
            result = (
                session.query(Customer, Appointment).join(Appointment)
                # .filter_by(Customer.id.in_(ids))
                .all()
            )
        print(result)

        for customer, appointment in result:
            email = MIMEText(body.format(customer.name, appointment.date))
            email["from"] = "plipro.hle55.team3@gmail.com"
            email["to"] = "underburningsky@gmail.com"
            email["subject"] = "Φιλική Υπενθύμηση"
            if debug:
                print(body.format(customer.name, appointment.date))
            else:
                self.server.sendmail(
                    "plipro.hle55.team3@gmail.com",
                    "underburningsky@gmail.com",
                    email.as_string(),
                )

        self.server.quit()
