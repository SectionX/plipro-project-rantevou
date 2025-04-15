# from __future__ import annotations

# import tkinter as tk
# from tkinter import ttk
# from datetime import datetime, timedelta
# from typing import Any

# from . import sidepanel
# from . import abstract_views

# from ..controller.appointments_controller import AppointmentControl
# from ..controller.logging import Logger
# from ..controller.mailer import Mailer

# ac = AppointmentControl()
# logger = Logger("appointment-manager")
# mailer = Mailer()


# class SearchResult(ttk.Button):

#     def __init__(self, master, period: datetime, duration: timedelta, *args, **kwargs):
#         super().__init__(master, *args, **kwargs)
#         self.config(command=self.open_add_screen)
#         self.period = period
#         self.duration = duration

#     def open_add_screen(self):
#         sidepanel.SidePanel.select_view(
#             "add", caller="search", data=(self.period, self.duration)
#         )


# class SearchResultsView(abstract_views.SideView):
#     name: str = "search"
#     periods: list[tuple[datetime, timedelta]]
#     result_frame: ttk.Frame

#     def __init__(self, root, *args, **kwargs):
#         super().__init__(root, *args, **kwargs)
#         self.name = self.__class__.name
#         self.set_title("Αποτελέσματα")
#         self.result_frame = ttk.Frame(self)
#         self.add_back_btn(self)
#         self.periods = []

#     def update_content(self):
#         periods: list | Any | None
#         user_input: timedelta | Any | None
#         caller_data = sidepanel.SidePanel.fetch_data("caller_data")

#         if not (isinstance(caller_data, tuple) and len(caller_data) == 2):
#             raise Exception("Searchbar passed wrong data")

#         periods, user_input = caller_data

#         if not isinstance(periods, list):
#             raise Exception("Results must be in a list")

#         if not isinstance(user_input, timedelta):
#             raise Exception("User input must be in timedelta")

#         self.periods = periods
#         self.user_input = user_input

#         self.result_frame.destroy()
#         self.result_frame = ttk.Frame(self)
#         for period, duration in self.periods:
#             start = period.strftime("%d/%m: %H:%M")
#             duration_mins = int(duration.total_seconds() // 60)
#             SearchResult(
#                 self.result_frame,
#                 period=period,
#                 duration=duration,
#                 text=f"{start}-{duration_mins} λεπτά",
#             ).pack(fill="x")
#         self.result_frame.pack(fill="x")
