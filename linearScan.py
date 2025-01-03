# linearScan.py

from MBR import MBR
from utils import Utils
import time

class LinearScan:
    def __init__(self, filename):
        self.filename = filename
        self.data = self.load_data()

    def load_data(self):
        """Φορτώνει τα δεδομένα από το αρχείο CSV."""
        data = []
        try:
            with open(self.filename, 'r') as file:
                header = next(file)  # Παράκαμψη επικεφαλίδων
                for line in file:
                    parts = line.strip().split(',')
                    if len(parts) != 5:
                        continue  # Παράλειψη μη έγκυρων γραμμών
                    id, xmin, ymin, xmax, ymax = parts
                    mbr = MBR(id, float(xmin), float(ymin), float(xmax), float(ymax))
                    data.append(mbr)
        except FileNotFoundError:
            print(f"Το αρχείο '{self.filename}' δεν βρέθηκε.")
        except Exception as e:
            print(f"Σφάλμα κατά τη φόρτωση του αρχείου '{self.filename}': {e}")
        return data

    def knn(self, qx, qy, k):
        """Εύρεση k κοντινότερων γειτόνων μέσω Linear Scan."""
        start_time = time.time()  # Έναρξη χρονομέτρησης
        results = []
        for obj in self.data:
            dist = obj.distance_to_point(qx, qy)
            results.append((dist, obj))
        # Ταξινόμηση με βάση την απόσταση
        results.sort(key=lambda x: x[0])
        elapsed_time = time.time() - start_time  # Υπολογισμός χρόνου εκτέλεσης
        print(f"Linear Scan k-NN ολοκληρώθηκε σε {elapsed_time:.4f} δευτερόλεπτα.")
        return results[:k]
