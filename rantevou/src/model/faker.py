from .session import SessionLocal, Base, engine

session = SessionLocal()


def generate_fake_customer_data(n):
    from itertools import combinations
    from faker import Faker
    from .customer import Customer

    combs_email = combinations("abcdefghijklmnopqrstuvwxyz123457890", 10)
    combs_phone = combinations("1234567890", 7)
    start = 210
    fk = Faker("el-GR")

    for i in range(n):
        try:
            cus = Customer(
                name=fk.first_name(),
                surname=fk.last_name(),
                email=f"{''.join(next(combs_email))}@example.com",
                phone=f"{start}{''.join(next(combs_phone))}",
            )
            yield cus
        except StopIteration:
            start += 1
            combs_phone = combinations("1234567890", 7)
        print(i, end="\r")


# TODO Καθαρισμός και μεταφορά σε άλλο αρχείο
def generate_fake_appointment_data(n):
    from datetime import datetime, timedelta
    from random import randint
    from .appointment import Appointment

    start_date = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
    for i in range(n):
        start_date = start_date + timedelta(minutes=5 * randint(4, 6))
        if start_date.hour > 17:
            start_date = start_date.replace(day=start_date.day, hour=9, minute=0) + timedelta(days=1)

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


def initialize_fake_db(n) -> None:
    session.add_all(generate_fake_customer_data(n))
    session.commit()
    session.add_all(generate_fake_appointment_data(n))
    session.commit()
    session.close()


def reset_db() -> None:
    from sqlalchemy import text

    session.execute(text("DROP TABLE Appointment"))
    session.execute(text("DROP TABLE Customer"))
    Base.metadata.create_all(engine)
    session.commit()
