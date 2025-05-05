# from ..src.model.appointment import Appointment, AppointmentModel
# from ..src.model.customer import Customer, CustomerModel
# from ..src.model.session import Base
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy import create_engine
# from datetime import datetime, timedelta

# engine = create_engine("sqlite:///:memory:")
# SessionLocal = sessionmaker(bind=engine)


# Base.metadata.create_all(engine)
# session = SessionLocal()


# AppointmentModel.session = session
# a_model = AppointmentModel()
# b_model = AppointmentModel()


# class Subscriber:
#     def __init__(self):
#         self.check = False

#     def subscriber_update(self):
#         self.check = True

#     def reset(self):
#         self.check = False


# subscriber = Subscriber()

# customer = Customer(id=2, name="a", surname="a", phone="a", email="a")

# appointment = Appointment(
#     id=1,
#     date=datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0),
#     is_alerted=False,
#     duration=timedelta(minutes=20),
#     customer_id=None,
#     employee_id=0,
# )


# def test_singleton():
#     assert a_model is b_model


# def test_add_subscriber():
#     a_model.add_subscriber(subscriber)
#     assert len(a_model.subscribers) == 1
#     assert len(b_model.subscribers) == 1


# def test_subscriber_update():
#     a_model.subscribers[0].subscriber_update()
#     assert subscriber.check
#     subscriber.reset()

#     b_model.subscribers[0].subscriber_update()
#     assert subscriber.check


# def test_add_appointment():
#     index = a_model.get_index(appointment.date)

#     assert len(a_model.appointments[index]) == 0
#     a_model.add_appointment(appointment)
#     assert len(a_model.appointments[index]) == 1

#     appointment_cache = a_model.appointments[index][0]
#     appointment_db = (
#         a_model.session.query(Appointment).filter_by(id=appointment_cache.id).first()
#     )

#     assert appointment_db is not None
#     assert appointment.values == appointment_cache.values == appointment_db.values
#     assert a_model.max_id == 1


# def test_overlap():
#     date = lambda x: datetime(1970, 1, 1, x)
#     duration = lambda x: timedelta(hours=x)

#     a1 = Appointment(date=date(0), duration=duration(1))
#     a2 = Appointment(date=date(1), duration=duration(1))
#     assert not a1.overlap(a2)

#     a1 = Appointment(date=date(1), duration=duration(1))
#     a2 = Appointment(date=date(0), duration=duration(1))
#     assert not a1.overlap(a2)

#     a1 = Appointment(date=date(1), duration=duration(2))
#     a2 = Appointment(date=date(0), duration=duration(2))
#     assert a1.overlap(a2)

#     a1 = Appointment(date=date(0), duration=duration(3))
#     a2 = Appointment(date=date(1), duration=duration(1))
#     assert a1.overlap(a2)

#     a1 = Appointment(date=date(0), duration=duration(2))
#     a2 = Appointment(date=date(1), duration=duration(2))
#     assert a1.overlap(a2)


# # def test_update_appointment():
# #     index = a_model.get_index(appointment.date)
# #     new


# # def test_delete_appointment(self, appointment: Appointment) -> bool:
# #     pass


# # def test_get_appointments(self) -> dict[int, list[Appointment]]:
# #     pass


# # def test_get_appointment_by_id(self, appointment_id: int) -> Appointment | None:
# #     pass


# # def test_get_appointment_by_date(self, date: datetime) -> Appointment | None:
# #     pass


# # def test_get_appointments_from_to_date():
# #     pass


# # def test_split_appointments_in_periods(self, *args, **kwargs):
# #     pass


# # def test_get_time_between_appointments():
# #     pass


# # def test_replace_in_cache(appointment, old_date):
# #     pass


# # def test_get_index(self, date: datetime):
# #     pass


# # def test_add_to_cache(self, target: Appointment):
# #     pass


# # def test_delete_from_cache(self, target: Appointment):
# #     pass


# # def test_update_subscribers(self):
# #     pass


# # def test_find_max_id(self) -> int:
# #     pass


# # def test_load_to_cache(self, date: datetime):
# #     pass


# # def test_time_to_appointment(self) -> timedelta:
# #     pass
# # def test_time_between_appointments(self, appointment: Appointment) -> timedelta:
# #     pass
# # def test_time_between_dates(self, date: datetime) -> timedelta:
# #     pass
# # def test_to_dict(self):
# #     pass
