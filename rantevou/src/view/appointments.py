from .abstract_views import AppFrame


class Appointments(AppFrame):
    def __init__(self, root, name="appointments"):
        super().__init__(root, name)

    def body_logic(self) -> None:
        """
        Εδώ προγραμματίζουμε την επιχειρησιακή λογική του frame.
        """
