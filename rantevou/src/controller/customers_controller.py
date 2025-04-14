from __future__ import annotations

from ..model.types import Customer, CustomerModel
from .logging import Logger

# TODO πρέπει να προσθεθούν σε όλα τα functions έλεγχος σφαλμάτων
#       και logs

logger = Logger("customer-controller")


class CustomerControl:
    _instance = None

    def __new__(cls, *args, **kwargs) -> CustomerControl:
        if cls._instance:
            return cls._instance

        cls._instance = super(CustomerControl, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.model = CustomerModel()
        self.customer = Customer

    def get_customers(self) -> list[Customer]:
        return self.model.get_customers()

    def create_customer(self, customer: Customer):
        return self.model.add_customer(customer)

    def delete_customer(self, customer: Customer) -> bool:
        return self.model.delete_customer(customer)

    def update_customer(self, customer: Customer) -> bool:
        return self.model.update_customer(customer)

    def get_customer_by_id(self, id) -> Customer | None:
        return self.model.get_customer_by_id(id)

    def get_customer_by_email(self, email: str) -> Customer | None:
        return self.model.get_customer_by_email(email)

    def add_subscription(self, node) -> None:
        self.model.add_subscriber(node)
