# spatialJoinPBSM.py

import time
from grid import Grid
from MBR import MBR

class SpatialJoinPBSM:
    """
    Υλοποιεί τον Spatial Join με χρήση του αλγορίθμου PBSM (Partition-Based Spatial Merge).
    Η ιδέα βασίζεται στο ότι το Grid διαμερίζει το χώρο, και ελέγχουμε τομή μόνο
    μεταξύ αντικειμένων (MBRs) που πέφτουν στο ίδιο κελί. Έτσι περιορίζουμε
    τις συγκρίσεις σε μικρότερα, τοπικά σύνολα αντί να ελέγχουμε κάθε ζεύγος (a,b).
    """

    def __init__(self, grid):
        """
        Αρχικοποιεί τον αλγόριθμο PBSM, δεσμευμένο πάνω σε ένα Grid. 
        Το grid θα πρέπει να έχει ήδη φορτωμένα τα σύνολα 'A' και 'B'.

        :param grid: Ένα αντικείμενο Grid, το οποίο περιέχει κελιά (Cell) και MBRs.
                     Απαραίτητο είναι να υπάρχουν τα datasets 'A' και 'B'
                     στο grid.datasets (π.χ. μετά από grid.load(...)).
        """
        self.grid = grid
        self.results = set()  # Αποθηκεύουμε ζεύγη (a,b) σε set για να αποφύγουμε διπλοτύπους

    def execute_join(self):
        """
        Εκτελεί τον Spatial Join με τον αλγόριθμο PBSM, ακολουθώντας τα εξής βήματα:

        1. Ελέγχουμε αν υπάρχουν τα datasets 'A' και 'B' στο self.grid (αλλιώς δε μπορούμε να προχωρήσουμε).
        2. Διατρέχουμε κάθε κελί (Cell) του πλέγματος (grid):
           - Λαμβάνουμε τα αντικείμενα A (π.χ. cell.objects['A']) και τα αντικείμενα B (cell.objects['B']).
           - Αν ένα από τα δύο σύνολα είναι άδειο, παρακάμπτουμε το κελί (skipped cells).
           - Αλλιώς, με έναν διπλό βρόχο ελέγχουμε για κάθε (a, b) αν a.intersects(b). 
             Αν ναι, καταχωρίζουμε το ζεύγος (a, b) στη λίστα αποτελεσμάτων.
        3. Υπολογίζουμε τον χρόνο εκτέλεσης και δημιουργούμε μια συμβολοσειρά στατιστικών (stats_str)
           που περιλαμβάνει:
             - #συνολικών κελιών
             - #κελιών που παραλείφθηκαν
             - #κελιών που επεξεργάστηκαν
             - #ζευγών (A,B) που εξετάστηκαν
             - #ζευγών που βρέθηκαν να τέμνονται
             - χρόνο εκτέλεσης
        4. Επιστρέφουμε:
            - Μια λίστα από μοναδικά ζεύγη (a, b) (αφού έχουμε χρησιμοποιήσει set στο self.results)
            - Τη συμβολοσειρά stats_str με την αναφορά στατιστικών.

        :return: Ένα tuple (results_list, stats_str), όπου:
            results_list: λίστα ζευγών (a, b) που τέμνονται
            stats_str: κείμενο με τις μετρήσεις και το χρόνο εκτέλεσης
        """
        # 0. Έλεγχος για την ύπαρξη των datasets 'A', 'B'
        if 'A' not in self.grid.datasets or 'B' not in self.grid.datasets:
            msg = "[SpatialJoinPBSM] Τα σύνολα 'A' και 'B' πρέπει να φορτωθούν πριν εκτελεστεί ο Spatial Join."
            print(msg)
            return [], msg

        start_time = time.time()  # Έναρξη μέτρησης χρόνου

        # Προετοιμάζουμε μετρητές στατιστικών
        total_cells = self.grid.m * self.grid.m
        skipped_cells = 0
        processed_cells = 0
        pairs_checked = 0

        # Διατρέχουμε όλα τα κελιά στο grid
        for i in range(self.grid.m):
            for j in range(self.grid.m):
                cell = self.grid.cells[i][j]

                objects_A = cell.objects.get('A', [])
                objects_B = cell.objects.get('B', [])

                # Αν δεν υπάρχουν αντικείμενα A ή B στο κελί, το παραλείπουμε
                if not objects_A or not objects_B:
                    skipped_cells += 1
                    continue

                # Διαφορετικά, επεξεργαζόμαστε το κελί
                processed_cells += 1

                # Διπλός βρόχος για κάθε ζεύγος (a, b)
                for a in objects_A:
                    for b in objects_B:
                        pairs_checked += 1
                        if a.intersects(b):
                            self.results.add((a, b))

        # Υπολογισμός χρόνου εκτέλεσης
        elapsed = time.time() - start_time

        # Δημιουργία αναφοράς στατιστικών
        join_count = len(self.results)
        stats_str = (
            "[SpatialJoinPBSM] Στατιστικά:\n"
            f" • Συνολικά κελιά στο grid: {total_cells}\n"
            f" • Παραλείφθηκαν (skipped) κελιά: {skipped_cells}\n"
            f" • Επεξεργαστήκαμε κελιά: {processed_cells}\n"
            f" • Συνολικά ζεύγη (A,B) εξετάστηκαν: {pairs_checked}\n"
            f" • Τελικά ζεύγη που τέμνονται: {join_count}\n"
            f" • Χρόνος εκτέλεσης: {elapsed:.4f} δευτερόλεπτα.\n"
        )

        print(stats_str)
        return list(self.results), stats_str
