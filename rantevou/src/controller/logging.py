"""
Ένα πολύ απλό πρόγραμμα logging. Προτιμήθηκε μια απλή υλοποίηση
παρά να κάνουμε χρήση του logger της Python ή κάποιου third party
επειδή η χρήση τους είναι σχετικά πολύπλοκη και η εφαρμογή μας
είναι απλή και δεν αξίζει να προσθέσουμε τέτοιο τεχνικό κόστος

Επεξήγηση των επιπέδων:

DEBUG - Όταν κατα την προσπάθεια υλοποίησης του προγράμματος, θέλουμε
        να δούμε ότι κάτι πιο φτιάξαμε παράγει το σωστό αποτέλεσμα

        Πχ θέλουμε να γράψουμε μια συνάρτηση που προσθέτει έναν καινούριο
        πελάτη στην βαση δεδομένων. Επειδή δεν είμαστε σίγουροι ότι ο κώδικας
        δουλεύει όπως πρέπει, κάνουμε print στο τερματικό τα στοιχεία του και
        βλέπουμε αν είναι σωστά.

        Αντί για print, χρησιμοποιούμε log_debug()

INFO - Αφού έχει υλοποιηθεί σωστά το πρόγραμμα/υποπρόγραμμα, εαν θέλουμε
       να γνωστοποιήσουμε ότι κάποια εργασία έχει ολοκληρωθεί.

       Πχ Εφόσον η συνάρτηση που προσθέτει τον πελάτη έχει υλοποιηθεί
       σωστά, καταγράφουμε το γεγονός ότι χρησιμοποιήθηκε κάθε φορά που
       το πρόγραμμα την καλεί.

       Σε αυτή την περίπτωση χρησιμοποιούμε log_info()

WARN - Αφού έχει υλοποιηθεί σωστά το πρόγραμμα/υποπρόγραμμα, εαν θέλουμε
       να γνωστοποιήσουμε ότι κάποια εργασία δεν ολοκληρώθηκε επειδή ο χρήστης
       έκανε κάποιο λάθος

       Πχ Εάν ο χρήστης πάει να προσθέσει έναν πελάτη αλλά δεν βάλει τα
       απαραίτητα στοιχεία, το πρόγραμμα μας θα τον σταματήσει. Σε αυτή
       την περίπτωση μπορούμε να καταγράψουμε αυτό το γεγονός χρησιμοποιόντας
       την log_warn()


ERROR - Αυτή η περίπτωση είναι για κάποιο καταστροφικό σφάλμα. Πχ έστω ότι για
        να δουλέψει το πρόγραμμα χρειάζεται ένα αρχείο config που διαβάζει κατα
        την εκκίνηση. Εάν δεν βρεθεί αυτό το αρχείο (ίσως επειδή καταλάθος κάποιος
        το διέγραψε), τότε ενημερώνουμε χρησιμοποιόντας το επίπεδο Error.


Τέλος το επίπεδο λειτουργίας (Logger.level) μας λέει πόσα από αυτά τα μυνήματα
να εκτυπωθούν στο terminal.

Εάν το επίπεδο είναι 0, τότε εκτυπώνονται όλα
Εάν είναι 1, τότε εκτυπώνονται INFO, WARN, ERROR
Εάν είναι 2, τότε εκτυπώνονται WARN, ERROR
Εάν είναι 3, τότε εκτυπώνονται ERROR
Εάν είναι 4 τότε δεν εκτυπώνεται τίποτα
"""

from __future__ import annotations

import datetime
import pathlib
import shutil
import zipfile
import re
import sys
from typing import Literal


class Logger:

    pattern_date = re.compile(r"\[\d+-\d+-(\d+)")
    logfile_path = pathlib.Path(__file__).parent.parent.parent / "data" / "log.txt"
    zipfile_path = pathlib.Path(__file__).parent.parent.parent / "data" / "log.zip"
    level = 0
    levels = ["DEBUG", "INFO", "WARN", "ERROR"]

    @classmethod
    def archive_day(cls):
        with cls.logfile_path.open("r") as f:
            first = next(f)

        date_search = cls.pattern_date.search(first)
        if not date_search:
            return

        day_log = int(date_search.group(1))
        day_now = datetime.datetime.now().day

        if day_now == day_log:
            return

        date = f"{date_search.group()}]"
        dst = cls.logfile_path.parent / f"log-{date}.txt"
        shutil.move(
            src=str(cls.logfile_path),
            dst=str(dst),
        )

        zf = zipfile.ZipFile(
            file=str(cls.zipfile_path),
            mode="a",
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=9,
        )
        zf.write(
            filename=str(dst),
            arcname=dst.name,
        )
        dst.unlink()

    def __init__(self, name=""):
        self.name = name

    def write_to_file(self, message):
        with self.logfile_path.open("a") as f:
            f.write(message + "\n")

    def log(self, message: str, severity: Literal["DEBUG", "INFO", "WARN", "ERROR"]):
        message = f"{severity} - [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]: {message} - {self.name}"
        self.write_to_file(message)

        if self.level <= self.levels.index(severity):
            print(message, file=sys.stderr)

    def log_debug(self, message: str) -> None:
        self.log(message, "DEBUG")

    def log_info(self, message: str) -> None:
        self.log(message, "INFO")

    def log_warn(self, message: str) -> None:
        self.log(message, "WARN")

    def log_error(self, message: str) -> None:
        self.log(message, "ERROR")
