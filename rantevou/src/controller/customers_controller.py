from .logging import logger
from ..model.session import SessionLocal
from ..model.customer import Customer


class CustomerControl:

    def __init__(self):
        self.session = SessionLocal()
        self.customer = Customer

    def get_customers(self):
        return self.session.query(self.customer).all()

    def create_customer(self, customer):
        self.session.add(customer)
        self.session.commit()

    def delete_customer(self, customer):
        self.session.delete(customer)
        self.session.commit()

    def update_customer(self, id, **fields):
        pass

    def get_customer_by_id(self, id):
        return self.session.query(self.customer).filter_by(id=id).first()
