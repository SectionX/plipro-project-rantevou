"""
Ορισμός του μοντέλου δεδομένων των πελατών. Ορίζει μεθόδους αναζήτησης στην βάση δεδομένων,
καθώς και εισαγωγή, επεξεργασία και διαγραφή.
"""

from __future__ import annotations

from math import ceil

from sqlalchemy import func, or_, desc
from sqlalchemy.exc import DatabaseError

from .session import session
from .entities import Customer
from .interfaces import SubscriberInterface
from .exceptions import IdMissing, IdOnNewCustomer, CustomerDBError
from ..controller.logging import Logger

logger = Logger("customer-model")


class CustomerModel:
    """
    Μοντέλο δεδομένων πελάτη. Εφαρμόοζει singleton pattern.
    """

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

    def is_similar(self, customer1: Customer, customer2: Customer) -> bool:
        """
        Ελέγχει αν τα σημαντικά στοιχεία 2 πελατών είναι ίδια

        Args:
            customer1 (Customer): Πελάτης 1
            customer2 (Customer): Πελάτης 2

        Returns:
            bool: True αν έχουν ίδια στοιχεία, αλλιώς False
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
        Επιστρέφει τους τίτλους των στήλων. Η σειρά είναι ίδια με την μέθοδο .values
        του Customer object

        Returns:
            list[str]
        """
        return ["id", "name", "surname", "phone", "email"]

    def filter_by_all(self, customer: Customer) -> Customer | None:
        """
        Ειδική συνάρτηση που ψάχνει έναν πελάτη στην βάση δεδομένων χωρίς την χρήση id

        Args:
            customer (Customer): Αντικείμενο αναπαράστασης πελάτη χωρίς id. Μπορεί να
            χρησιμοποιηθεί και με id, αλλα προτίμησε την χρήση της .get_customer_by_id

        Returns:
            Customer | None
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

    def add_customer(self, customer: Customer) -> Customer:
        """
        Προσθήκη νέου πελάτη στην βάση δεδομένων. Το αντικείμενο δεν πρέπει να έχει
        id. Ενημερώνει τα στοιχεία του αντικειμένου κατα την εισαγωγή για περεταίρω
        επεξεργασία από την καλούσα.

        Args:
            customer (Customer): Αναπαράσταση του πελάτη σε sql object χωρίς id.

        Raises:
            IdOnNewCustomer: Εάν η αναπαράσταση του πελάτη έχει id
            CustomerDBError: Εάν κάτι πάει λάθος κατά την είσοδο στην βάση δεδομένων

        Returns:
            Customer: Πλήρης αναπαράσταση του πελάτη με ενεργή σύνδεση στην βάση δεδομένων.
        """
        logger.log_info(f"Excecuting creation of new {customer}")

        if customer.id is not None:
            raise IdOnNewCustomer(customer)

        try:
            session.add(customer)
            session.commit()
            session.refresh(customer)
            self.max_id = customer.id
            logger.log_debug(f"Assigned id={customer.id}")
        except DatabaseError as e:
            session.rollback()
            raise CustomerDBError(str(e)) from e

        # Ενημέρωση subscriber
        self.notify_subscribers()
        return customer

    def delete_customer(self, customer: Customer) -> bool:
        """
        Διαγράφει τον πελάτη από την βάση δεδομένων. Επιβάλλει ο πελάτης
        να έχει id.

        Args:
            customer (Customer): Πελάτης προς διαγραφή

        Raises:
            IdMissing: Εάν το customer object δεν έχει id
            CustomerDBError: Εάν κάτι πάει λάθος κατά το transaction

        Returns:
            bool: True στην επιτυχία, αλλιώς error
        """
        logger.log_info(f"Excecuting deletion of {customer}")

        # Επιβολή ύπαρξης id
        if customer.id is None:
            raise IdMissing(customer)

        # Διαγραφή πελάτη.
        try:
            session.refresh(customer)
            session.delete(customer)
            session.commit()
            self.max_id = self.__find_max_id()
        except DatabaseError as e:
            session.rollback()
            raise CustomerDBError(customer, str(e)) from e

        # Ενημέρωση subscriber
        self.notify_subscribers()
        return True

    def update_customer(self, customer: Customer) -> bool:
        """
        Ενημέρωση στοιχείων πελάτη. Ελέγχει αν ήδη υπάρχει ο πελάτης
        πριν τον ενημερώσει.

        Επιστρέφει boolean επιτυχούς ενημέρωσης
        """
        logger.log_info(f"Excecuting update of {customer}")

        # Έλεγχος για ύπαρξη id
        if customer.id is None:
            raise IdMissing(customer)

        try:
            (
                session.query(Customer)
                .filter_by(id=customer.id)
                .update(
                    {
                        Customer.name: customer.name,
                        Customer.surname: customer.surname,
                        Customer.normalized_name: customer.normalized_name,
                        Customer.normalized_surname: customer.normalized_surname,
                        Customer.phone: customer.phone,
                        Customer.email: customer.email,
                    }
                )
            )
        except DatabaseError as e:
            session.rollback()
            raise CustomerDBError(customer, str(e)) from e

        # Ενημερώνει το cache και τους subscribers
        self.notify_subscribers()
        return True

    def add_subscriber(self, subscriber: SubscriberInterface) -> None:
        """
        Προσθέτει subscribers στην λίστα, προς ενημέρωση. Δες rantevou.src.controller.subscriber
        Args:
            subscriber (SubscriberInterface)
        """
        logger.log_info(f"Excecuting subscription of {subscriber}")
        self.subscribers.append(subscriber)

    def notify_subscribers(self) -> None:
        """
        Ενημερώνει τους subscribers
        """
        logger.log_info(f"Excecuting notification of {len(self.subscribers)} subscribers")
        for sub in self.subscribers:
            sub.subscriber_update()

    def get_customer_by_id(self, id_: int) -> Customer | None:
        """
        Μέθοδος γρήγορης εύρεσης πελάτη με id

        Args:
            id_ (int)

        Returns:
            Customer | None
        """
        return session.query(Customer).filter_by(id=id_).first()

    def customer_search(self, query: str) -> list[Customer]:
        """
        Μέθοοδος αναζήτησης πελάτη. Ψάχνει πελάτες με στοιχεία που
        εμπεριέχουν τους χαρακτήρες του query, σε σειρά.

        Ο χαρακτήρας % στην sqlite3 είναι wildcard. Δηλαδή εάν το
        query είναι "νι", τότε η αναζήτηση θα είναι για "νι%" που ταιριάζει
        σε strings όπως νικος, νικη, νικολαος, νικολοπουλος, νιγιαννης κλπ

        Αυτή η μέθοδος προορίζεται για στοχευμένες αναζητήσεις με σκοπό την εύρεση
        ενός, η λίγων πελατών με συγκεκριμένο χαρακτηριστικό. Προτίνεται μόνο για
        αναζήτηση τον μοναδικών στοιχείων όπως τηλέφωνο και email. Για πιο γενικές
         αναζητήσεις χρησιμοποίησε την .get_customers

        Args:
            query (str): Συμβολοσειρά προς αναζήτηση

        Returns:
            list[Customer]: Αποτελέσματα αναζήτησης
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

    def __find_max_id(self) -> int:
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
        Βασική μέθοδος αναζήτησης πελατών στην βάση δεδομένων.

        Χτίζει το query τμηματικά βάση των παραμέτρων. Προορίζεται για χρήση σε
        συναρτήσης που ψάχνουν μεγάλο πλήθος πελατών με έμφαση στα μη μοναδικά
        χαρακτηριστικά όπως όνομα και επίθετο.

        Args:
            page_number (int, optional):
            Αριθμός σελίδας, επιστρέφει όλα τα αποτέλεσματα εάν είναι 0. Defaults to 0.

            page_length (int, optional):
            Αποτελέσματα ανα σελίδα, άπειρα αποτελέσματα εάν είναι 0. Defaults to 0.

            search_query (str, optional):
            Η συμβολοσειρά αναζήτησης. Αάπειρα αποτελέσματα εάν είναι κενή. Defaults to "".

            sorted_by (str, optional):
            Στήλη στην οποία θα γίνει ταξινόμηση. Αγνοεί αν είναι άδειο. Defaults to "".

            descending (bool, optional):
            Μόνο εάν υπάρχει στήλη ταξινόμησης, True για φθήνουσα. Defaults to False.

        Returns:
            tuple[list[Customer], int]:
            Πλειάδα με την λίστα των πελατών και το σύνολο των σελίδων
        """
        query = self.session.query(Customer)

        # Δημιουργία query αναζήτησης
        if search_query:
            filter_ = or_(
                Customer.name.like(f"{search_query}%"),
                Customer.surname.like(f"{search_query}%"),
                Customer.normalized_name.like(f"{search_query}%"),
                Customer.normalized_surname.like(f"{search_query}%"),
                Customer.email.like(f"{search_query}%"),
                Customer.phone.like(f"{search_query}%"),
            )
            query = query.filter(filter_)

        # Δημιουργία query ταξινόμησης
        if sorted_by:
            order_property = Customer.__dict__[sorted_by]
            if descending:
                order_property = desc(order_property)
            query = query.order_by(order_property)

        count = query.count()

        # Δημιουργία query σελιδοποίησης
        if page_number > 0 and page_length > 0:
            query = query.limit(page_length)
            query = query.offset((page_number - 1) * page_length)

        if page_length <= 0:
            count = 1
        else:
            count = ceil(count / page_length)

        logger.log_info(f"Executing {query}")
        return query.all(), count

    def merge(self, customer: Customer) -> Customer:
        """
        Συνδέει το αντικείμενο με το session

        Μετατρέπει την κατάσταση του από transient σε peristent
        Αυτό επιτρέπει την χρήση του Customer().appointments χωρίς
        να χρειάζεται ξεχωριστή αναζήτηση στην βάση δεδομένων.

        Args:
            customer (Customer): Transient object

        Returns:
            Customer: Persistent object
        """

        return self.session.merge(customer)
