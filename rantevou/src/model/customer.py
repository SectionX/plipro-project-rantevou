from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from .session import Base


class Customer(Base):
    __tablename__ = "customer"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    surname: Mapped[str]
    email: Mapped[str]
    phone: Mapped[str]

    def __repr__(self):
        return f"Customer(id={self.id}, name={self.name}, surname={self.surname}, email={self.email}, phone={self.phone})"
