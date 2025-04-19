# ΠΛΗΠΡΟ Προγραμματιστικό Project ΗΛΕ55 - Ραντεβού

## Documentation
Όλο το σχετικό documentation βρίσκεται στο directory docs/

## Οδηγίες εγκατάστασης

### Με το χέρι
```
Κατεβάζουμε και το project (Code -> Download Zip)
Κάνουμε unzip το αρχείο
Ανοίγουμε terminal στο directory με το setup.py
pip install .
rantevou
```
### Με εντολές χωρίς git
```
wget https://github.com/SectionX/plipro-project-rantevou/archive/refs/heads/main.zip
unzip main.zip
cd plipro-project-rantevou-main/
pip install .
rantevou
```
### Με git
```
git clone https://github.com/SectionX/plipro-project-rantevou.git
cd plipro-project-rantevou-main/
pip install .
rantevou
```
### Με pip απ'ευθείας (απαιτείται εγκατάσταση git)
```
pip install git+https://github.com/SectionX/plipro-project-rantevou.git
rantevou
```
## Που βρισκόμαστε:

Ημερολόγιο της κατάστασης υλοποίησης του προγράμματος.

### Στουραϊτης 4/4/2025
Δημιουργία σκελετού του προγράμματος και υλοποίηση των βασικών στοιχείων του Model και του View με βάση το MVC μοντέλο

### Στουραϊτης 5/4/2025
Δημιουργία των βασικών CRUD εντολών στον controller. Δημιουργία λογαριασμού gmail
και λειτουργίας αποστολής email.

### Στουραϊτης 6/4/2025
Ολοκλήρωση του gui panel που αφορά τους πελάτες, διόρθωση
δεκάδων bugs, βελτίωση της συνεργασίας μεταξύ Overview panel και App Frames. Προσθήκη σχολίων και documentation σε πολλά σημεία του κώδικα.

### Στουραϊτης 7/4/2025
Υλοποίηση του logging, υλοποίηση των βασικών class και gui elements που αφορά
τα ραντεβού, προσθήκη docstrings/σχόλια σε όλα τα functions/class που έχουν υλοποιηθεί ή έχουν αρχικοποιηθεί χωρίς υλοποίηση έως τώρα. Μαρκάρισμα με "# TODO" 
σε οτιδήποτε μένει να ολοκληρωθεί. Προσθήκη documentation για όλες τις πτυχές της υλοποίσης ως τώρα στο docs/. Αλλαγή της κεντρικής λογικής διαχείρισης παραθύρων σε πιο απλό σχήμα με tk.ttk.Notebook (μέχρι τώρα υπήρχε ένα tab σύστημα που υλοποίησα με το χέρι. Όλο αυτό έχει αλλάξει αλλα μπορεί να υπάρχουν κατάλοιπα)

### Στουραϊτης 9/4/2025
Υλοποίηση επιχειρησιακής λειτουργικότητας στα models, διορθωση και υλοποιήση πολλών συναρτήσεων του controller για κοινούς υπολογισμούς, διόρθωση πολλών bugs σε διάφορα σημεία των controllers που είχαν να κάνουν με κακό έλεγχο των τύπων σε πολυμορφικές συναρτήσεις. Έσβησα όλο τον κώδικα του view για τα ραντεβού και τον ξαναέγραψα από την αρχή επειδή έφτασα σε ένα σχετικό αδιέξοδο. Δεν έχω ενημερώσει ακόμα τα σχόλια/docstrings/documentation και ο κώδικας είναι χαοτικός λόγο αυτού. Τα βασικά στοιχεία έχουν υλοποιηθεί. Αυτό που μένει είναι επικοινωνία μεταξύ των χρονικών περιόδων, σύνδεση με τον controller ώστε ο χρήστης να μπορεί να προσθέσει και να επεξεργαστεί τα ραντεβού, και το σύστημα ειδοποιήσεων. Μετά από αυτά μένει το styling σε όλη την εφαρμογή, και αν υπάρχει χρόνος, τα στατιστικά στοιχεία.

### Στουραϊτης 11/4/2025
Για άλλη μια φορά το view των ραντεβού υλοποιήθηκε από το 0. Αυτή τη φορά όμως ήρθε για να μείνει, με ένα εντελώς OOP μοντέλο και προσέγγιση από κάτω προς τα πάνω. Ο λόγος είναι ξανά ότι βγήκα σε αδιέξοδο επειδή οι κεντρικές γραφικές μονάδες έκαναν επεξεργασία δεδομένων για όλες τις υπόλοιπες. Το αποτέλεσμα ήταν να έχει τεράστια blocks που ήταν δυσάναγνωστα και οι διορθώσεις έπαιρναν πολύ χρόνο. Επειδή πλέον έχω και καλύτερη ιδέα του πως θέλω να φαίνεται το GUI, η ιεράρχιση των στοιχείων έγινε πολύ πιο εύκολα από τις προηγούμενες προσπάθειες. Επίσης προστέθηκε ένα subscriber pattern, που διατάζει όλες τις μονάδες να ανανεώσουν τα στοιχεία τους κάθε φορά που γίνεται σημαντική αλλαγή στην βάση δεδομένων. Τέλος μεταφέρθηκε ακόμα περισσότερος κώδικας στο μοντέλο και διοθρώθηκαν αρκετά bugs (τα περισσότερα μη κρίσημα) που αφορούν database access και emails. 

Η κύρια λειτουργικότητα που μένει να υλοποιηθεί είναι η συνδεση μεταξύ της μονάδας των ραντεβού με την μονάδα των πελατών. Αλλά πριν γίνει η σύνδεση θα γίνει ένα σοβαρό refactor στην μονάδα view των πελατών.

### Στουραϊτης 12/4/2025
Ολοκλήρωση όλου του λειτουργικού κομματιού της εφαρμογής και των ζητημάτων της εργασίας. Η εφαρμογή προσφέρει τα εξής:
- Δημιουργία, επεξεργάσία και να διαγραφή ραντεβού, με ενδεικτική διάρκεια 20 λεπτών αλλά και ελευθερία αλλαγής.
- Δημιουργία, επεξεργασία και διαγραφή πελατολογίου.
- Σχεσιακή βάση δεδομένων με χρήση sqlalchemy και sqlite3
- Λειτουργία ειδοποιήσεων για προσεχή ραντεβού με δυνατότητα αποστολής email
- Γραφική επιφάνεια με χρήση tkinter

Ιδέες σχεδιασμού λογισμικού που χρησιμοποιήθηκαν
- MVC pattern, διαχωρισμός των στοιχείων της γραφικής επιφάνειας, της διαδραστικότητας με τον χρήστη και του μοντέλου των δεδομένων.
- Subscriber/Observer pattern, αυτόματη ενημέρωση των στοιχείων με την ιδέα ότι αυτά κάνουν "subscribe" στο μοντέλο.
- Singleton Pattern (python implementation), προγραμματισμός των constructor ωστε να επιστρέφουν το ίδιο instance σε όποιον το ζητάει, με σκοπό να διατηρεί τις πληροφορίες και να τις διαθέτει προς χρήση σε global επίπεδο
- Strict Typed implementation, με όλους τους απαραίτητους ελέγχους και δηλώσεις τύπων για την αποφυγή σχετικών bugs
- Caching, για μικρότερη ανάγκη ανάγνωσης από τον σκληρό δίσκο
- Logging implementation, με το πρότυπο debug, info, warn, error

Απομένουν ακόμα
- Βελτίωση της γραφικής επιφάνειας σε αισθητικό επίπεδο.
- Βελτίωση του αυτοματισμού για περαιτέρω διευκόλυνση του χρήστη
- Εμφάνιση στατιστικών στοιχείων της επιχείρησης
- Αναλυτικό documentation και σχολιασμός στον κώδικα
- Καθαρότερο γράψιμο σημείων του κώδικα που είναι υπερβολικά πολύπλοκα και φέρουν πολλαπλα type checking.

### Στουραίτης 13/04/2025

Υλοποίηση των παρακάτω
- Λειτουργία αναζήτησης πελατών με εμφάνιση κατά την πληκτρολόγηση και αγνόηση των τόνων και των κεφαλαίων
- Docstrings και σχολιασμός στον κώδικα των model
- Διόρθωση bugs κατα την ενημέρωση των ραντεβού που προκύπτουν από εσωτερικές διεργασίες του sqlalchemy
- Βελτίωση των CRUD με error checking και rollbacks
- Καθαρισμός κάποιων αχρείαστων αρχείων από τον κώδικα
- Αρχείο settings.json που ορίζει την συμπεριφορά του προγράμματος
- Υλοποίηση βασικής πλοήγησης με hotkeys (f1: ραντεβού, f2: πελάτες, f3: στατιστικα), και αυτόματη εστίαση στην μπάρα αναζήτησης πελατών
- Βελτίωση της γραφικής επιφάνειας, υλοποίηση χρωματικής κώδικοποίησης
- Βελτίωση των πληροφοριών στο Grid
- Βελτίωση πληροφοριών στο side panel του Grid
- Αυτόματη συμπλήρωση ημερομηνίας κατα την δημιουργία νέου ραντεβού  
- Υλοποίηση αυτόματης εισαγωγής πελάτη κατα την δημιουργία ραντεβού με διπλό κλικ στην εγγραφή του στο Customer Tab

### Στουραϊτης 14/04/2025

Πλέον η εφαρμογή είναι σε beta έκδοση. Θεωρώ ότι δουλεύουν τα βασικά στοιχεία όπως πρέπει και χρειάζομαι feedback. Σαφώς πρέπει να βελτιωθεί το gui σε σημεία ώστε να καταλαβαίνει καλύτερα ο χρήστης τι πρέπει να κάνει, και να έχει περισσότερο feedback στις ενέργειες του. Εφόσον έβλεπα τα πάντα από τα logs δεν ήταν σημαντικό, αλλά χωρίς αυτά είναι αρκετά χαοτικό.

Σκέφτομαι σοβαρά να ξαναγράψω όλο το side panel από την αρχή (1000~ γραμμές κώδικα) για τον πολύ απλό λόγο ότι είναι αργό, και επανέλαβα το ίδιο λάθος που έκανα στην αρχή. Υλοποίησα τα tabs με το χέρι. Δεν συνειδητοποίησα ότι το ttk.Notebook θα με εξυπηρετήσει, και τώρα ο κώδικας του είναι ένας ιστός από singletons, interfaces και data pipelines που δεν διαβάζεται. Επίσης έχει πολλά forget() και pack() που το κάνουν να φαίνεται σαν να σέρνεται. Δεν αξίζει καν να τον σχολιάσω. Θα κοιτάξω τις επόμενες μέρες μήπως μπορώ να κάνω την μετάβαση σε ttk.Notebook διατηρώντας όσο γίνεται τα γραφικά components.Όμως αυτό θα πάρει χρόνο επειδή ήδη είμαι 10 μέρες ασταμάτητα και χρειάζομαι διάλλειμα.

Το άλλο θέμα, που πάλι αφορά το side panel, είναι ότι κάνει υπολογισμούς. Είμαι σε δίλημμα επειδή οι υπολογισμοί αφορούν 90% το γραφικό κομμάτι, αλλά θα ήταν πολύ πιο βολικό αν μεταφέρονταν στο μοντέλο. Για παράδειγμα, χρειάζομαι μια λίστα από "κενά" ραντεβού ώστε να τα βάλω σε κουμπιά για τον χρήστη. Δεν είναι δεδομένα, αλλά είναι μια πληροφορία που εν γένει προέρχεται από την έννοια της βασικής οντότητας. Οι απαιτήσεις μνήμης θα αυξηθούν κατακόρυφα εάν το υλοποιήσω όμως. Δεν ειναι ιδιαίτερα σημαντικό για την εργασία, αλλά με ενοχλεί. Ίσως αν τα μοντελοποιήσω με διαφορετικό τρόπο.. οψόμεθα.

Από αλλαγές σήμερα κυρίως ασχολήθηκα με επίλυση bugs που προέρχονται από εσωτερικές λειτουργίες της sqlalchemy και της υλοποίησης των singleton. Δεν είχα ξαναχρησιμοποιήσει τον __ new __ constructor, είχα λανθασμένη εντύπωση για το πως δουλεύει, και έκανα το λάθος να έχω και new και init μαζί, οπότε η init έσβηνε τα δεδομένα που αρχικοποιούσε η new χωρίς να παραπονιέται κάπως και δεν μπορούσα να βρω το σφάλμα με τον debugger. Είναι γνωστή απροσεξία να παραγράφεις τα pointers στην python..

### Στουραΐτης 15/04/2025

- Μεταφορά πολλών class σε διαφορετικά αρχεία. Το SidePanel με τα Views είχε ξεπεράσει τις 2000 γραμμές και σήμερα πρόσθεσα άλλες 500. Ίσως να αλλάξω τις ονομασίες των αρχείων στο μέλλον. Έγινε λίγο προχειροδουλειά σε αυτό το κομμάτι.
- Αλλαγή του SidePanel σε ttk.Notebook απο ttk.Frame και δραματική απλοποίηση του κώδικα (μεγάλη βελτίωση και στο performance επειδή δεν χρειάζεται πλέον πολλά forget/pack. Το ttk.Notebook είναι βελτιστοποιημένο για αυτή την δουλειά)
- Σπάσιμο του κώδικα που αφορά είσοδο και επεξεργασία οντοτήτων. Τώρα υπάρχουν 2 components που μπορούν να κουμπώσουν σε κάθε view. Πριν κάθε view είχε την δική της υλοποίηση, η οποία κατα βάση ήταν αντιγραφή. Μένει να ολοκληρωθεί η αναβάθμιση στα views της διαχείρισης πελατών.
- Σημαντική βελτίωση των components, με refactors για να είναι πιο ευανάγνωστα.
- Δραματική απλοποίηση των υπολογισμών που κάνουν τα view components. Χρειάζεται περισσότερη δουλειά σε αυτό το κομμάτι και ευτυχώς έχω ιδέες.
- Αλλαγή της ιεραρχίας των component. Πριν κάθε class δημιουργούσε αυτόματα ότι χρειαζόταν σαν dominos. Τώρα αρχικοποιούνται εξ αρχής. Αυτό έλυσε πολλά προβλήματα με circular imports αλλά έκανε πιο πολύπλοκο το type checking, με αποτέλεσμα να πρέπει να γραψω protocols και dummy classes για να μου δώσει το ok από το MyPy. Ευτυχώς τα προβληματικά κομμάτια είναι μοναδικά στο πρόγραμμα, οπότε άπαξ και δούλεψε, πολύ δύσκολα να δημιουργήσει πρόβλημα στο μέλλον.
- Η παραπάνω αλλαγή πήρε πολλές ώρες επειδή έπρεπε να αλλάξει σημαντικά ο τρόπος που επικοινωνούν τα στοιχεία. Πριν χρησιμοποιούσε ένα dictionary σαν global state για να μεταφέρει στοιχεία. Υλοποιήθηκε με πιο διαδικαστικό στιλ, με όλες τις πληροφορίες να είναι παράμετροι σε συναρτήσεις. Κράτησα το interface/api ίδιο που διευκόλυνε την κατάσταση, αλλά δημιουργήθηκαν και ένα σωρό bugs που χρειάζονταν επίλυση και δεν τα έπιανε εύκολα το Pylance και το MyPy επειδή το tkinter δεν κάνει καλή δουλειά με τα types. Είναι όλα Misc | Any | None
- Υλοποίηση μιας στοίβας για καλύτερη πλοήγηση. Επιτρέπει την μετακίνηση σε προηγούμενο view, οπότε πλέον υπάρχουν "go back" κουμπιά. Έχει ένα bug που πρέπει να διορθωθεί, εάν πηγαίνεις μπρος πίσω με διαφορετικό τρόπο από τον προβλεπώμενο.
- Βελτίωση της ροής των στοιχείων στα view components και άρχισα να υλοποιώ και custom exceptions. Θα χρειαστεί αρκετή δουλειά για να υλοποιηθούν σε όλο το πρόγραμμα και να αποδίδουν καλύτερα από τα logs, αλλά είναι πιο ευανάγνωστα στον κώδικα.
- Σε αυτή τη φάση όλος ο κώδικας του controller έχει ολοκληρωθεί. Η εφαρμογή δεν έχει ιδιαίτερες απαιτήσεις εφόσον δεν υπάρχουν απομακρυσμένοι servers και ιδιαίτερο φορτίο. Μένει το documentation, αν και τα ονόματα των μεθόδων είναι πλήρως επεξηγηματικά και ο κώδικας σχετικά απλός.


### Στουραϊτης 16/04/2025

- Διόρθωση ενός bug όταν το view στέλνει κενά strings αντι None.
- Βελτίωση του κώδικα δημιουργίας λίστας κενών ραντεβού και προσθήκη ενός απλού μηχανισμού caching
- Βελτίωση της δημιουργίας κουμπιών για προσθήκη/επεξεργασία ραντεβού (μέχρι τώρα κατέστρεφε τα παλιά και έφτιαχνε καινούρια. Τώρα απλά ενημερώνει τα στοιχεία στα ήδη υπάρχοντα και σβήνει/προσθέτει κατα ανάγκη)
- Για όποιον συμφοιτητή θέλει να κάνει contribute, στο views/customer_view.py υπάρχουν σχόλια του πως θα υλοποιήσει ένα panel που εμφανίζει όλα τα ραντεβού για κάποιον επιλεγμένο πελάτη. Τα σχόλια αφορούν κυρίως την συνδεση με το υπόλοιπο πρόγραμμα. Βλέπε την υλοποίηση του AppointmentView για ιδέες
- Νέα ιδέα επέκτασης: Παράλληλα ραντεβού.
Μέχρι στιγμής το πρόγραμμα θεωρεί ότι μπορεί να εξυπηρετηθεί μόνο ένας πελάτης ανα χρονική περίοδο. Οπότε εαν υπάρχουν πολλοί υπάλληλοι, δεν μπορούν να μπουν τα ραντεβού ακόμα και αν γίνεται να εξυπηρετηθούν. Τεχνικά μπορεί να γίνει εάν βάλουμε μηδενική διάρκεια στο ραντεβού αλλά έτσι απλά κοροιδεύουμε το πρόγραμμα.


### Στουραϊτης 17/04/2025
Δραματικές βελτιώσεις στον χρόνο αναζήτησης, δημιουργίας και επεξεργασίας ραντεβού. Το λάθος που έγινε εξ αρχής είναι ότι θεώρησα πως η επεξεργασία στην μνήμη μέσω της python θα ήταν δραστικά πιο γρήγορη από IO στον σκληρό δίσκο (και χρησιμοποιώ έναν με 5500 RPM, πιο low spec δεν γίνεται). Tο αποτέλεσμα ήταν ότι μολις δοκίμασα να τρέξω το πρόγραμμα με 300000 εγγραφές αντι για 300, κάθε ενέργεια επεξεργασίας ραντεβού έπαιρνε 3 λεπτά.

Μετέφερα όλη την επεξεργασία στη βάση δεδομένων, πρόσθεσα indices στην στήλη της ημερομηνίας και κράτησα ένα πολύ μικρό cache με lazy loading για βασικούς επαναλαμβανόμενους υπολογισμούς που αποδεδειγμένα δουλεύει πιο γρήγορα απο sql queries. Τα 3 λεπτά έγιναν 1 δευτερόλεπτο, αν και ακόμα το θεωρώ αργό, οπότε αν χρειαστεί θα μεταφέρω τις ακριβές συναρτήσεις σε άλλο thread για να μην παγώνει το GUI και το main thread απλά θα ανανεώνει το cache, που όλα τα operations πλέον είναι Ο(1).

### Στουραϊτης 18/04/2025

- Πριν το cache ήταν ένα απλό dictionary με κάθε κλειδί να κρατάει δεδομένα για 1 συγκεκριμένη χρονική περίοδο (2 ώρες είναι το default). Τώρα είναι ένα καινούριο wrapper class γύρω από το dictionary με μεθόδους επεξεργασίας των στοιχείων, αυτόματο lazy loading στα cache misses, παραγωγή Generator για πιο εύκολη επεξεργασία των δεδομένων από το view κλπ. Ουσιαστικά είναι άλλο ένα layer μπροστά από την βάση δεδομένων. Με αυτη την υλοποίηση υπάρχει ένα υποτυπώδες interface πάνω στο οποίο μπορεί να υλοποιηθεί και third party cache service όπως redis/memcached. Σε γενικές γραμμές είμαι ευχαριστημένος με την απόδοση. Η γραφική επιφάνεια δεν μπλοκάρει αισθητά, τα operations στην βάση δεδομένων είναι αρκετά γρήγορα. Δεν θεωρώ ότι αξίζει να γίνει κάτι αλλο χωρίς περεταίρω επέκταση του προγράμματος. 

- Σχετικά με τους πελάτες, σαφώς είχαν το ίδιο πρόβλημα με τα ραντεβού, και επιπλέον πρόβλημα ότι το GUI εμφανίζει μια λίστα με τα στοιχεια πελατών, ενώ τουλάχιστον τα ραντεβού είναι ομαδοποιημένα με τρόπο που δεν είναι δυνατόν για τους πελάτες.

Στην προσπάθεια μου να βρω λύση, συνδειδητοποίησα ποσο εξαιρετικό λογισμικό είναι οι βάσεις δεδομένων. Εδώ να πω ότι το σύστημα μου έχει έναν σκληρό δίσκο 5500rpm 10ετίας. Παρόλα αυτά, η αναζήτηση στην βάση δεδομένων για n > 3000 είναι πιο γρήγορη διαβάζοντας από τον δίσκο, παρά από τα loops της python. 

Για σύγκριση, μια αναζήτηση ονόματος σε 300000 εγγραφές ήθελε μόνο 30ms στην βάση δεδομένων (με indexing), ενώ στην Python 190ms. Η διαφορά είναι δραματική και γίνεται ακόμα χειρότερη επειδή η λειτουργική ανάγκη είναι πιο σύνθετη.

Όμως υπάρχουν και αρνητικά, με το κυριότερο το Collation. Επειδή δεν ήθελα να μπλεχτώ με τα server based rdbms, χρησιμοποιώ sqlite3. Η sqlite κάνει case insensitive σύγκριση μόνο σε ASCII. Οπότε ο μόνος τρόπος που υπάρχει για να λυθεί το πρόβλημα, είναι διπλά columns για κάθε όρισμα που δέχεται ελληνικούς χαρακτήρες. Προσπάθησα να βρω πολλές λύσεις, ακόμα και custom collation στην sqlalchemy, αλλα τίποτα δεν δουλεύει.

Το δεύτερο πρόβλημα που αντιμετώπισα ήταν ότι μετά από 3-4 χιλιάδες εγγραφές, το treeview γίνεται δραματικά αργό. Αυτό σημαίνει ότι πρέπει να μπει pagination. Ίσως να είναι και μια καλή ευκαιρία να αλλάξω το μοντέλο για να περιορίσω την χρήση μνήμης.

Αλλαγές
- Αλλαγή του αλγόριθμου αναζήτησης, πλέον δεν γίνεται με python loop αλλα με αναζήτηση στην βάση δεδομένων. Μέσος χρόνος αναζήτησης 300ms για 300,000 πελάτες στην μηχανή μου συγκριτικά με 1000+ ms που ήταν πριν
- Ασύγχρονος μηχανισμός που περιμένει 400ms πριν εκτελέσει την αναζήτηση μετά το πάτημα του τελευταίου πλήκτρου. Έτσι δεν κλειδώνει η γραφική επιφάνεια και μειώνονται οι συνολικές αναζητήσεις (πριν έκανε αναζήτηση για κάθε πάτημα πλήκτρου)
- Περιορισμός στην εμφάνιση των πελατών σε 100 ανα σελίδα. Έτσι λύθηκε το πρόβλημα που κλείδωνε η γραφική επιφάνεια μέχρι να γεμίσει η λίστα με τους πελάτες. Ο μηχνισμός pagination δεν έχει υλοποιηθεί ακόμα.
- Διόρθωση ορισμένων bug στην επεξεργασία ραντεβού. Στην αλλαγή ημερομηνίας, υπο συνθήκες, άφηνε ένα αντίγραφο του παλιού ραντεβού στο cache. Τώρα δουλεύει όπως πρέπει.
- Καθαρισμός του κώδικα και διόρθωση bugs που είχαν να κάνουν με αρχικοποιήσεις σε global scope. Το αποτέλεσμα είναι να προσπαθούν να διαβάσουν από την βάση δεδομένων πριν αρχικοποιηθεί σωστά ο μηχανισμός. Τo bug εμφανίστηκε όταν έκανα ολικό reset την βάση δεδομένων, γιαυτό άργησα τόσο πολύ να το εντοπίσω.

# Στουραϊτης 19/04/2025

- Αλλαγή στο delay της αναζήτησης να είναι βάση του πλήθους των εγγραφών. Εφόσον το πρόγραμμα προορίζεται για πιο μικρές επιχειρήσεις, είναι υπερβολή τα 400 ms. Αλλάξε σε (50 + n // 1000)ms. Εφόσον η χρονική πολυπλοκότητα είναι Ο(n), θα κάνει scaling στα επίπεδα που υπολόγιζα.
- Υλοποίηση του pagination στο view των πελατών. Δεν ειναι βελτιστοποιημένο να μειώνει την χρήση μνήμης, αλλά μειώνει δραματικά τους χρόνους rendering.
- Διόρθωση των sort αλγορίθμων να δουλεύουν σωστά με τις νέες αλλαγές.
- Έλεγχος ορθής λειτουργίας των παρακάτω διαδικασιών με μεγάλο όγκο δεδομένων
1. Προσθήκη ραντεβού 
2. Επεξεργασία ραντεβού
3. Διαγραφή ραντεβού
4. Προσθήκη ραντεβού με νέο πελάτη
5. Προσθήκη ραντεβού με παλιό πελάτη
6. Επεξεργασία ραντεβού με επεξεργασία πελάτη
7. Προσθήκη νέου πελάτη
8. Επεξεργασία παλιού πελάτη
9. Διαγραφή παλιού πελάτη
10. Λειτουργία αναζήτησης
11. Λειτουργία sort σε όλη την λίστα
12. Λειτουργία sort σε αποτελέσματα αναζήτησης

Μένει να υλοποιηθεί
- View πελατών με τα ραντεβού τους, ιστορικό και τρέχων
- View στατιστικών με εμφάνιση
1. Ραντεβού ανα περιοδο, ημερα, ημερομηνια, έτος
2. Μέσο πλήθος ραντεβού ανα πελάτη
3. Μέσος χρόνος ραντεβού

Το πρόγραμμα προς το παρών δεν υποστηρίζει κάτι έξτρα όπως έσοδα αλλα υπο συνθήκες είναι σχετικά εύκολο να υλοποιηθεί

Επίσης θα μπορουσε να υλοποιηθεί και ένα πεδίο για σχόλια/παρατηρήσεις

Η τελική βελτίωση είναι να υποστηρίζει και πολλούς υπαλλήλους.Υπάρχει μια ιδέα για τρόπο υλοποίησης αλλά δεν θα γίνει στο προσεχές μέλλον.