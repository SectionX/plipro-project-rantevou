from ..model.types import Customer, CustomerModel
from .logging import Logger

# TODO πρέπει να προσθεθούν σε όλα τα functions έλεγχος σφαλμάτων
#       και logs

logger = Logger("customer-controller")


class CustomerControl:
    _instance = None

    def __new__(cls, *args, **kwargs):
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
        self.model.add_customer(customer)

    def delete_customer(self, customer: Customer | int | None) -> None:
        if isinstance(customer, int):
            customer = self.model.get_customer_by_id(customer)
        if not customer:
            return
        self.model.delete_customer(customer)

    def update_customer(self, customer: Customer):
        self.model.update_customer(customer)

    def get_customer_by_id(self, id) -> Customer | None:
        return self.model.get_customer_by_id(id)

    def get_customer_by_email(self, email: str) -> Customer | None:
        return self.model.get_customer_by_email(email)

    def add_subscriber(self, node):
        self.model.add_subscriber(node)

    def get_customer_fields(self):
        return self.model.get_fields()
