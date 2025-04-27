from .src.model.session import initialize_db, reset_initialize_fake_db, reset_db
from .src.controller.logging import Logger
from sys import argv, exit

from .src.view.window import Window

# TODO Χρήση argparse αντι αυτού του σχήματος
if len(argv) > 1:
    if argv[1] == "reset":
        reset_db()
    elif argv[1] == "reset-fake":
        reset_initialize_fake_db()
    else:
        exit(0)

initialize_db()

# TODO Μεταφορά σε option
Logger.level = 0


def main():
    """
    Η είσοδος στο πρόγραμμα. Σημαντική σημείωση για τους contributors,
    εάν προσπαθήσετε να τρέξετε το πρόγραμμα με την εντολή "python __main__.py"
    θα βγάλει import error.

    Αντί αυτού πηγαίνετε πίσω στο directory με το setup.py και τρέξτε την εντολή
    "pip install -e ."

    Μετα θα εκκινείτε το πρόγραμμα με τις εντολές:
    "rantevou"
    "python -m rantevou"

    Το option -e σημαίνει "editable", που σας επιτρέπει να κάνετε κανονικά αλλαγές
    στον κώδικα και να τρέχετε το πρόγραμμα. Χωρίς αυτό θα πρέπει να κάνετε
    reinstall κάθε φορά που κάνετε αλλαγές.
    """

    logger = Logger("main")
    logger.log_info("Starting Rantevou")

    root = Window()
    root.mainloop()


if __name__ == "__main__":
    main()
