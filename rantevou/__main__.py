from .src.view.window import Window
from .src.view.overview import Overview
from .src.view.statistics import Statistics
from .src.view.customers import Customers
from .src.view.appointments import Appointments
from .src.view.alerts import Alerts


def main():
    root = Window()
    root.load_frames(
        [
            Overview(root),
            Statistics(root),
            Customers(root),
            Appointments(root),
            Alerts(root),
        ]
    )

    root.run()


if __name__ == "__main__":
    main()
