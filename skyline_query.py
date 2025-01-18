# skyline_query.py

import time
from utils import Utils

class SkylineQuery:
    """
    Η κλάση SkylineQuery υλοποιεί ένα ερώτημα Skyline (Pareto) πάνω σε ένα Grid.
    Η βασική ιδέα είναι να εντοπίσουμε εκείνα τα αντικείμενα MBR που δεν κυριαρχούνται
    (dominated) από κανένα άλλο.

    * Κυριαρχία (dominance) σε 2D (xmin, ymin):
      p κυριαρχεί q αν p.xmin <= q.xmin, p.ymin <= q.ymin και
      (p.xmin < q.xmin ή p.ymin < q.ymin).

    * Η υλοποίηση εκμεταλλεύεται τη διάταξη των αντικειμένων στο Grid:
      - Παρακάμπτουμε (skip) ολόκληρα κελιά αν γνωρίζουμε ότι κυριαρχούνται ήδη
        από κάποιο Skyline σημείο.
      - Αυτό μειώνει τις περιττές συγκρίσεις και επιταχύνει τη διαδικασία.

    * Μπορεί να επεκταθεί σε πολυδιάστατα δεδομένα, αρκεί να προσαρμόσουμε
      τη συνάρτηση get_coords() και τον έλεγχο dominates_cell() / dominates_point()
      ώστε να λαμβάνει υπόψη περισσότερες από 2 διαστάσεις.
    """

    def __init__(self, grid, dims=2):
        """
        Αρχικοποιεί το SkylineQuery με ένα ήδη φορτωμένο Grid (που περιέχει τα MBRs) και
        καθορίζει τον αριθμό διαστάσεων που θέλουμε να χειριστούμε.

        :param grid: Ένα αντικείμενο Grid, του οποίου τα κελιά (Cell) έχουν ήδη MBRs
                     στο objects['default'] (ή άλλα labels).
        :param dims: Πλήθος διαστάσεων. Αν dims=2, χειριζόμαστε (xmin, ymin) ως 2D.
                     Αν dims>2, υποθέτουμε ότι τα αντικείμενα έχουν obj.attrs
                     και η κυριαρχία ελέγχεται σε όλες τις συνιστώσες του attrs.
        """
        self.grid = grid
        self.dims = dims

    def get_coords(self, obj):
        """
        Επιστρέφει τις συντεταγμένες του αντικειμένου (obj) ως tuple ή λίστα,
        ανάλογα με τον αριθμό των διαστάσεων (dims).

        * Εάν dims=2, απλώς επιστρέφουμε (obj.xmin, obj.ymin).
        * Εάν dims>2, μπορούμε να διαβάσουμε π.χ. obj.attrs (μια λίστα τιμών)
          που αντιστοιχούν στις έξτρα διαστάσεις.

        :param obj: Το αντικείμενο (MBR ή άλλο) του οποίου τα δεδομένα διαστάσεων θέλουμε.
        :return: Συνήθως (xmin, ymin) σε 2D, ή μια λίστα αν υπάρχουν περισσότερες διαστάσεις.
        """
        if self.dims == 2:
            return (obj.xmin, obj.ymin)
        else:
            # Παράδειγμα πολυδιάστατου: θεωρούμε ότι obj.attrs διατίθεται
            return obj.attrs

    def dominates_point(self, p, q):
        """
        Ελέγχει εάν το αντικείμενο p κυριαρχεί το αντικείμενο q (dominates),
        σε όλες τις διαστάσεις.

        * Για 2D, το p κυριαρχεί q αν:
            p.xmin <= q.xmin AND p.ymin <= q.ymin
            με τουλάχιστον μία αυστηρή ανισότητα (<).

        * Στα βήματα:
          1. Παίρνουμε τις συντεταγμένες p_coords = self.get_coords(p).
          2. Παίρνουμε τις συντεταγμένες q_coords = self.get_coords(q).
          3. Ελέγχουμε αν p_coords[i] <= q_coords[i] για όλες τις διαστάσεις i,
             και αν τουλάχιστον σε μία διάσταση είναι (<).

        :param p: Ένα αντικείμενο (συνήθως MBR) που ελέγχουμε αν κυριαρχεί.
        :param q: Το αντικείμενο που θεωρούμε ότι μπορεί να κυριαρχείται.
        :return: True αν p κυριαρχεί q, αλλιώς False.
        """
        p_coords = self.get_coords(p)
        q_coords = self.get_coords(q)

        all_less_equal = True
        strictly_less_in_one = False

        for i in range(len(p_coords)):
            if p_coords[i] > q_coords[i]:
                all_less_equal = False
                break
            if p_coords[i] < q_coords[i]:
                strictly_less_in_one = True

        return all_less_equal and strictly_less_in_one

    def dominates_cell(self, sky_points, cell):
        """
        Ελέγχει αν ένα ολόκληρο κελί (cell) κυριαρχείται από κάποιο ήδη γνωστό Skyline point.
        - Για 2D, παίρνουμε το "κατώτατο άκρο" (cell.mbr.xmin, cell.mbr.ymin).
        - Αν κάποιος p στο sky_points κυριαρχεί αυτό το (xmin, ymin), τότε
          ολόκληρο το κελί κυριαρχείται.

        :param sky_points: Η λίστα των ήδη γνωστών Skyline points.
        :param cell: Ένα κελί (Cell) του Grid με mbr.xmin, mbr.ymin κ.ο.κ.
        :return: True αν το κελί κυριαρχείται πλήρως, αλλιώς False.
        """
        if self.dims == 2:
            cell_coords = (cell.mbr.xmin, cell.mbr.ymin)
        else:
            # Για nD περίπτωση, θα θέλαμε π.χ. cell.mbr.attrs κ.λπ.
            cell_coords = (cell.mbr.xmin, cell.mbr.ymin)

        for p in sky_points:
            p_coords = self.get_coords(p)

            all_less_equal = True
            strictly_less_in_one = False

            # Συνεχίζουμε να θεωρούμε len(cell_coords)=2 για απλοποίηση
            for i in range(len(cell_coords)):
                if p_coords[i] > cell_coords[i]:
                    all_less_equal = False
                    break
                if p_coords[i] < cell_coords[i]:
                    strictly_less_in_one = True

            if all_less_equal and strictly_less_in_one:
                # Μία φορά αρκεί για να συμπεράνουμε ότι το κελί κυριαρχείται
                return True

        return False

    def sky_query(self):
        """
        Εκτελεί το Skyline Query πάνω στο Grid, ακολουθώντας τα εξής βήματα:

        1. Εντοπίζουμε όλα τα "ενεργά" κελιά, δηλ. όσα περιέχουν αντικείμενα (objects['default']).
        2. Ταξινομούμε αυτά τα κελιά με κριτήριο (mbr.xmin, mbr.ymin) ώστε
           να εξετάζουμε πρώτα τα "κάτω-αριστερά" (τα οποία έχουν υψηλές πιθανότητες
           να κυριαρχήσουν επόμενα κελιά).
        3. Διατρέχουμε τη λίστα κελιών:
           - Αν το κελί κυριαρχείται πλήρως από κάποιο Skyline point (dominates_cell),
             το παραλείπουμε.
           - Διαφορετικά, εξετάζουμε τα αντικείμενα (MBRs) στο κελί:
             * Ελέγχουμε αν κάποιο ήδη γνωστό Skyline point κυριαρχεί το συγκεκριμένο αντικείμενο.
               Αν ναι, το αγνοούμε.
             * Αν όχι, αφαιρούμε από τη λίστα Skyline points όσα κυριαρχούνται
               από το νέο αντικείμενο και προσθέτουμε το νέο αντικείμενο στη λίστα.
        4. Επιστρέφουμε την τελική λίστα Skyline points μαζί με μια συμβολοσειρά (stats_str)
           που περιγράφει διάφορα στατιστικά (π.χ. πόσα κελιά εξετάστηκαν / παραλείφθηκαν,
           χρόνος εκτέλεσης κ.λπ.).

        :return: (skyline_points, stats_str)
          - skyline_points: Λίστα αντικειμένων (συνήθως MBRs) που βρέθηκαν να μην κυριαρχούνται.
          - stats_str: Συμβολοσειρά με στατιστικά εκτέλεσης (π.χ. #κελιών, #αντικειμένων, χρόνος).
        """
        start_time = time.perf_counter()

        # 1. Εντοπίζουμε τα ενεργά κελιά (όσα έχουν objects['default'] != [])
        active_cells = [
            cell for row in self.grid.cells for cell in row
            if cell.objects.get('default', [])
        ]

        # 2. Ταξινομούμε με βάση (xmin, ymin)
        sorted_cells = sorted(active_cells, key=lambda c: (c.mbr.xmin, c.mbr.ymin))

        skyline_points = []
        skipped_cells = 0
        processed_cells = 0
        processed_points = 0

        # 3. Εξετάζουμε κάθε κελί
        for cell in sorted_cells:
            # Εάν το κελί κυριαρχείται πλήρως, το παραλείπουμε
            if self.dominates_cell(skyline_points, cell):
                skipped_cells += 1
                continue

            processed_cells += 1
            points_in_cell = cell.objects.get('default', [])

            for point in points_in_cell:
                processed_points += 1
                dominated = False

                # Ελέγχουμε αν κάποιο ήδη γνωστό Skyline point κυριαρχεί αυτό το point
                for sp in skyline_points:
                    if self.dominates_point(sp, point):
                        dominated = True
                        break

                if not dominated:
                    # Αφαιρούμε από τη λίστα των Skyline points όσα κυριαρχούνται
                    # από το point
                    skyline_points = [
                        sp for sp in skyline_points
                        if not self.dominates_point(point, sp)
                    ]
                    skyline_points.append(point)

        elapsed_time = time.perf_counter() - start_time

        # 4. Συγκεντρώνουμε τα στατιστικά
        total_active_cells = len(active_cells)
        stats_str = (
            "[SkylineQuery] Στατιστικά:\n"
            f" • Συνολικά ενεργά κελιά: {total_active_cells}\n"
            f" • Παραλείφθηκαν (skipped) κελιά: {skipped_cells}\n"
            f" • Επεξεργαστήκαμε κελιά: {processed_cells}\n"
            f" • Συνολικά αντικείμενα εξετάστηκαν: {processed_points}\n"
            f" • Χρόνος εκτέλεσης: {elapsed_time:.6f} δευτερόλεπτα."
        )

        print(stats_str)
        return skyline_points, stats_str
