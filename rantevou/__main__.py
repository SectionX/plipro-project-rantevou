from sys import exit
import argparse

from .src.controller.logging import Logger
from .src.model.faker import reset_db, initialize_fake_db
from .src.view.window import Window

parser = argparse.ArgumentParser("Rantevou", "rantevou, rantevou --web", "Appointment manager for small businesses.")
parser.add_argument("-w", "--web", action="store_true", help="Starts a flask server to serve the app", default=False)
parser.add_argument(
    "--host", action="store", help="Define the host ip for web server, defaults to localhost", default="localhost"
)
parser.add_argument(
    "--port", action="store", help="Define the port for web server, defaults to 5000", type=int, default=5000
)
parser.add_argument(
    "-r", "--reset", action="store_true", help="Resets the database for testing purposes", default=False
)
parser.add_argument(
    "-f",
    "--fake",
    action="store",
    help="Populates the database with fake data for testing purposes",
    type=int,
    default=0,
)
parser.add_argument(
    "-l",
    "--loglevel",
    action="store",
    help="Adjusts the verbosity of logs to the terminal. Default=1, 0 to 4",
    type=int,
    default=1,
)


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
    args = parser.parse_args()

    if args.reset is True:
        inp = input("Are you sure you want to delete the database?")
        if inp.lower() != "y":
            exit(0)
        reset_db()
        if args.fake == 0:
            exit(0)

    if args.fake > 0:
        initialize_fake_db(args.fake)
        exit(0)

    Logger.level = args.loglevel

    if args.web is True:
        from .server import start_server

        start_server(host=args.host, port=args.port)
    else:
        logger = Logger("main")
        logger.log_info("Starting Rantevou")

        root = Window()
        root.mainloop()


if __name__ == "__main__":
    main()
