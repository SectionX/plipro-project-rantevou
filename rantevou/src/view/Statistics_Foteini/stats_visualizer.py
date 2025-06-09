import requests
import matplotlib.pyplot as plt


def fetch_stats():
    url = "http://localhost:5000/stats/overview"
    response = requests.get(url)
    return response.json()


def plot_stats(stats):
    # 1. Πλήθος ανά ημέρα
    days = list(stats["appointments_per_day"].keys())
    values = list(stats["appointments_per_day"].values())

    plt.figure(figsize=(10, 5))
    plt.bar(days, values)
    plt.xticks(rotation=45)
    plt.title("Πλήθος ραντεβού ανά ημέρα")
    plt.ylabel("Ραντεβού")
    plt.tight_layout()
    plt.show()

    # 2. Πλήθος ανά εβδομάδα
    weeks = list(stats["appointments_per_week"].keys())
    week_values = list(stats["appointments_per_week"].values())

    plt.figure(figsize=(8, 4))
    plt.plot(weeks, week_values, marker="o")
    plt.title("Πλήθος ραντεβού ανά εβδομάδα")
    plt.ylabel("Ραντεβού")
    plt.xticks(rotation=30)
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # 3. Μέση διάρκεια
    avg = stats["average_duration_minutes"]
    plt.figure()
    plt.bar(["Μέση διάρκεια"], [avg])
    plt.title("Μέση διάρκεια ραντεβού")
    plt.ylabel("Λεπτά")
    plt.ylim(0, max(avg + 10, 30))
    plt.tight_layout()
    plt.show()

    # 4. Πιο δραστήριος πελάτης
    customer = stats["most_active_customer"]
    count = stats["most_active_customer_appointments"]
    name = f"{customer.get('name')} {customer.get('surname', '')}"
    print(f" Πιο δραστήριος πελάτης: {name} ({count} ραντεβού)")


if __name__ == "__main__":
    stats = fetch_stats()
    plot_stats(stats)
