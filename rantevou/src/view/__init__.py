from .window import Window
from .overview import Overview
from .appointments import Appointments
from .customers import Customers
from .statistics import Statistics
from .alerts import Alerts

__all__ = [
    "Window",
    "Overview",
    "Appointments",
    "Customers",
    "Statistics",
    "Alerts",
]


def create_window() -> Window:
    """
    Factory function που δημιουργεί και σετάρει την tkinter εφαρμογή
    """
    root = Window()
    root.load_frames(
        [
            Overview(root),
            Appointments(root),
            Customers(root),
            Statistics(root),
            Alerts(root),
        ]
    )
    return root
