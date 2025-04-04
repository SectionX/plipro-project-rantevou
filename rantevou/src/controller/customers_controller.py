from ..model.session import SessionLocal
from ..model.customer import Customer


class CustomerControl:

    def __init__(self):
        self.session = SessionLocal()
        self.customer = Customer

    def get_customers(self) -> list[Customer]:
        return self.session.query(self.customer).all()

    def create_customer(self, customer) -> None:
        self.session.add(customer)
        self.session.commit()

    def delete_customer(self, customer: Customer) -> None:
        self.session.delete(customer)
        self.session.commit()

    def update_customer(self, customer: Customer) -> None:
        old_customer = self.session.query(Customer).filter_by(id=customer.id).first()
        if old_customer:
            old_customer.name = customer.name
            old_customer.surname = customer.surname
            old_customer.email = customer.email
            old_customer.phone = customer.phone
        self.session.commit()

    def get_customer_by_id(self, id) -> Customer | None:
        return self.session.query(self.customer).filter_by(id=id).first()
