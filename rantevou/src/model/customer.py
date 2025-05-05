from __future__ import annotations

from unicodedata import normalize
from math import ceil

from sqlalchemy import func, or_, desc

from .session import session
from .interfaces import SubscriberInterface
from .entities import Customer
from ..controller.logging import Logger

logger = Logger("customer-model")


class CustomerModel:
    subscribers: list[SubscriberInterface]
    _instance = None
    session = session
    max_id: int

    def __new__(cls, *args, **kwargs) -> CustomerModel:
        if cls._instance is None:
            cls._instance = super(CustomerModel, cls).__new__(cls, *args, **kwargs)
            cls.subscribers = []
            max_id = cls.session.query(func.max(Customer.id)).scalar() or 0
            if isinstance(max_id, int):
                cls.max_id = max_id

        return cls._instance

    @property
    def customers(self) -> list[Customer]:
        return self.session.query(Customer).all()

    def sanitize(self, customer: Customer):
        """
        Μετατρέπει τα κενά strings σε None
        """
        for k, v in customer.__dict__.items():
            if k.startswith("_"):
                continue
            if isinstance(v, str) and v == "":
                customer.__dict__[k] = None

    def is_similar(self, customer1: Customer, customer2: Customer) -> bool:
        """
        Ελέγχει αν τα σημαντικά στοιχεία 2 πελατών είναι ίδια
        """
        return all(
            (
                customer1.name == customer2.name,
                customer1.surname == customer2.surname,
                customer1.phone == customer2.phone,
                customer1.email == customer2.email,
            )
        )

    def get_fields(self) -> list[str]:
        """
        Επιστρέφει τους τίτλους των στήλων
        """
        return ["id", "name", "surname", "phone", "email"]

    def filter_by_all(self, customer: Customer) -> Customer | None:
        """
        Ειδική συνάρτηση που ψάχνει έναν πελάτη στην βάση δεδομένων
        χωρίς την χρήση id
        """
        return (
            session.query(Customer)
            .filter(
                Customer.name == customer.name,
                Customer.surname == customer.surname,
                Customer.phone == customer.phone,
                Customer.email == customer.email,
            )
            .first()
        )

    def add_customer(self, customer: Customer) -> tuple[int | None, bool]:
        """
        Δημιουργία καινούριου πελάτη. Ελέγχει αν υπάρχει ήδη ο πελάτης
        πριν τον προσθέσει στην βάση δεδομένων. Ισότητα σημαίνει όλα τα
        πεδία είναι ίδια.

        Επιστρέφει πλειάδα tuple(customer.id, επιτυχία προσθήκης)
        """
        logger.log_info(f"Excecuting creation of {customer}")

        # Σημαντική προεπεξεργασία ώστε τα κενά strings να μετατρέπονται
        # σε None. Αλλιώς θεωρεί ότι το "" είναι πληροφορία και δεν δέχεται
        # δεύτερο πελάτη με κενό τηλέφωνο η email.

        # Έλεγχος ύπαρξης πελάτη
        existing_customer = self.filter_by_all(customer)
        if existing_customer is not None:
            logger.log_info(f"{existing_customer} already exists")
            return existing_customer.id, False

        # Προσθήκη νέου πελάτη
        if existing_customer is None:
            try:
                session.add(customer)
                session.commit()
                session.refresh(customer)
                self.max_id += customer.id
                logger.log_debug(f"Assigned id={self.max_id}")
            except Exception as e:
                logger.log_error(str(e))
                session.rollback()
                return None, False

        # Έλεγχος ορθής προσθήκης
        new_customer = self.get_customer_by_id(self.max_id)
        if new_customer is None:
            logger.log_error("Failed to retrieve customer id after insertion")
            raise Exception(f"DB Error on {customer}")

        # Ενημέρωση subscriber
        self.notify_subscribers()
        return self.max_id, True

    def delete_customer(self, customer: Customer) -> bool:
        """
        Διαγραφή πελάτη. Επιβάλλει την ύπαρξη customer.id πριν την
        διαγραφή.

        Επιστρέφει boolean επιτυχούς διαγραφής
        """
        logger.log_info(f"Excecuting deletion of {customer}")

        # Επιβολή ύπαρξης id
        if customer.id is None:
            logger.log_warn(f"{customer} does not have an id")
            return False

        # Διαγραφή πελάτη. To query είναι αναγκαίο για το sqlalchemy
        customer_to_delete = self.get_customer_by_id(customer.id)
        try:
            session.delete(customer_to_delete)
            session.commit()
        except Exception as e:
            logger.log_error(str(e))
            session.rollback()
            return False

        # Έλεγχος επιτυχούς διαγραφής
        # TODO: Μπορεί να αφαιρεθεί μόνο μετά από εξωνυχιστικό testing
        deleted_customer = self.get_customer_by_id(customer.id)
        if deleted_customer is not None:
            logger.log_error(f"Failed to delete {customer}")
            raise Exception(f"DB Error on {customer}")

        # Ενημέρωση max_id για ευκολότερη διαχείρηση
        self.max_id = self.find_max_id()

        # Ενημέρωση subscriber
        self.notify_subscribers()
        return True

    def update_customer(self, new_customer: Customer) -> bool:
        """
        Ενημέρωση στοιχείων πελάτη. Ελέγχει αν ήδη υπάρχει ο πελάτης
        πριν τον ενημερώσει.

        Επιστρέφει boolean επιτυχούς ενημέρωσης
        """
        logger.log_info(f"Excecuting update of {new_customer}")

        # Αναζητεί την παλιά εγγραφή του πελάτη
        old_customer = None
        if new_customer.id is not None:
            old_customer = self.get_customer_by_id(new_customer.id)

        if new_customer.id is None:
            old_customer = self.filter_by_all(new_customer)

        if old_customer is None:
            logger.log_warn(f"{new_customer} does not exist in database")
            return False

        if self.is_similar(old_customer, new_customer):
            logger.log_info(f"{new_customer} has not changed")
            return False

        # Ενημερώνει με τα καινούρια στοιχεία
        old_customer.name = new_customer.name
        old_customer.surname = new_customer.surname
        old_customer.normalized_name = new_customer.normalized_name
        old_customer.normalized_surname = new_customer.normalized_surname
        old_customer.phone = new_customer.phone
        old_customer.email = new_customer.email

        # Εκτελεί την ενημέρωση στην βάση δεδομένων
        try:
            session.commit()
            # session.refresh(new_customer)
        except Exception as e:
            logger.log_error(str(e))
            session.rollback()
            return False

        updated_customer = self.get_customer_by_id(old_customer.id)
        if updated_customer is None:
            logger.log_error(f"Failed to update {new_customer}")
            raise Exception(f"DB Error on {new_customer}")

        # Ενημερώνει το cache και τους subscribers
        # Σημαντικό να χρησιμοποιηθεί το αποτέλεσμα του νέου query και όχι ο πελάτης της παραμέτρου
        self.notify_subscribers()
        return True

    def get_customer_by_id(self, id: int) -> Customer | None:
        return session.query(Customer).filter_by(id=id).first()

    def get_customer_by_email(self, email: str) -> Customer | None:
        return session.query(Customer).filter_by(email=email).first()

    def get_customer_by_phone(self, phone: str) -> Customer | None:
        return session.query(Customer).filter_by(phone=phone).first()

    def add_subscriber(self, subscriber: SubscriberInterface) -> None:
        logger.log_info(f"Excecuting subscription of {subscriber}")
        self.subscribers.append(subscriber)

    def notify_subscribers(self) -> None:
        logger.log_info(f"Excecuting notification of {len(self.subscribers)} subscribers")
        for sub in self.subscribers:
            sub.subscriber_update()

    def customer_search(self, query: str) -> list[Customer]:
        """
        Συνάρτηση αναζήτησης πελάτη. Ψάχνει πελάτες με στοιχεία που
        εμπεριέχουν τους χαρακτήρες του query, σε σειρά.

        Ο χαρακτήρας % στην sqlite3 είναι wildcard. Δηλαδή εάν το
        query είναι "νι", τότε η αναζήτηση θα είναι για "νι%" που τεριάζει
        σε strings όπως νικος, νικη, νικολαος, νικολοπουλος, νιγιαννης κλπ
        """
        return (
            session.query(Customer)
            .filter(
                or_(
                    Customer.name.like(f"{query}%"),
                    Customer.surname.like(f"{query}%"),
                    Customer.normalized_name.like(f"{query}%"),
                    Customer.normalized_surname.like(f"{query}%"),
                    Customer.email.like(f"{query}%"),
                    Customer.phone.like(f"{query}%"),
                )
            )
            .all()
        )

    def find_max_id(self) -> int:
        result = self.session.query(func.max(Customer.id)).scalar()
        if result is None:
            return 0
        if not isinstance(result, int):
            return 0
        return result

    def get_customers(
        self,
        page_number: int = 0,
        page_length: int = 0,
        search_query: str = "",
        sorted_by: str = "",
        descending: bool = False,
    ) -> tuple[list[Customer], int]:
        """
        Φτιάχνει το query ανάλογα με της ανάγκες του caller. Επιστρέφει
        ένα tuple με τα αποτελέσματα και το σύνολο σελίδων
        """
        query = self.session.query(Customer)

        if search_query:
            filter = or_(
                Customer.name.like(f"{search_query}%"),
                Customer.surname.like(f"{search_query}%"),
                Customer.normalized_name.like(f"{search_query}%"),
                Customer.normalized_surname.like(f"{search_query}%"),
                Customer.email.like(f"{search_query}%"),
                Customer.phone.like(f"{search_query}%"),
            )
            query = query.filter(filter)

        if sorted_by:
            order_property = Customer.__dict__[sorted_by]
            if descending:
                order_property = desc(order_property)
            query = query.order_by(order_property)

        count = query.count()

        if page_number > 0 and page_length > 0:
            query = query.limit(page_length)
            query = query.offset((page_number - 1) * page_length)

        if page_length <= 0:
            count = 1
        else:
            count = ceil(count / page_length)

        return query.all(), count
