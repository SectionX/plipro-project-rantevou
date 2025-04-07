from threading import Thread

from ..model.session import SessionLocal
from ..model.types import Customer

# TODO: Πρέπει να αλλαχθεί το πρόγραμμα ώστε κάθε φορά που ολοκληρώνονται οι
#       διαδικασιες του session, να κλείνει (session.close()). Ο λόγος που
#       έγινε έτσι ήταν θέμα ταχύτητας, δουλεύει, αλλά δημιουργεί και προβλήματα
#       μερικές φορές, ειδικά επειδή η sqlite δεν είναι ασύγχρονη.


class CustomerControl:

    def __init__(self):
        self.session = SessionLocal()
        self.customer = Customer

    def get_customers(self) -> list[Customer]:
        return self.session.query(self.customer).all()

    def create_customer(self, customer: dict | Customer, threaded=False) -> None:

        if isinstance(customer, dict):
            customer = Customer(**customer)
        elif not isinstance(customer, Customer):
            raise TypeError
        if threaded:
            Thread(target=self.create_customer, args=(customer,)).start()
            return

        if not self.validate_customer(customer):
            raise ValueError
        self.session.add(customer)
        self.session.commit()

    def delete_customer(
        self, customer: Customer | dict | int | None, threaded=False
    ) -> None:

        if isinstance(customer, dict):
            customer = Customer(**customer)
        elif isinstance(customer, int):
            customer = self.get_customer_by_id(customer)
        if customer is None:
            return
        if threaded:
            Thread(target=self.delete_customer, args=(customer,)).start()
            return

        self.session.delete(customer)
        self.session.commit()

    def update_customer(self, customer: Customer | dict | None, threaded=False) -> None:

        if isinstance(customer, dict):
            customer = Customer(**customer)
        if customer is None:
            return
        if threaded:
            Thread(target=self.update_customer, args=(customer,)).start()
            return

        old_customer = self.get_customer_by_id(customer.id)
        if old_customer is None:
            return

        old_customer.name = customer.name
        old_customer.surname = customer.surname
        old_customer.email = customer.email
        old_customer.phone = customer.phone
        self.session.commit()

    def get_customer_by_id(self, id) -> Customer | None:
        return self.session.query(self.customer).filter_by(id=id).first()

    def validate_customer(self, customer: dict | Customer) -> bool:
        if isinstance(customer, Customer):
            if customer.name:
                return True
            else:
                return False

        if isinstance(customer, dict):
            return all(key in customer for key in ["name"]) and customer["name"]

        return False
