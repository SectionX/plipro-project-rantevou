from .src import controller

ac = controller.appointments_controller.AppointmentControl()
cc = controller.customers_controller.CustomerControl()


def get_appointments():
    return ac.get_appointments()


def get_customers():
    return cc.get_customers()
