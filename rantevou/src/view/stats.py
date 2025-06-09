import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import requests

from .abstract_views import AppFrame


class Statistics(AppFrame):
    def __init__(self, root):
        super().__init__(root)

        self.pack(fill="both", expand=True)
        self.canvas = None

        ttk.Label(self, text=" Στατιστικά Ραντεβού", font=("Arial", 16, "bold")).pack(pady=10)

        self.info_label = ttk.Label(self, text="Φόρτωση δεδομένων...")
        self.info_label.pack()

        self.after(500, self.load_and_display_stats)  # Καθυστέρηση για να φορτωθεί σωστά το UI

    def load_and_display_stats(self):
        stats = self.fetch_stats()
        if not stats:
            self.info_label.config(text="Αποτυχία φόρτωσης στατιστικών.")
            return

        # --- Εμφάνιση στατιστικών ως κείμενο ---
        customer = stats.get("most_active_customer", {})
        name = f"{customer.get('name', '')} {customer.get('surname', '')}"
        duration = stats.get("average_duration_minutes", 0)
        count = stats.get("most_active_customer_appointments", 0)

        text = f"🔹 Πιο δραστήριος πελάτης: {name} ({count} ραντεβού)\n" f"🔹 Μέση διάρκεια: {duration} λεπτά"
        self.info_label.config(text=text)

        # --- Εμφάνιση γραφήματος: Ραντεβού ανά ημέρα ---
        self.plot_bar_chart(stats["appointments_per_day"])

    def plot_bar_chart(self, data):
        fig, ax = plt.subplots(figsize=(6, 3))
        days = list(data.keys())
        counts = list(data.values())

        ax.bar(days, counts)
        ax.set_title("Ραντεβού ανά ημέρα")
        ax.set_ylabel("Πλήθος")
        ax.tick_params(axis="x", rotation=45)
        fig.tight_layout()

        if self.canvas:
            self.canvas.get_tk_widget().destroy()

        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(pady=10)

    def fetch_stats(self):
        try:
            response = requests.get("http://localhost:5000/stats/overview")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            try:
                return self.fetch_from_db()
            except Exception as e:
                print(f"[Σφάλμα] Δεν φορτώθηκαν τα στατιστικά: {e}")
                return {}

    def fetch_from_db(self):
        from collections import defaultdict
        from statistics import mean
        from ..controller.customers_controller import CustomerControl
        from ..controller.appointments_controller import AppointmentControl

        appointments_data = AppointmentControl().get_appointments()

        daily_counts = defaultdict(int)
        weekly_counts = defaultdict(int)
        customer_counter = defaultdict(int)
        durations = []

        for _, appointments in appointments_data.items():
            for apt in appointments:
                date = apt.date
                daily_key = date.date().isoformat()
                weekly_key = f"{date.isocalendar().year}-W{date.isocalendar().week}"
                customer_id = apt.customer_id
                duration = apt.duration.total_seconds() / 60

                daily_counts[daily_key] += 1
                weekly_counts[weekly_key] += 1
                customer_counter[customer_id] += 1
                durations.append(duration)

        customer_counter.pop(None)
        most_active_customer_id = max(customer_counter, key=customer_counter.get, default=None)
        customer_ctrl = CustomerControl()
        most_active_customer = (
            customer_ctrl.get_customer_by_id(most_active_customer_id).to_dict_api()
            if most_active_customer_id is not None
            else None
        )

        average_duration = round(mean(durations), 2) if durations else 0

        return {
            "appointments_per_day": dict(sorted(daily_counts.items())),
            "appointments_per_week": dict(sorted(weekly_counts.items())),
            "most_active_customer": most_active_customer,
            "most_active_customer_appointments": customer_counter.get(most_active_customer_id, 0),
            "average_duration_minutes": average_duration,
        }
