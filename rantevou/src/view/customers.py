from .abstract_views import AppFrame


class Customers(AppFrame):
    def __init__(self, root, name="customers"):
        super().__init__(root, name)
