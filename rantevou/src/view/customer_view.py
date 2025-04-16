# TODO Ένα side view που δείχνει στοιχεία και όλα τα
# ραντεβού για τον συγκεκριμένο πελάτη

# Για να υλοποιηθεί πρέπει να γίνουν τα εξής βήματα
# 1. Εισαγωγή του SideView για να κληρονομηθεί από το καινούριο αντικείμενο
#    class CustomerView(SideView)
# 2. Αρχικοποίηση των στοιχείων του View στην __init__, και δημιουργία μεθόδου
#    .update_content(...). Δες το class AppointmentView στο /view/appointment_view.py
# 3. Εισαγωγή του CustomerView στο SidePanel, που γίνεται στο /view/window.py
# 4. Δημιουργία κουμπιού στο ManagmentBar του /view/customers.py που παίρνει τα στοιχεία
#    από το worksheet (worksheet.focus_values), κάνει αναζήτηση στην βάση δεδομένων
#    και το στέλνει στο καινούριο CustomerView μέσω της συνάρτησης "self.sidepanel.select_view(...)"
