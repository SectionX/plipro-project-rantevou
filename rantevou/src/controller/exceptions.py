class ViewWrongDataError(Exception):
    """Για όταν κάποιο view component λαμβάνει λανθασμένο τύπο η πλήθος στοιχείων"""


class ViewCommunicationError(Exception):
    """Για όταν κάποιο view component δεν μπορεί να καλέσει κάποιο άλλο"""


class ViewInternalError(Exception):
    """Για όταν οι υπολογισμοί που κάνει εσωτερικά το component παράγουν κάποιο σφάλμα"""


class ViewInputError(Exception):
    """Για όταν o χρήστης εισάγει ασύμβατα στοιχεία"""
