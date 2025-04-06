from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DB_PATH = str(Path(__file__).parent.parent.parent / "rantevou.db")
# SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"  # Προσωρινό

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def generate_fake_data():
    from faker import Faker
    from .customer import Customer
    from .appointment import Appointment

    fk = Faker("el-GR")

    for i in range(30):
        yield Customer(
            name=fk.first_name(),
            surname=fk.last_name(),
            email=fk.email(),
            phone=fk.phone_number(),
        )


def initialize_db() -> None:

    Base.metadata.create_all(bind=engine)
    # with SessionLocal() as session:
    #     session.add_all(generate_fake_data())
    #     session.commit()
