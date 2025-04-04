# SQLALCHEMY_TEST_DATABASE = f"sqlite:///:memory:"  # Προσωρινό

# test_engine = create_engine(SQLALCHEMY_TEST_DATABASE)
# SessionLocalTest = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


# def initialize_test_db():
#     from .appointment import Appointment
#     from .customer import Customer
#     from datetime import datetime

#     Base.metadata.create_all(bind=test_engine)
#     with SessionLocalTest() as session:
#         session.add(
#             Customer(
#                 name="Κωνσταντινος",
#                 surname="Καραπανακιος",
#                 email="kostas@k.gr",
#                 phone="123456789",
#             )
#         )
#         session.add(
#             Customer(
#                 name="Νικόλαος",
#                 surname="Καραπανακιος",
#                 email="kostas@k.gr",
#                 phone="123456789",
#             )
#         )
#         session.add(Appointment(date=datetime(2023, 1, 1), customer_id=1))
#         session.add(Appointment(date=datetime(2023, 1, 2), customer_id=2))
#         session.commit()
