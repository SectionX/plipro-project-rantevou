from .abstract_views import AppFrame


class Appointments(AppFrame):
    def __init__(self, root, name="appointments"):
        super().__init__(root, name)
