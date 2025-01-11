from MBR import MBR
from cell import Cell

class Grid:
    def __init__(self, xL, yL, xU, yU, m):
        """
        Δημιουργεί ένα πλέγμα (Grid) από m x m κελιά (Cell), καλύπτοντας την
        περιοχή [xL, xU] x [yL, yU].
        
        :param xL: Ελάχιστο x-όριο όλου του πλέγματος
        :param yL: Ελάχιστο y-όριο όλου του πλέγματος
        :param xU: Μέγιστο x-όριο όλου του πλέγματος
        :param yU: Μέγιστο y-όριο όλου του πλέγματος
        :param m:   Πλήθος κελιών κατά άξονα (διάσταση του grid)
        """
        self.xL = xL
        self.yL = yL
        self.xU = xU
        self.yU = yU
        self.m = m  # Αριθμός διαίρεσης σε κάθε άξονα

        # Δημιουργία 2D λίστας (m x m) με κελιά
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

        # Λεξικό για να αποθηκεύουμε τα datasets που φορτώνουμε (π.χ. {'A': [...], 'B': [...], ...})
        self.datasets = {}

    def load(self, filename, dataset_label='default'):
        """
        Φορτώνει ένα dataset από αρχείο CSV που περιέχει γραμμές της μορφής:
        
            id, xmin, ymin, xmax, ymax
        
        και το αποθηκεύει στο λεξικό self.datasets[dataset_label].
        Στη συνέχεια καλεί τη συναρτηση assign_to_cells για να τοποθετήσει
        τα MBRs στα κελιά.

        :param filename: Όνομα του αρχείου CSV
        :param dataset_label: Ετικέτα με την οποία θα αποθηκευτεί το dataset στο Grid
        """
        if dataset_label in self.datasets:
            print(f"Το σύνολο '{dataset_label}' υπάρχει ήδη. Θα αντικατασταθεί.")

        data = []
        try:
            with open(filename, 'r') as file:
                header = next(file)  # Παράκαμψη της επικεφαλίδας

                for line in file:
                    parts = line.strip().split(',')
                    if len(parts) != 5:
                        # Παράλειψη μη έγκυρων γραμμών
                        continue

                    id_str, xmin_str, ymin_str, xmax_str, ymax_str = parts
                    try:
                        xmin = float(xmin_str)
                        ymin = float(ymin_str)
                        xmax = float(xmax_str)
                        ymax = float(ymax_str)

                        # Προαιρετικός έλεγχος εγκυρότητας (π.χ. xmin <= xmax)
                        if xmin > xmax or ymin > ymax:
                            # Αγνοούμε αυτή τη γραμμή αν τα όρια είναι ασύμβατα
                            continue

                        mbr = MBR(id_str, xmin, ymin, xmax, ymax)
                        data.append(mbr)
                    except ValueError:
                        # Αν κάποια τιμή δεν μπορεί να μετατραπεί σε float, αγνοούμε τη γραμμή
                        continue

        except FileNotFoundError:
            print(f"Το αρχείο '{filename}' δεν βρέθηκε.")
            return
        except Exception as e:
            print(f"Σφάλμα κατά τη φόρτωση του αρχείου '{filename}': {e}")
            return

        # Φυλάμε τη λίστα των MBRs στο λεξικό
        self.datasets[dataset_label] = data

        # Αναθέτουμε τα MBRs στα αντίστοιχα κελιά
        self.assign_to_cells(data, dataset_label)

        print(f"Φορτώθηκε το dataset '{dataset_label}' από το αρχείο '{filename}' με {len(data)} ορθογωνία.")

    def assign_to_cells(self, data, dataset_label):
        """
        Αναθέτει κάθε MBR στα κελιά του grid που τέμνει.
        Εδώ γίνεται μια βελτιστοποίηση υπολογίζοντας μόνο
        τα απαραίτητα κελιά αντί να ελέγχουμε όλα τα m^2 κελιά.

        :param data: Λίστα με MBRs
        :param dataset_label: Ετικέτα dataset
        """
        if self.m == 0:
            return  # Αποφυγή διαίρεσης με το 0, αν m=0

        cell_size_x = (self.xU - self.xL) / self.m
        cell_size_y = (self.yU - self.yL) / self.m

        for mbr in data:
            # Υπολογίζουμε τους ελάχιστους και μέγιστους indices i, j που καλύπτει το MBR
            i_min = int((mbr.xmin - self.xL) // cell_size_x)
            i_max = int((mbr.xmax - self.xL) // cell_size_x)
            j_min = int((mbr.ymin - self.yL) // cell_size_y)
            j_max = int((mbr.ymax - self.yL) // cell_size_y)

            # "Σφίγγουμε" τα indices στα όρια του [0, m - 1]
            i_min = max(0, min(i_min, self.m - 1))
            i_max = max(0, min(i_max, self.m - 1))
            j_min = max(0, min(j_min, self.m - 1))
            j_max = max(0, min(j_max, self.m - 1))

            # Προσθέτουμε το MBR σε κάθε κελί που πιθανώς τέμνει
            for i in range(i_min, i_max + 1):
                for j in range(j_min, j_max + 1):
                    cell = self.cells[i][j]
                    # Προαιρετικός έλεγχος intersects αν θες να είσαι απόλυτα σίγουρος
                    if cell.mbr.intersects(mbr):
                        cell.add_object(mbr, dataset_label)

    def get_dataset(self, dataset_label):
        """
        Επιστρέφει το dataset με το συγκεκριμένο label (λίστα από MBRs).
        Αν δεν υπάρχει, επιστρέφει κενή λίστα.

        :param dataset_label: Ετικέτα dataset
        :return: Λίστα MBRs
        """
        return self.datasets.get(dataset_label, [])

    def find_cell(self, qx, qy):
        """
        Βρίσκει το κελί που περιέχει το σημείο (qx, qy), αν το πλέγμα το καλύπτει.
        Επιστρέφει το αντικείμενο Cell ή None αν το σημείο είναι εκτός ορίων.

        :param qx: Συντεταγμένη x
        :param qy: Συντεταγμένη y
        :return: Ένα αντικείμενο Cell ή None
        """
        if not self.cells:  # Αν δεν υπάρχουν κελιά
            return None

        # Έλεγχος αν (qx, qy) είναι εκτός των ορίων του grid
        if not (self.xL <= qx <= self.xU and self.yL <= qy <= self.yU):
            return None

        cell_size_x = (self.xU - self.xL) / self.m
        cell_size_y = (self.yU - self.yL) / self.m

        i = int((qx - self.xL) / cell_size_x)
        j = int((qy - self.yL) / cell_size_y)

        # Διόρθωση για τα δεξιά / άνω όρια
        if i == self.m:
            i -= 1
        if j == self.m:
            j -= 1

        return self.cells[i][j]

    def find_cells_at_hops(self, qx, qy, hop):
        """
        Βρίσκει όλα τα κελιά που βρίσκονται σε ακτίνα 'hop' (σε επίπεδο indices)
        από το κελί που περιέχει το σημείο (qx, qy). Επιστρέφει λίστα από Cell.

        Σημείωση: Η υλοποίηση θεωρεί ότι το hop ορίζει
        ένα τετράγωνο [i-hop, i+hop] x [j-hop, j+hop] γύρω από το αρχικό κελί.

        :param qx: Συντεταγμένη x
        :param qy: Συντεταγμένη y
        :param hop: Απόσταση σε “κελιά”/indices
        :return: Λίστα από Cell
        """
        initial_cell = self.find_cell(qx, qy)
        if not initial_cell:
            return []

        # Εύρεση (i, j) του αρχικού κελιού
        cell_i, cell_j = -1, -1
        for i in range(self.m):
            for j in range(self.m):
                if self.cells[i][j] == initial_cell:
                    cell_i, cell_j = i, j
                    break
            if cell_i != -1:
                break

        if cell_i == -1:
            return []  # Δεν βρέθηκε κελί

        neighbor_cells = []
        # Εξετάζουμε όλα τα κελιά (i', j') για i' ∈ [cell_i - hop, cell_i + hop]
        # και j' ∈ [cell_j - hop, cell_j + hop]
        for i in range(cell_i - hop, cell_i + hop + 1):
            for j in range(cell_j - hop, cell_j + hop + 1):
                if 0 <= i < self.m and 0 <= j < self.m:
                    # Εξαιρούμε το αρχικό κελί (προαιρετικό)
                    if i == cell_i and j == cell_j:
                        continue
                    neighbor_cells.append(self.cells[i][j])

        return neighbor_cells

    def get_object_by_id(self, obj_id):
        """
        Επιστρέφει το πρώτο MBR που βρίσκει με το συγκεκριμένο ID, σε οποιοδήποτε dataset.
        Διατρέχει όλα τα datasets που είναι φορτωμένα στο self.datasets.

        :param obj_id: Το string ID του αντικειμένου
        :return: Το αντίστοιχο MBR ή None αν δεν βρεθεί
        """
        for dataset in self.datasets.values():
            for obj in dataset:
                if obj.id == obj_id:
                    return obj
        return None
