import json
import pathlib
from .appointments_controller import AppointmentControl
from .customers_controller import CustomerControl

ac = AppointmentControl()
cc = CustomerControl()

PATH = pathlib.Path(__file__).parent.parent.parent.parent / "settings.json"

cfg = None


def get_config():
    global cfg
    if cfg is None:
        with PATH.open("r") as f:
            cfg = json.load(f)
    return cfg


from .logging import Logger

Logger.archive_day()


class SubscriberInterface:
    def __init__(self):
        ac.add_subscription(self)
        cc.add_subscription(self)

    def subscriber_update(self):
        raise NotImplementedError
