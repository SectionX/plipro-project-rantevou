import json
import pathlib


PATH = pathlib.Path(__file__).parent.parent.parent.parent / "settings.json"

cfg = None


def get_config():
    global cfg
    if cfg is None:
        with PATH.open("r") as f:
            cfg = json.load(f)
    return cfg


from .logging import Logger

try:
    Logger.archive_day()
except:
    pass


class SubscriberInterface:
    from .appointments_controller import AppointmentControl
    from .customers_controller import CustomerControl

    def __init__(self):
        self.AppointmentControl().add_subscription(self)
        self.CustomerControl().add_subscription(self)

    def subscriber_update(self):
        raise NotImplementedError
