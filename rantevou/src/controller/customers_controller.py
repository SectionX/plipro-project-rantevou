from __future__ import annotations

from ..model.entities import Customer
from ..model.customer import CustomerModel
from .logging import Logger

# TODO πρέπει να προσθεθούν σε όλα τα functions έλεγχος σφαλμάτων
#       και logs

logger = Logger("customer-controller")


class CustomerControl:
    _instance = None
    model: CustomerModel

    def __new__(cls, *args, **kwargs) -> CustomerControl:
        if cls._instance:
            return cls._instance

        cls._instance = super(CustomerControl, cls).__new__(cls, *args, **kwargs)
        cls.model = CustomerModel()
        return cls._instance

    def get_customers(
        self,
        page_number: int = 0,
        page_length: int = 0,
        search_query: str = "",
        sorted_by: str = "",
        descending: bool = False,
    ) -> tuple[list[Customer], int]:
        logger.log_info(
            f"Requesting customer search with query: {page_number}, {page_length}, {search_query}, {sorted_by}, {descending}"
        )
        return self.model.get_customers(page_number, page_length, search_query, sorted_by, descending)

    def create_customer(self, customer: Customer):
        logger.log_info(f"Requesting creation of {customer}")
        return self.model.add_customer(customer)

    def delete_customer(self, customer: Customer) -> bool:
        logger.log_info(f"Requesting deletion of {customer}")
        return self.model.delete_customer(customer)

    def update_customer(self, customer: Customer) -> bool:
        logger.log_info(f"Requesting update of {customer}")
        return self.model.update_customer(customer)

    def get_customer_by_id(self, id: int) -> Customer | None:
        logger.log_info(f"Requesting customer search by id {id}")
        return self.model.get_customer_by_id(id)

    def get_customer_by_email(self, email: str) -> Customer | None:
        logger.log_info(f"Requesting customer search by email {email}")
        return self.model.get_customer_by_email(email)

    def add_subscription(self, node) -> None:
        logger.log_info(f"Requesting subscription for node {node}")
        self.model.add_subscriber(node)

    def search(self, string: str) -> list[Customer]:
        logger.log_info(f"Requesting customer search with query: {string}")
        if string == "":
            return self.model.customers
        return self.model.customer_search(string)
