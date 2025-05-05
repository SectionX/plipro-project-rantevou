class SubscriberInterface:
    from .appointments_controller import AppointmentControl
    from .customers_controller import CustomerControl

    def __init__(self):
        self.AppointmentControl().add_subscription(self)
        self.CustomerControl().add_subscription(self)

    def subscriber_update(self):
        raise NotImplementedError
