from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DB_PATH = Path(__file__).parent.parent.parent / "data" / "rantevou.db"
# SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

SQLALCHEMY_DATABASE_URL = f"sqlite:///{str(DB_PATH)}"  # Προσωρινό

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

session = SessionLocal()


class Base(DeclarativeBase):
    pass


from unicodedata import normalize


def normalize_cus(customer):
    customer.normalized_name = normalize("NFKD", customer.name).lower().replace("́", "")
    try:
        customer.normalized_surname = (
            normalize("NFKD", customer.surname).lower().replace("́", "")
        )
    except:
        pass


def generate_fake_customer_data():
    from itertools import combinations
    from faker import Faker
    from .customer import Customer

    combs_email = combinations("abcdefghijklmnopqrstuvwxyz123457890", 10)
    combs_phone = combinations("1234567890", 7)
    start = 210
    fk = Faker("el-GR")

    for i in range(30000):
        try:
            cus = Customer(
                name=fk.first_name(),
                surname=fk.last_name(),
                email=f"{''.join(next(combs_email))}@example.com",
                phone=f"{start}{''.join(next(combs_phone))}",
            )
            normalize_cus(cus)
            yield cus
        except StopIteration:
            start += 1
            combs_phone = combinations("1234567890", 7)
        print(i, end="\r")


def generate_fake_appointment_data():
    from datetime import datetime, timedelta
    from random import randint
    from .appointment import Appointment

    start_date = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
    for i in range(30000):
        start_date = start_date + timedelta(minutes=5 * randint(4, 6))
        if start_date.hour > 17:
            start_date = start_date.replace(
                day=start_date.day, hour=9, minute=0
            ) + timedelta(days=1)

        if i % 5 == 0:
            customer_id = None
        else:
            customer_id = randint(1, 300)

        is_alerted = bool(randint(0, 1))
        yield Appointment(
            date=start_date,
            customer_id=customer_id,
            is_alerted=is_alerted,
            duration=timedelta(minutes=20),
        )
        print(i, end="\r")


def initialize_db() -> None:
    Base.metadata.create_all(bind=engine)


def reset_initialize_fake_db() -> None:
    DB_PATH.unlink(missing_ok=True)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        session.add_all(generate_fake_customer_data())
        session.add_all(generate_fake_appointment_data())
        session.commit()


def reset_db() -> None:
    DB_PATH.unlink(missing_ok=True)
    Base.metadata.create_all(bind=engine)
