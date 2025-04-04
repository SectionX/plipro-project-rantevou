"""
Ορίζει το κεντρικό παράθυρο της εφαρμογής πάνω στο οποίο υπάρχουν όλα
τα σχετικά frames της εφαρμογής (με frame εννοούμε τα παράθυρα που αφορούν
την κάθε ξεχωριστή λειτουργία της εφαρμογής)

Η "αρχική σελίδα" της εφαρμογής είναι η Overview, όπως ορίζεται στο views/overview.py
και φέρει κουμπιά που καλούν τα συγκεκριμένα frames. Πχ το κουμπί "Appointments"
ανοίγει το frame της εφαρμογής "Appointments". Το πρόγραμμα την αναγνωρίζει και
την διαχειρίζεται αυτόματα.
"""

import tkinter as tk
from collections import OrderedDict


class Window(tk.Tk):

    def __init__(self, title="Appointments App", width=800, height=600):
        super().__init__()
        self.geometry(f"{width}x{height}")
        self.title(title)
        self.children = OrderedDict()

    def load_frames(self, frames: list):
        """
        Αυτή η συνάρτηση υπάρχει για να λύσει ένα πρόβλημα που μάλλον
        δημιουργείται λόγο της απειρίας μου με το tkinter.

        1. Λύνει το θέμα των προβληματικών imports. Πολύ συνοπτικά δεν σε
        αφήνει να αρχικοποιήσεις κάποιο widget και να το μεταφέρεις μέσω
        import σε άλλο module, ή αν σε αφήνει δημιουργεί bugs.
        Αυτό γίνεται μάλλον επειδή το tkinter είναι γραμμένο σε γλώσσα "tcl"
        και καλεί τον tcl interpreter όταν εκτελεί σχετικές εντολές

        2. Αυτοματοποιεί την επιλογή του frame "overview" ώς "αρχική σελίδα"
        του προγράμματος.

        3. Αλλάζει το σχήμα ονομασίας των widget από "!name" σε "name".

        Παράδειγμα προβλήματος: Ενώ έχω αρχικοποιήσει το property "self.children"
        σε κενό dictionary, το tkinter χωρίς να με ρωτήσει πάει και το γεμίζει.
        Αυτή η συμπεριφορά είναι πολύ ανορθόδοξη.

        Η συνάρτηση εκτελείται μια φορά στο αρχείο rantevou/__main__.py και δεν
        υπάρχει λόγος να ξανακληθεί κάπου αλλού, οπότε συνίσταται να ξεχάσετε
        την ύπαρξη της.

        Ιδανικά δεν θα υπάρξει λόγος να πειράξουμε τις αρχικοποιήσεις στο
        υπόλοιπο πρόγραμμα και αυτή η συνάρτηση θα μείνει ως μια κακή ανάμνηση.
        """

        self.children.clear()  # Καθαρίζει τα κατάλοιπα του tkinter
        for frame in frames:
            self.children[frame.name] = frame

        self.children["overview"].initialize(self.children)  # type: ignore
        self.windowframe = self.children["overview"]
        self.windowframe.pack(fill="both", expand=True)

    def change_frame(self, frame_name):
        """
        Αλλάζει το ενεργό frame στο παράθυρο. Χρησιμοποείται από το widget
        GoToButton στο views/navigation.py
        """
        self.windowframe.forget()
        self.windowframe = self.children[frame_name]
        self.windowframe.pack(fill="both", expand=True)

    def run(self):
        self.mainloop()
        self.destroy()
