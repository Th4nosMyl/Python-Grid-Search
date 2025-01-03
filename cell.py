# cell.py

from MBR import MBR

class Cell:
    def __init__(self, xmin, ymin, xmax, ymax):
        self.mbr = MBR(None, xmin, ymin, xmax, ymax)  # Ορίζουμε id=None για κελιά του grid
        self.objects_A = []
        self.objects_B = []
        self.objects_default = []  # Για single-dataset αλγορίθμους

    def add_object(self, mbr, dataset_label='default'):
        """Προσθέτει ένα αντικείμενο στο κατάλληλο σύνολο."""
        if dataset_label == 'A':
            self.objects_A.append(mbr)
        elif dataset_label == 'B':
            self.objects_B.append(mbr)
        else:
            self.objects_default.append(mbr)

    def __repr__(self):
        return (f"Cell(mbr={self.mbr}, "
                f"objects_A={len(self.objects_A)}, "
                f"objects_B={len(self.objects_B)}, "
                f"objects_default={len(self.objects_default)})")
