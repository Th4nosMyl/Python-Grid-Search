# kNN.py

import heapq
from utils import Utils
import time
import itertools

class kNN:
    """
    Κλάση που υλοποιεί την αναζήτηση k-Nearest Neighbors (k-NN) σε ένα Grid.
    Η μέθοδος `knn` δέχεται ένα σημείο (qx, qy) και έναν αριθμό k,
    και επιστρέφει τους k κοντινότερους γείτονες.
    """

    @staticmethod
    def knn(grid, qx, qy, k):
        """
        Εκτελεί αναζήτηση k-κοντινότερων γειτόνων (k-NN) πάνω σε ένα Grid,
        ξεκινώντας από το κελί που καλύπτει το σημείο (qx, qy) και επεκτείνοντας
        την αναζήτηση σε γειτονικά κελιά (hops) έως ότου βρούμε αρκετά κοντινά αντικείμενα.

        :param grid: Αντικείμενο Grid, το οποίο περιέχει τα κελιά (cells)
                     και τα αποθηκευμένα MBRs (π.χ. objects['default']).
        :param qx: Η x-συντεταγμένη του σημείου ενδιαφέροντος (query point).
        :param qy: Η y-συντεταγμένη του σημείου ενδιαφέροντος (query point).
        :param k:  Ο αριθμός k γειτόνων που θέλουμε να επιστρέψουμε.
        :return: Δύο τιμές:
            1) results: Μια λίστα (απόσταση, MBR), ταξινομημένη κατά αύξουσα απόσταση.
            2) stats_str: Συμβολοσειρά που περιγράφει στατιστικά για την εκτέλεση, όπως:
               - πόσα αντικείμενα εξετάστηκαν
               - πόσα γειτονικά κελιά εξετάστηκαν
               - χρόνος εκτέλεσης, κ.λπ.
        """
        start_time = time.time()

        # Χρησιμοποιούμε max-heap (pq) με μορφή (αρνητική_απόσταση, counter, αντικείμενο).
        pq = []
        threshold = float('inf')
        initial_cell = grid.find_cell(qx, qy)

        # Μετρικές για στατιστικά
        processed_objects = 0          # Πόσα αντικείμενα εξετάστηκαν συνολικά
        processed_neighbor_cells = 0   # Πόσα γειτονικά κελιά ελέγχθηκαν

        # Αν το σημείο (qx, qy) βρίσκεται εκτός των ορίων του Grid, επιστρέφουμε κενά αποτελέσματα
        if not initial_cell:
            msg_out_of_grid = (
                f"[kNN] Το σημείο ({qx}, {qy}) είναι εκτός του πλέγματος.\n"
                f"    Όρια Grid: xmin={grid.xL}, ymin={grid.yL}, xmax={grid.xU}, ymax={grid.yU}"
            )
            print(msg_out_of_grid)
            stats_str = (
                "[kNN] ΔΕΝ έγινε αναζήτηση, γιατί το σημείο είναι εκτός grid.\n"
                + msg_out_of_grid
            )
            return [], stats_str

        print(f"[kNN] Αναζήτηση στο κελί: {initial_cell.mbr}, "
              f"{len(initial_cell.objects.get('default', []))} αντικείμενα.")

        processed_ids = set()       # Χρησιμοποιείται για να αποφύγουμε διπλό processing
        counter = itertools.count() # Χρησιμοποιείται για tie-breaking στο heap

        # 1. Έλεγχος αντικειμένων στο αρχικό κελί
        for obj in initial_cell.objects.get('default', []):
            if obj.id in processed_ids:
                continue
            processed_ids.add(obj.id)
            processed_objects += 1

            dist_sq = Utils.squared_distance(qx, qy, obj.xmin, obj.ymin)

            if len(pq) < k:
                heapq.heappush(pq, (-dist_sq, next(counter), obj))
            elif dist_sq < -pq[0][0]:
                heapq.heappushpop(pq, (-dist_sq, next(counter), obj))
                threshold = -pq[0][0]

        # 2. Επέκταση σε γειτονικά κελιά κατά hop
        hop = 1
        MAX_HOPS = 5
        while hop <= MAX_HOPS:
            continue_search = False
            neighbor_cells = grid.find_cells_at_hops(qx, qy, hop)
            processed_neighbor_cells += len(neighbor_cells)

            for cell in neighbor_cells:
                # Ελέγχουμε αν η ελάχιστη (τετραγωνική) απόσταση από το cell στο (qx, qy)
                # είναι μικρότερη από το threshold. Αν όχι, δεν χρειάζεται να το εξετάσουμε.
                if Utils.mindist_squared(qx, qy, cell.mbr) < threshold:
                    continue_search = True
                    for obj in cell.objects.get('default', []):
                        if obj.id in processed_ids:
                            continue
                        processed_ids.add(obj.id)
                        processed_objects += 1

                        dist_sq = Utils.squared_distance(qx, qy, obj.xmin, obj.ymin)
                        if len(pq) < k:
                            heapq.heappush(pq, (-dist_sq, next(counter), obj))
                        elif dist_sq < -pq[0][0]:
                            heapq.heappushpop(pq, (-dist_sq, next(counter), obj))
                            threshold = -pq[0][0]

            # Αν δεν βρήκαμε κάτι καινούργιο που να μειώνει το threshold, σταματάμε.
            if not continue_search:
                break
            hop += 1

        # Υπολογισμός χρόνου εκτέλεσης
        elapsed_time = time.time() - start_time
        print(f"[kNN] Grid-based k-NN ολοκληρώθηκε σε {elapsed_time:.4f} δευτερόλεπτα.")

        # Μετατροπή των στοιχείων (αρνητική_απόσταση, counter, obj) σε (απόσταση, obj)
        results = sorted(
            [(-dist_sq, obj) for dist_sq, _, obj in pq],
            key=lambda x: x[0]
        )
        print(f"[kNN] Βρέθηκαν {len(results)} κοντινότεροι γείτονες (επιστρέφουμε τους k={k}).")

        # Δημιουργούμε τη συμβολοσειρά stats_str για να αναφέρουμε τα στατιστικά
        stats_str = (
            "[kNN] Στατιστικά:\n"
            f" • Συνολικά αντικείμενα εξετάστηκαν: {processed_objects}\n"
            f" • Γειτονικά κελιά εξετάστηκαν: {processed_neighbor_cells}\n"
            f" • Τελικός αριθμός γειτόνων (<=k): {len(results)}\n"
            f" • Χρόνος εκτέλεσης: {elapsed_time:.4f} δευτερόλεπτα.\n"
        )

        return results, stats_str
