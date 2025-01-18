# cell.py

from MBR import MBR

class Cell:
    """
    Κλάση που αναπαριστά ένα κελί (Cell) του Grid, με ένα bounding MBR και ένα λεξικό
    για την αποθήκευση των αντικειμένων (MBRs) ανά dataset_label.
    """

    def __init__(self, xmin, ymin, xmax, ymax):
        """
        Αρχικοποιεί ένα κελί (Cell) ορίζοντας το αντίστοιχο Bounding MBR
        και προετοιμάζει ένα λεξικό objects για την αποθήκευση MBRs ανά dataset.

        :param xmin: Ελάχιστο x-όριο του κελιού.
        :param ymin: Ελάχιστο y-όριο του κελιού.
        :param xmax: Μέγιστο x-όριο του κελιού.
        :param ymax: Μέγιστο y-όριο του κελιού.
        """
        self.mbr = MBR(None, xmin, ymin, xmax, ymax)
        self.objects = {}

    def add_object(self, mbr, dataset_label='default'):
        """
        Προσθέτει ένα αντικείμενο (MBR) στο λεξικό self.objects, ομαδοποιημένο
        βάσει του dataset_label (π.χ. 'A', 'B', 'default').

        :param mbr: Ένα αντικείμενο MBR που θέλουμε να αποθηκεύσουμε σε αυτό το κελί.
        :param dataset_label: Η ετικέτα dataset στην οποία ανήκει το MBR.
        """
        if dataset_label not in self.objects:
            self.objects[dataset_label] = []
        self.objects[dataset_label].append(mbr)

    def __repr__(self):
        """
        Επιστρέφει μια περιγραφή του κελιού (Cell), συμπεριλαμβάνοντας το bounding MBR
        και ένα σύνοψης αριθμό αντικειμένων ανά dataset_label.

        :return: Συμβολοσειρά που περιγράφει το κελί.
        """
        objects_summary = {k: len(v) for k, v in self.objects.items()}
        return f"Cell(mbr={self.mbr}, objects={objects_summary})"
