from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Appointment(Base):
    __tablename__ = "appointment"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[str]
    time: Mapped[str]
    customer_id: Mapped[int] = mapped_column(foreign_key="customer.id")

    def __repr__(self):
        return (
            f"Appointment(id={self.id}, date={self.date}, "
            f"time={self.time}, customer_id={self.customer_id})"
        )
