# from .window import Window
# from .overview import Overview
# from .appointments import Appointments
# from .customers import Customers
# from .statistics import Statistics
# from .alerts import Alerts

# __all__ = [
#     "Window",
#     "Overview",
#     "Appointments",
#     "Customers",
#     "Statistics",
#     "Alerts",
# ]


<<<<<<< HEAD
def create_window() -> Window:
    """
    Factory function που δημιουργεί και σετάρει την tkinter εφαρμογή
    """
    root = Window()
    Overview(root)
    Appointments(root)
    Customers(root)
    Statistics(root)
    Alerts(root)
    root.initialize()

    return root
=======
# def create_window() -> Window:
#     """
#     Factory function που δημιουργεί και σετάρει την tkinter εφαρμογή
#     """
#     root = Window()
#     Customers(root)
#     Appointments(root)
#     Statistics(root)
#     Alerts(root)
#     Overview(root).pack(fill="both", expand=True)

#     return root
>>>>>>> dev-stouraitis
