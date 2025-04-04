Βασικές έννοιες

- App Frame
Αναφέρεται στο παράθυρο που εξυπηρετεί την κάθε λειτουργία. Π.χ.
το frame Appointments εξυπηρετεί την διαχείρηση ραντεβού

Εάν κάποιο παράθυρο χρειάζεται βοηθητικά παράθυρα, τότε θα τα λέμε
subframes.

- Overview Frame
Αναφέρεται στο frame της "αρχικής σελίδας". Είναι το πρώτο πράγμα
που βλέπει ο χρήστης όταν τρέχει το πρόγραμμα, και έχει κουμπιά που
τον μεταφέρουν στα frames που εξυπηρετούν τις υπόλοιπες λειτουργίες.


Αρχιτεκτονική

- Κατα την εκκίνηση του προγράμματος δημιουργούνται όλα τα κατάλληλα
app frames και αποθηκεύονται στην μνήμη.

- Όλα τα frames έχουν μια ασθενή σύνδεση με το Overview Frame. Δεν έχουν
εξάρτηση πατέρα-παιδιού, αλλά έχουν όλα την δυνατότητα να "επιστρέψουν"
στο overview με κουμπί.

- Yπάρχει το abstract class AppFrame που ορίζει την
κοινή συμπεριφορά που θα έχουν όλα τα App Frames. Συνεπώς κάθε App Frame
κανει inherit απο AppFrame class. Η συγκεκριμένη λειτουργία του κάθε frame
θα πρέπει να ορίζεται στην μέθοδο "body_logic()".


Προβλήματα με την προσέγγιση

- Επειδή το tkinter χρησιμοποιεί τον δικό του interpreter, δημιουργούνται
προβλήματα πολύ ιδιαίτερης φύσεως και έχουν να κάνουν με τις αρχικοποιήσεις
των γραφικών στοιχείων και την μεταφορά του state κατα την εκκίνηση του
προγράμματος. 

- Στην φάση που βρίσκεται η υλοποίηση δεν είναι σαφές πως θα διαχείριστούμε
το global state και αν εν τέλη χρειάζεται. Αυτό θα φανεί όταν θα πρέπει να
κάνουμε εναλλαγή frame με διατήρηση στοιχείων (πχ να πηγαίνουμε από τα ραντεβου
στον πελάτη και πίσω). Η αρχική ιδέα είναι να οριστεί ενα αντικείμενο με όνομα
AppContext που θα είναι προσβάσιμο σε όλα τα υποπρογράμματα, αλλά αναμένει να φανεί
πως θα συνεργάζεται με το tkinter.

