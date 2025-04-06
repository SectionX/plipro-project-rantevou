from .abstract_views import AppFrame


class Alerts(AppFrame):
    def __init__(self, root, name="alerts"):
        super().__init__(root, name)

        self.initialize()
