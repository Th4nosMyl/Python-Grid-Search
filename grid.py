# grid.py

from MBR import MBR
from cell import Cell  # Εισαγωγή της κλάσης Cell από cell.py

class Grid:
    def __init__(self, xL, yL, xU, yU, m):
        self.xL = xL
        self.yL = yL
        self.xU = xU
        self.yU = yU
        self.m = m  # Αριθμός διαίρεσης σε κάθε άξονα
        self.cells = [[Cell(xL + i * (xU - xL) / m,
                           yL + j * (yU - yL) / m,
                           xL + (i + 1) * (xU - xL) / m,
                           yL + (j + 1) * (yU - yL) / m) for j in range(m)] for i in range(m)]
        self.datasets = {}  # Λεξικό για αποθήκευση datasets

    def load(self, filename, dataset_label='default'):
        """Φορτώνει ένα dataset από αρχείο και το αποθηκεύει στο λεξικό datasets."""
        if dataset_label in ['A', 'B']:
            objects_list = f"objects_{dataset_label}"
        else:
            objects_list = "objects_default"

        if dataset_label in self.datasets:
            print(f"Το σύνολο '{dataset_label}' υπάρχει ήδη. Θα αντικατασταθεί.")
        data = []
        try:
            with open(filename, 'r') as file:
                header = next(file)  # Παράκαμψη επικεφαλίδων
                for line in file:
                    parts = line.strip().split(',')
                    if len(parts) != 5:
                        continue  # Παράλειψη μη έγκυρων γραμμών
                    id, xmin, ymin, xmax, ymax = parts
                    mbr = MBR(id, float(xmin), float(ymin), float(xmax), float(ymax))
                    data.append(mbr)
        except FileNotFoundError:
            print(f"Το αρχείο '{filename}' δεν βρέθηκε.")
            return
        except Exception as e:
            print(f"Σφάλμα κατά τη φόρτωση του αρχείου '{filename}': {e}")
            return
        self.datasets[dataset_label] = data
        self.assign_to_cells(data, dataset_label)
        print(f"Φορτώθηκε το dataset '{dataset_label}' από το αρχείο '{filename}' με {len(data)} ορθογωνία.")

    def assign_to_cells(self, data, dataset_label):
        """Αναθέτει κάθε MBR σε όλα τα κελιά που τέμνει."""
        for mbr in data:
            for i in range(self.m):
                for j in range(self.m):
                    cell = self.cells[i][j]
                    if cell.mbr.intersects(mbr):
                        cell.add_object(mbr, dataset_label)

    def get_dataset(self, dataset_label):
        """Επιστρέφει το dataset με το συγκεκριμένο label."""
        return self.datasets.get(dataset_label, [])

    def find_cell(self, qx, qy):
        """Βρίσκει το κελί που περιέχει το σημείο (qx, qy)."""
        if not self.cells:
            return None
        if not (self.xL <= qx <= self.xU and self.yL <= qy <= self.yU):
            return None
        cell_size_x = (self.xU - self.xL) / self.m
        cell_size_y = (self.yU - self.yL) / self.m
        i = int((qx - self.xL) / cell_size_x)
        j = int((qy - self.yL) / cell_size_y)
        # Διόρθωση για τα όρια
        if i == self.m:
            i -= 1
        if j == self.m:
            j -= 1
        return self.cells[i][j]

    def find_cells_at_hops(self, qx, qy, hop):
        """Βρίσκει όλα τα κελία που βρίσκονται σε hop βήματα από το αρχικό κελί."""
        initial_cell = self.find_cell(qx, qy)
        if not initial_cell:
            return []
        # Βρίσκουμε τα indices του αρχικού κελιού
        cell_i, cell_j = -1, -1
        for i in range(self.m):
            for j in range(self.m):
                if self.cells[i][j] == initial_cell:
                    cell_i, cell_j = i, j
                    break
            if cell_i != -1:
                break
        if cell_i == -1:
            return []

        neighbor_cells = []
        # Εξετάζουμε μόνο τα νέα κελία σε αυτό το hop
        for i in range(cell_i - hop, cell_i + hop + 1):
            for j in range(cell_j - hop, cell_j + hop + 1):
                if 0 <= i < self.m and 0 <= j < self.m:
                    # Αποκλείουμε το αρχικό κελί
                    if i == cell_i and j == cell_j:
                        continue
                    neighbor_cells.append(self.cells[i][j])
        return neighbor_cells

    def get_object_by_id(self, obj_id):
        """Επιστρέφει το αντικείμενο MBR με το συγκεκριμένο ID."""
        for dataset in self.datasets.values():
            for obj in dataset:
                if obj.id == obj_id:
                    return obj
        return None