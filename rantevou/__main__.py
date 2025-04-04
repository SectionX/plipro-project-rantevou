from .src.view import create_window
from .src.model.session import initialize_db


def main():
    """
    Η είσοδος στο πρόγραμμα. Σημαντική σημείωση για τους contributors,
    εάν προσπαθήσετε να τρέξετε το πρόγραμμα με την εντολή "python __main__.py"
    θα βγάλει importerror.

    Αντί αυτού πηγαίνετε πίσω στο directory με το setup.py και τρέξτε την εντολή
    "pip install -e ."

    Μετα θα εκκινείτε το πρόγραμμα με τις εντολές:
    "rantevou"
    "python -m rantevou"

    Το option -e σημαίνει "editable", που σας επιτρέπει να κάνετε κανονικά αλλαγές
    στον κώδικα και να τρέχετε το πρόγραμμα. Χωρίς αυτό θα πρέπει να κάνετε
    reinstall κάθε φορά που κάνετε αλλαγές.
    """

    initialize_db()
    root = create_window()
    root.run()


if __name__ == "__main__":
    main()
