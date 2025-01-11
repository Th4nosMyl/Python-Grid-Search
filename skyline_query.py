import time
from utils import Utils

class SkylineQuery:
    """
    Υλοποιεί ένα ερώτημα Skyline πάνω σε ένα ήδη κατασκευασμένο Grid.
    Επιχειρεί να παραλείψει (skip) ολόκληρα κελιά που κυριαρχούνται
    από ήδη γνωστά skyline points, ώστε να επιταχύνει την εκτέλεση.

    Μπορεί να χειριστεί 2D (π.χ. xmin, ymin) ή περισσότερες διαστάσεις,
    αρκεί να τροποποίησεις τη συνάρτηση get_coords ώστε να επιστρέφει
    τις τιμές των διαστάσεων (attrs) κάθε αντικειμένου.
    """

    def __init__(self, grid, dims=2):
        """
        :param grid: Ένα αντικείμενο Grid, ήδη φορτωμένο με δεδομένα (π.χ. objects['default']).
        :param dims: Ο αριθμός διαστάσεων που θες να χειριστείς (default = 2).
                     - Αν dims=2, χρησιμοποιούμε xmin, ymin όπως πριν.
                     - Αν dims>2, πρέπει να επεκτείνεις τον τρόπο που ανακτάς συντεταγμένες.
        """
        self.grid = grid
        self.dims = dims

    def get_coords(self, obj):
        """
        Επιστρέφει τις συντεταγμένες (attrs) του αντικειμένου obj ως λίστα ή tuple.
        - Σε καθαρά 2D περιβάλλον, είναι (xmin, ymin).
        - Για πολυδιάστατα δεδομένα (>=3D), προσαρμόζεις ώστε να επιστρέφει π.χ. [x, y, cost, weight...].
        """
        if self.dims == 2:
            return (obj.xmin, obj.ymin)
        else:
            # Π.χ. αν το obj έχει obj.attrs = [x, y, cost...].
            return obj.attrs

    def dominates_point(self, p, q):
        """
        Ελέγχει αν το αντικείμενο p κυριαρχεί το q σε όλες τις διαστάσεις:
          - σε όλες τις διαστάσεις: p[i] <= q[i]
          - και τουλάχιστον σε μία διάσταση p[i] < q[i]

        Για 2D, αυτό αντιστοιχεί στο:
            p.xmin <= q.xmin AND p.ymin <= q.ymin
            AND (p.xmin < q.xmin OR p.ymin < q.ymin)
        """
        p_coords = self.get_coords(p)
        q_coords = self.get_coords(q)

        all_less_equal = True
        strictly_less_in_one = False

        for i in range(len(p_coords)):
            if p_coords[i] > q_coords[i]:
                # Σε κάποια διάσταση η p είναι μεγαλύτερη -> δεν κυριαρχεί
                all_less_equal = False
                break
            if p_coords[i] < q_coords[i]:
                # Σε κάποια διάσταση βρήκαμε αυστηρά μικρότερο
                strictly_less_in_one = True

        return all_less_equal and strictly_less_in_one

    def dominates_cell(self, sky_points, cell):
        """
        Ελέγχει αν ένα κελί ολόκληρο κυριαρχείται από κάποιο ήδη γνωστό skyline point.
        Για 2D, παίρνουμε (cell.mbr.xmin, cell.mbr.ymin) ως "κατώτατο άκρο".
        Αν p κυριαρχεί αυτό το άκρο, τότε όλο το κελί κυριαρχείται.
        """
        if self.dims == 2:
            cell_coords = (cell.mbr.xmin, cell.mbr.ymin)
        else:
            # Πολυδιάστατη περίπτωση (ενδεικτικά):
            cell_coords = (cell.mbr.xmin, cell.mbr.ymin)

        for p in sky_points:
            p_coords = self.get_coords(p)

            all_less_equal = True
            strictly_less_in_one = False

            # Θεωρούμε len(cell_coords) = 2 εδώ.
            for i in range(len(cell_coords)):
                if p_coords[i] > cell_coords[i]:
                    all_less_equal = False
                    break
                if p_coords[i] < cell_coords[i]:
                    strictly_less_in_one = True

            if all_less_equal and strictly_less_in_one:
                return True

        return False

    def sky_query(self):
        """
        Εκτελεί το Skyline Query στο grid και επιστρέφει:
            - Τη λίστα skyline_points
            - Μια συμβολοσειρά stats_str με στατιστικά:
                * Συνολικά ενεργά κελιά
                * Παραλειφθέντα (skipped) κελιά
                * Επεξεργασμένα κελιά
                * Πόσα αντικείμενα εξετάστηκαν
                * Συνολικό χρόνο εκτέλεσης

        :return: (skyline_points, stats_str)
        """
        start_time = time.perf_counter()

        # 1. Εντοπίζουμε τα "ενεργά" κελιά (που έχουν τουλάχιστον ένα αντικείμενο "default")
        active_cells = [
            cell for row in self.grid.cells for cell in row
            if cell.objects.get('default', [])
        ]

        # 2. Ταξινομούμε τα κελιά (π.χ. με κριτήριο (xmin asc, ymin asc))
        sorted_cells = sorted(
            active_cells,
            key=lambda c: (c.mbr.xmin, c.mbr.ymin)
        )

        skyline_points = []
        skipped_cells = 0
        processed_cells = 0
        processed_points = 0

        # 3. Ελέγχουμε κάθε κελί
        for cell in sorted_cells:
            # Αν κυριαρχείται ολόκληρο, το skip-άρουμε
            if self.dominates_cell(skyline_points, cell):
                skipped_cells += 1
                continue

            processed_cells += 1
            points_in_cell = cell.objects.get('default', [])

            for point in points_in_cell:
                processed_points += 1
                dominated = False
                for sp in skyline_points:
                    if self.dominates_point(sp, point):
                        dominated = True
                        break

                if not dominated:
                    # Αφαιρούμε όσα Skyline points κυριαρχούνται πλέον από το point
                    skyline_points = [
                        sp for sp in skyline_points
                        if not self.dominates_point(point, sp)
                    ]
                    skyline_points.append(point)

        elapsed_time = time.perf_counter() - start_time

        # 4. Στατιστικά
        total_active_cells = len(active_cells)
        stats_str = (
            "[SkylineQuery] Στατιστικά:\n"
            f" • Συνολικά ενεργά κελιά: {total_active_cells}\n"
            f" • Παραλείφθηκαν (skipped) κελιά: {skipped_cells}\n"
            f" • Επεξεργαστήκαμε κελιά: {processed_cells}\n"
            f" • Συνολικά αντικείμενα εξετάστηκαν: {processed_points}\n"
            f" • Χρόνος εκτέλεσης: {elapsed_time:.6f} δευτερόλεπτα."
        )

        # Μπορούμε να τυπώσουμε και στο κονσόλ/terminal (προαιρετικά)
        print(stats_str)

        return skyline_points, stats_str
