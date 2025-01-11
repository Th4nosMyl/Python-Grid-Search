import heapq
from utils import Utils
import time
import itertools

class kNN:
    """
    Κλάση που υλοποιεί τη διαδικασία k-Nearest Neighbors (k-NN) πάνω σε ένα Grid.
    """

    @staticmethod
    def knn(grid, qx, qy, k):
        """
        Εκτελεί αναζήτηση k κοντινότερων γειτόνων (k-NN) πάνω σε ένα Grid.
        
        Επιστρέφει:
          - Τη λίστα results (λίστα από tuples (distance, MBR))
          - Μία συμβολοσειρά stats_str με στατιστικά (π.χ. πόσα αντικείμενα εξετάστηκαν, πόσα κελιά, χρόνος κ.λπ.)
        """
        start_time = time.time()  # Έναρξη χρονομέτρησης

        # Χρησιμοποιούμε max-heap με μορφή (αρνητική_απόσταση, counter, αντικείμενο)
        pq = []
        threshold = float('inf')
        initial_cell = grid.find_cell(qx, qy)

        # Counters για στατιστικά
        processed_objects = 0     # Συνολικά αντικείμενα που είδαμε
        processed_neighbor_cells = 0  # Πόσα neighbor cells εξετάστηκαν (σε όλα τα hops)

        # Έλεγχος αν το σημείο είναι εντός πλέγματος
        if not initial_cell:
            msg_out_of_grid = (
                f"[kNN] Το σημείο ({qx}, {qy}) είναι εκτός του πλέγματος.\n"
                f"    Όρια Grid: xmin={grid.xL}, ymin={grid.yL}, xmax={grid.xU}, ymax={grid.yU}"
            )
            print(msg_out_of_grid)
            # Επιστρέφουμε κενά αποτελέσματα κι ένα stats_str που εξηγεί την κατάσταση
            stats_str = f"[kNN] ΔΕΝ έγινε αναζήτηση, γιατί το σημείο είναι εκτός grid.\n{msg_out_of_grid}"
            return [], stats_str

        print(f"[kNN] Αναζήτηση στο κελί: {initial_cell.mbr}, "
              f"{len(initial_cell.objects.get('default', []))} αντικείμενα.")

        processed_ids = set()  # Για την παρακολούθηση των επεξεργασμένων IDs
        counter = itertools.count()  # Γεννήτρια για tie-breaking στο heap

        # 1. Έλεγχος αντικειμένων στο αρχικό κελί
        for obj in initial_cell.objects.get('default', []):
            if obj.id in processed_ids:
                continue
            processed_ids.add(obj.id)
            processed_objects += 1

            # Υπολογίζουμε την ΤΕΤΡΑΓΩΝΙΚΗ απόσταση (ή ό,τι λογική θέλεις)
            dist_sq = Utils.squared_distance(qx, qy, obj.xmin, obj.ymin)

            if len(pq) < k:
                heapq.heappush(pq, (-dist_sq, next(counter), obj))
            elif dist_sq < -pq[0][0]:
                heapq.heappushpop(pq, (-dist_sq, next(counter), obj))
                threshold = -pq[0][0]

        # 2. Επέκταση σε γειτονικά κελιά κατά hop
        hop = 1
        MAX_HOPS = 5  # Παράδειγμα· μπορείς να το αυξήσεις/μειώσεις.
        while hop <= MAX_HOPS:
            continue_search = False
            neighbor_cells = grid.find_cells_at_hops(qx, qy, hop)

            # Μετράμε πόσα cells εξετάζουμε σε αυτό το hop
            processed_neighbor_cells += len(neighbor_cells)

            for cell in neighbor_cells:
                # mindist_squared() υπολογίζει την ΤΕΤΡΑΓΩΝΙΚΗ ελάχιστη απόσταση
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

            if not continue_search:
                # Αν κανένα κελί δεν μπόρεσε να προσθέσει νέο αντικείμενο ή μειώσει το threshold, σταματάμε
                break
            hop += 1

        # Υπολογισμός χρόνου εκτέλεσης
        elapsed_time = time.time() - start_time
        print(f"[kNN] Grid-based k-NN ολοκληρώθηκε σε {elapsed_time:.4f} δευτερόλεπτα.")

        # Μετατρέπουμε τα αποτελέσματα από (αρνητική_απόσταση, counter, obj) σε (απόσταση, obj)
        results = sorted(
            [(-dist_sq, obj) for dist_sq, _, obj in pq],
            key=lambda x: x[0]
        )
        print(f"[kNN] Βρέθηκαν {len(results)} κοντινότεροι γείτονες (επιστρέφουμε τους k={k}).")

        # Δημιουργούμε το stats_str
        stats_str = (
            "[kNN] Στατιστικά:\n"
            f" • Συνολικά αντικείμενα εξετάστηκαν: {processed_objects}\n"
            f" • Γειτονικά κελιά εξετάστηκαν: {processed_neighbor_cells}\n"
            f" • Τελικός αριθμός γειτόνων (<=k): {len(results)}\n"
            f" • Χρόνος εκτέλεσης: {elapsed_time:.4f} δευτερόλεπτα.\n"
        )

        return results, stats_str
