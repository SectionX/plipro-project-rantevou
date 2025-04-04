from .src.view import initialize_window
from .src.model.session import initialize_db


def main():

    initialize_db()
    root = initialize_window()
    root.run()


if __name__ == "__main__":
    main()
