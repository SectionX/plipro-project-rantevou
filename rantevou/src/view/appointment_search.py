from __future__ import annotations

from tkinter import ttk
from datetime import datetime, timedelta
import typing as Type

from . import abstract_views
from .exceptions import *
from .abstract_views import Caller
from ..controller import get_config
from ..controller.logging import Logger

logger = Logger("appointment-search")

cfg = get_config()
__working_hours = int(cfg["view_settings"]["working_hours"])
__opening_hour = int(cfg["view_settings"]["opening_hour"])
CLOSING_HOUR = __opening_hour + __working_hours


class SearchResult(ttk.Button, Caller):
    """
    Κουμπί που εμφανίζει ένα αποτελέσμα αναζήτησης κενού χρόνου μεταξύ
    των ραντεβού.

    Εάν πατηθεί πηγαίνει στην φόρμα προσθήκης νέου ραντεβού, βάζοντας
    αυτόματα τα σχετικά στοιχεία στα αντίστοιχα κελια.
    """

    def __init__(self, master, date: datetime, duration: timedelta, user_input: timedelta, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        Caller.__init__(self)
        self.date = date
        self.duration = duration
        self.user_input = user_input

        self.config(command=self.open_add_screen)
        self.draw()

    def open_add_screen(self):
        self.sidepanel.select_view("add", caller="search", caller_data=(self.date, self.duration))

    def draw(self):
        minutes = self.duration.total_seconds() // 60
        duration = f"{minutes} λεπτά"

        if (self.date + self.user_input).hour >= CLOSING_HOUR:
            duration = "Εκτός Ωραρίου"

        date = self.date.strftime("%d/%m, %H:%M")
        self.config(text=f"{date}-{duration}")


class SearchResultsView(abstract_views.SideView):
    """
    View που εμφανίζει τα αποτελέσματα αναζήτησης κενού χρόνου μεταξύ
    των ραντεβού.
    """

    name: str = "search"
    dates: Type.Sequence[tuple[datetime, timedelta]]
    result_frame: ttk.Frame

    def __init__(self, root, *args, **kwargs):
        super().__init__(root, *args, **kwargs)
        self.set_title("Αποτελέσματα")
        self.name = self.__class__.name
        self.dates = []

        self.result_frame = ttk.Frame(self)
        self.back_btn.config(command=self.sidepanel.go_back)

    def update_content(self, caller, caller_data):

        if not isinstance(caller_data, Type.Sequence):
            raise ViewWrongDataError(self, caller, caller_data)

        if len(caller_data) < 2:
            raise ViewWrongDataError(self, caller, caller_data)

        if not isinstance(caller_data[0], Type.Sequence):
            raise ViewWrongDataError(self, caller, caller_data)

        if not isinstance(caller_data[1], timedelta):
            raise ViewWrongDataError(self, caller, caller_data)

        if not isinstance(caller_data[0][0], Type.Sequence):
            raise ViewWrongDataError(self, caller, caller_data)

        if not isinstance(caller_data[0][0][0], datetime):
            raise ViewWrongDataError(self, caller, caller_data)

        if not isinstance(caller_data[0][0][1], timedelta):
            raise ViewWrongDataError(self, caller, caller_data)

        self.dates, self.user_input = caller_data

        self.result_frame.destroy()
        self.result_frame = ttk.Frame(self)
        for date, duration in self.dates:
            SearchResult(self.result_frame, date=date, duration=duration, user_input=self.user_input).pack(fill="x")
        self.result_frame.pack(fill="x")
