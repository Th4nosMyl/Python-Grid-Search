import time
from grid import Grid
from MBR import MBR

class SpatialJoinPBSM:
    """
    Υλοποίηση του Spatial Join με χρήση του PBSM (Partition Based Spatial Merge).
    Βασίζεται σε διαμέριση του χώρου (grid) και έλεγχο τομής
    μόνο μεταξύ αντικειμένων που πέφτουν στο ίδιο κελί.
    """

    def __init__(self, grid):
        """
        :param grid: Αντικείμενο Grid, στο οποίο θα πρέπει ήδη να έχουν φορτωθεί
                     τα σύνολα 'A' και 'B' (π.χ. grid.load('A.csv', 'A')).
        """
        self.grid = grid
        self.results = set()  # Χρήση set για αποφυγή διπλοτύπων (π.χ. ίδιο ζεύγος)

    def execute_join(self):
        """
        Εκτέλεση του Spatial Join χρησιμοποιώντας τον PBSM αλγόριθμο:
          1. Ελέγχουμε αν υπάρχουν τα datasets 'A' και 'B' στο self.grid.
          2. Για κάθε κελί (cell) του grid:
             - Παίρνουμε όλα τα MBRs του A (π.χ. cell.objects['A']).
             - Παίρνουμε όλα τα MBRs του B (π.χ. cell.objects['B']).
             - Διπλός βρόχος ελέγχου τομής μεταξύ τους.
             - Αν τέμνονται, προσθέτουμε το ζεύγος στο self.results (set).
          3. Επιστρέφουμε (λίστα αποτελεσμάτων, stats_str) για να μπορούμε να εμφανίσουμε
             / αποθηκεύσουμε τα στατιστικά στον κώδικα που το καλεί.

        :return: (list_of_results, stats_str)
                 όπου:
                   list_of_results: λίστα από μοναδικά tuples (a, b) όπου a∈A, b∈B και a τέμνει b.
                   stats_str: κείμενο με στατιστικά (χρόνος, πόσα κελιά παραλείφθηκαν κ.λπ.).
        """

        # 0. Έλεγχος ύπαρξης datasets
        if 'A' not in self.grid.datasets or 'B' not in self.grid.datasets:
            msg = "[SpatialJoinPBSM] Τα σύνολα 'A' και 'B' πρέπει να φορτωθούν πριν εκτελέσεις τον Spatial Join."
            print(msg)
            return [], msg  # Επιστρέφουμε κενό και μήνυμα

        # 1. Έναρξη χρονομέτρησης
        start_time = time.time()

        # 2. Προετοιμασία counters για στατιστικά
        total_cells = self.grid.m * self.grid.m
        skipped_cells = 0
        processed_cells = 0
        pairs_checked = 0  # Πόσα ζεύγη (a, b) εξετάστηκαν;

        # (ή αν δε θέλεις pairs_checked, μπορείς να το παραλείψεις.)

        # 3. Επανάληψη σε κάθε κελί του grid
        for i in range(self.grid.m):
            for j in range(self.grid.m):
                cell = self.grid.cells[i][j]
                objects_A = cell.objects.get('A', [])
                objects_B = cell.objects.get('B', [])

                # Αν ένα από τα δύο σύνολα είναι άδειο, παραλείπουμε το κελί
                if not objects_A or not objects_B:
                    skipped_cells += 1
                    continue

                # Αλλιώς, το επεξεργαζόμαστε
                processed_cells += 1

                # Διπλός βρόχος ελέγχου τομής
                for a in objects_A:
                    for b in objects_B:
                        pairs_checked += 1
                        if a.intersects(b):
                            self.results.add((a, b))

        # 4. Υπολογισμός χρόνου
        end_time = time.time()
        elapsed = end_time - start_time

        # 5. Δημιουργία stats_str
        join_count = len(self.results)  # Πόσα ζεύγη βρέθηκαν
        stats_str = (
            "[SpatialJoinPBSM] Στατιστικά:\n"
            f" • Συνολικά κελιά στο grid: {total_cells}\n"
            f" • Παραλείφθηκαν (skipped) κελιά: {skipped_cells}\n"
            f" • Επεξεργαστήκαμε κελιά: {processed_cells}\n"
            f" • Συνολικά ζεύγη (A,B) εξετάστηκαν: {pairs_checked}\n"
            f" • Τελικά ζεύγη που τέμνονται: {join_count}\n"
            f" • Χρόνος εκτέλεσης: {elapsed:.4f} δευτερόλεπτα.\n"
        )

        # 6. (Προαιρετικά) εκτύπωση στο console
        print(stats_str)

        # 7. Επιστρέφουμε (results_list, stats_str)
        return list(self.results), stats_str
