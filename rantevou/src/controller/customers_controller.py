from threading import Thread

from ..model.session import SessionLocal
from ..model.customer import Customer


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
            print(customer)
            raise TypeError
        if threaded:
            Thread(target=self.create_customer, args=(customer,)).start()
            return

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

    def validate_customer(self, customer: dict | list) -> bool:
        test1 = all(key in customer for key in ["name", "surname", "email", "phone"])
        test2 = len(customer) == 4

        if not (test1 and test2):
            return False
        if isinstance(customer, list):
            return all(customer)
        if isinstance(customer, dict):
            return all(customer.values())
