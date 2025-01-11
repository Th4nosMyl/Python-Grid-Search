from MBR import MBR

class Cell:
    def __init__(self, xmin, ymin, xmax, ymax):
        """
        Μια Cell (κελί) περιέχει ένα MBR οριοθέτησης και
        ένα λεξικό για αποθήκευση MBRs διαφορετικών datasets.
        
        :param xmin: Ελάχιστο x-όριο του κελιού
        :param ymin: Ελάχιστο y-όριο του κελιού
        :param xmax: Μέγιστο x-όριο του κελιού
        :param ymax: Μέγιστο y-όριο του κελιού
        """
        self.mbr = MBR(None, xmin, ymin, xmax, ymax)  # Ορίζουμε id=None για κελιά του grid
        # Αντί για 3 ξεχωριστές λίστες (objects_A, objects_B, objects_default),
        # χρησιμοποιούμε ένα λεξικό όπου κάθε key είναι το dataset_label (π.χ. 'A','B','default','C' κ.λπ.).
        self.objects = {}

    def add_object(self, mbr, dataset_label='default'):
        """
        Προσθέτει ένα αντικείμενο (MBR) στο λεξικό self.objects
        βάσει του dataset_label.

        :param mbr: Το MBR αντικείμενο που θέλουμε να αποθηκεύσουμε
        :param dataset_label: Ετικέτα dataset (π.χ. 'A', 'B', 'default', κ.λπ.)
        """
        if dataset_label not in self.objects:
            self.objects[dataset_label] = []
        self.objects[dataset_label].append(mbr)

    def __repr__(self):
        """
        Επιστρέφει μια συμβολοσειρά που παρουσιάζει το MBR του κελιού
        και τον αριθμό αντικειμένων ανά dataset_label.
        """
        objects_summary = {k: len(v) for k, v in self.objects.items()}
        return f"Cell(mbr={self.mbr}, objects={objects_summary})"
