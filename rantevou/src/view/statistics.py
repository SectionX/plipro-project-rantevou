from .abstract_views import AppFrame


class Statistics(AppFrame):
    def __init__(self, root, name="statistics"):
        super().__init__(root, name)

        self.initialize()
