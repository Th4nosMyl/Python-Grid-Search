# grid.py

from MBR import MBR
from cell import Cell

class Grid:
    """
    Κλάση που αναπαριστά ένα πλέγμα (Grid) αποτελούμενο από m x m κελιά (Cells).
    Χρησιμοποιείται για τη διαχείριση και ανάθεση MBRs σε διαφορετικά datasets
    μέσα στην περιοχή [xL, xU] x [yL, yU].
    """

    def __init__(self, xL, yL, xU, yU, m):
        """
        Αρχικοποιεί το Grid, δημιουργώντας m x m κελιά για την περιοχή
        [xL, xU] x [yL, yU].

        :param xL: Ελάχιστο x-όριο όλου του πλέγματος.
        :param yL: Ελάχιστο y-όριο όλου του πλέγματος.
        :param xU: Μέγιστο x-όριο όλου του πλέγματος.
        :param yU: Μέγιστο y-όριο όλου του πλέγματος.
        :param m:  Πλήθος κελιών ανά άξονα. Το τελικό Grid θα έχει m x m κελιά.
        """
        self.xL = xL
        self.yL = yL
        self.xU = xU
        self.yU = yU
        self.m = m

        # Δημιουργία 2D λίστας κελιών (m x m).
        self.cells = [
            [
                Cell(
                    xL + i * (xU - xL) / m,
                    yL + j * (yU - yL) / m,
                    xL + (i + 1) * (xU - xL) / m,
                    yL + (j + 1) * (yU - yL) / m
                )
                for j in range(m)
            ]
            for i in range(m)
        ]

        # Λεξικό για την αποθήκευση των datasets (π.χ. {'A': [...], 'B': [...]}).
        self.datasets = {}

    def load(self, filename, dataset_label='default'):
        """
        Φορτώνει ένα dataset από ένα CSV αρχείο και το αποθηκεύει στο λεξικό
        self.datasets[dataset_label]. Στη συνέχεια καλεί τη μέθοδο assign_to_cells
        για να τοποθετήσει τα MBRs στα αντίστοιχα κελιά του Grid.

        :param filename: Όνομα του αρχείου CSV (με γραμμές: ID,xmin,ymin,xmax,ymax).
        :param dataset_label: Ετικέτα (string) για το συγκεκριμένο dataset.
        """
        if dataset_label in self.datasets:
            print(f"Το σύνολο '{dataset_label}' υπάρχει ήδη. Θα αντικατασταθεί.")

        data = []
        try:
            with open(filename, 'r') as file:
                header = next(file, None)  # Παράκαμψη επικεφαλίδας, αν υπάρχει
                for line in file:
                    parts = line.strip().split(',')
                    if len(parts) != 5:
                        continue  # Αγνόηση μη έγκυρων γραμμών

                    id_str, xmin_str, ymin_str, xmax_str, ymax_str = parts
                    try:
                        xmin = float(xmin_str)
                        ymin = float(ymin_str)
                        xmax = float(xmax_str)
                        ymax = float(ymax_str)

                        if xmin > xmax or ymin > ymax:
                            continue
                        data.append(MBR(id_str, xmin, ymin, xmax, ymax))
                    except ValueError:
                        # Αγνοούμε γραμμή αν δεν μετατρέπεται σε float
                        continue
        except FileNotFoundError:
            print(f"Το αρχείο '{filename}' δεν βρέθηκε.")
            return
        except Exception as e:
            print(f"Σφάλμα κατά τη φόρτωση του αρχείου '{filename}': {e}")
            return

        self.datasets[dataset_label] = data
        self.assign_to_cells(data, dataset_label)
        print(f"Φορτώθηκε το dataset '{dataset_label}' από το αρχείο '{filename}' με {len(data)} ορθογώνια.")

    def assign_to_cells(self, data, dataset_label):
        """
        Αναθέτει τα MBRs σε όλα τα κελιά του Grid που πιθανώς τα περιέχουν,
        υπολογίζοντας τους δείκτες κελιών (i_min .. i_max, j_min .. j_max).

        :param data: Λίστα με MBR αντικείμενα (π.χ. από ένα CSV).
        :param dataset_label: Ετικέτα dataset (string).
        """
        if self.m == 0:
            return  # Σε περίπτωση που m=0, δεν δημιουργούνται κελιά

        cell_size_x = (self.xU - self.xL) / self.m
        cell_size_y = (self.yU - self.yL) / self.m

        for mbr in data:
            i_min = int((mbr.xmin - self.xL) // cell_size_x)
            i_max = int((mbr.xmax - self.xL) // cell_size_x)
            j_min = int((mbr.ymin - self.yL) // cell_size_y)
            j_max = int((mbr.ymax - self.yL) // cell_size_y)

            i_min = max(0, min(i_min, self.m - 1))
            i_max = max(0, min(i_max, self.m - 1))
            j_min = max(0, min(j_min, self.m - 1))
            j_max = max(0, min(j_max, self.m - 1))

            for i in range(i_min, i_max + 1):
                for j in range(j_min, j_max + 1):
                    cell = self.cells[i][j]
                    if cell.mbr.intersects(mbr):
                        cell.add_object(mbr, dataset_label)

    def get_dataset(self, dataset_label):
        """
        Επιστρέφει όλα τα MBRs που ανήκουν στο dataset με ετικέτα dataset_label.
        Εάν δεν υπάρχει τέτοιο dataset, επιστρέφει κενή λίστα.

        :param dataset_label: Ετικέτα (string) του dataset.
        :return: Λίστα από MBR αντικείμενα.
        """
        return self.datasets.get(dataset_label, [])

    def find_cell(self, qx, qy):
        """
        Επιστρέφει το κελί που περιέχει το σημείο (qx, qy), αν αυτό βρίσκεται
        εντός των ορίων του Grid. Επιστρέφει None αν βρίσκεται εκτός ορίων
        ή αν δεν υπάρχουν καθόλου κελιά.

        :param qx: Συντεταγμένη x του σημείου.
        :param qy: Συντεταγμένη y του σημείου.
        :return: Ένα αντικείμενο Cell ή None.
        """
        if not self.cells:
            return None
        if not (self.xL <= qx <= self.xU and self.yL <= qy <= self.yU):
            return None

        cell_size_x = (self.xU - self.xL) / self.m
        cell_size_y = (self.yU - self.yL) / self.m

        i = int((qx - self.xL) / cell_size_x)
        j = int((qy - self.yL) / cell_size_y)

        if i == self.m: i -= 1
        if j == self.m: j -= 1

        return self.cells[i][j]

    def find_cells_at_hops(self, qx, qy, hop):
        """
        Βρίσκει όλα τα κελιά που βρίσκονται σε ακτίνα 'hop' γύρω από το κελί
        που περιέχει το σημείο (qx, qy). Η ακτίνα ορίζεται σε επίπεδο index
        (π.χ. cell_i ± hop).

        :param qx: Συντεταγμένη x του σημείου αναζήτησης.
        :param qy: Συντεταγμένη y του σημείου αναζήτησης.
        :param hop: Απόσταση σε μονάδες κελιών (integer).
        :return: Λίστα από Cell που βρίσκονται εντός αυτής της περιοχής.
        """
        initial_cell = self.find_cell(qx, qy)
        if not initial_cell:
            return []

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
        for i in range(cell_i - hop, cell_i + hop + 1):
            for j in range(cell_j - hop, cell_j + hop + 1):
                if 0 <= i < self.m and 0 <= j < self.m:
                    if i == cell_i and j == cell_j:
                        continue
                    neighbor_cells.append(self.cells[i][j])
        return neighbor_cells

    def get_object_by_id(self, obj_id):
        """
        Αναζητά ένα MBR με το συγκεκριμένο ID σε όλα τα loaded datasets
        (π.χ. 'A', 'B', 'default') και επιστρέφει το πρώτο που βρεθεί.
        Διαφορετικά, επιστρέφει None.

        :param obj_id: Το ID (string) του αντικειμένου.
        :return: Ένα αντικείμενο MBR ή None αν δεν βρεθεί.
        """
        for dataset in self.datasets.values():
            for obj in dataset:
                if obj.id == obj_id:
                    return obj
        return None
