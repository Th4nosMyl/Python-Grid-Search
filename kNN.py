# kNN.py

import heapq
from utils import Utils
import time
import itertools  # Προσθήκη itertools για τον μετρητή

class kNN:
    @staticmethod
    def knn(grid, qx, qy, k):
        """Εύρεση k κοντινότερων γειτόνων μέσω Grid-based k-NN."""
        start_time = time.time()  # Έναρξη χρονομέτρησης

        pq = []
        threshold = float('inf')
        initial_cell = grid.find_cell(qx, qy)

        # Έλεγχος αν το σημείο είναι εντός πλέγματος
        if not initial_cell:
            print(f"Το σημείο ({qx}, {qy}) είναι εκτός του πλέγματος.")
            print(f"Όρια Grid: xmin={grid.xL}, ymin={grid.yL}, xmax={grid.xU}, ymax={grid.yU}")
            return []

        print(f"Αναζήτηση στο κελί: {initial_cell.mbr}, {len(initial_cell.objects_default)} αντικείμενα.")

        processed_ids = set()  # Σύνολο για την παρακολούθηση των επεξεργασμένων αντικειμένων
        counter = itertools.count()  # Δημιουργία μετρητή

        # Εύρεση k-NN στο αρχικό κελί
        for obj in initial_cell.objects_default:
            if obj.id in processed_ids:
                continue  # Παράβλεψη αν το αντικείμενο έχει ήδη επεξεργαστεί
            processed_ids.add(obj.id)
            dist_sq = Utils.squared_distance(qx, qy, obj.xmin, obj.ymin)
            if len(pq) < k:
                heapq.heappush(pq, (-dist_sq, next(counter), obj))
            elif dist_sq < -pq[0][0]:
                heapq.heappushpop(pq, (-dist_sq, next(counter), obj))
                threshold = -pq[0][0]

        hop = 1
        MAX_HOPS = 5  # Μείωση του MAX_HOPS για καλύτερη απόδοση
        while hop <= MAX_HOPS:
            continue_search = False
            neighbor_cells = grid.find_cells_at_hops(qx, qy, hop)

            # Αφαίρεση των print statements για βελτίωση της απόδοσης
            # print(f"Hop {hop}: Εξέταση {len(neighbor_cells)} γειτονικών κελιών.")
            for cell in neighbor_cells:
                if Utils.mindist_squared(qx, qy, cell.mbr) < threshold:
                    continue_search = True
                    # print(f"Γειτονικό κελί: {cell.mbr}, {len(cell.objects_default)} αντικείμενα.")
                    for obj in cell.objects_default:
                        if obj.id in processed_ids:
                            continue  # Παράβλεψη αν το αντικείμενο έχει ήδη επεξεργαστεί
                        processed_ids.add(obj.id)
                        dist_sq = Utils.squared_distance(qx, qy, obj.xmin, obj.ymin)
                        if len(pq) < k:
                            heapq.heappush(pq, (-dist_sq, next(counter), obj))
                        elif dist_sq < -pq[0][0]:
                            heapq.heappushpop(pq, (-dist_sq, next(counter), obj))
                            threshold = -pq[0][0]

            if not continue_search:
                break
            hop += 1

        elapsed_time = time.time() - start_time  # Υπολογισμός χρόνου εκτέλεσης
        print(f"Grid-based k-NN ολοκληρώθηκε σε {elapsed_time:.4f} δευτερόλεπτα.")

        # Επιστροφή ταξινομημένων γειτόνων με απόσταση
        results = sorted([(-dist_sq, obj) for dist_sq, _, obj in pq], key=lambda x: x[0])
        print(f"Βρέθηκαν {len(results)} κοντινότεροι γείτονες.")
        return results
