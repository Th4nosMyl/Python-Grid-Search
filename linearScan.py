# linearScan.py

import time
from MBR import MBR
from utils import Utils

class LinearScan:
    """
    Κλάση που υλοποιεί την αναζήτηση k-Nearest Neighbors (k-NN)
    μέσω γραμμικής σάρωσης ενός αρχείου CSV (ID, xmin, ymin, xmax, ymax).
    """

    def __init__(self, filename):
        """
        Αρχικοποιεί τη δομή LinearScan, φορτώνοντας τα δεδομένα MBR
        από το δοθέν αρχείο CSV.

        :param filename: Το όνομα του CSV αρχείου που περιέχει τα δεδομένα.
        """
        self.filename = filename
        self.data = self.load_data()

    def load_data(self):
        """
        Φορτώνει τα δεδομένα (MBRs) από ένα CSV αρχείο με μορφή γραμμών:
          ID,xmin,ymin,xmax,ymax

        - Παραλείπει γραμμές που δεν περιέχουν ακριβώς 5 πεδία.
        - Αγνοεί γραμμές όπου xmin>xmax ή ymin>ymax, ή εφόσον δεν
          μπορούν να μετατραπούν σε float.

        :return: Μια λίστα από MBR αντικείμενα.
        """
        data = []
        try:
            with open(self.filename, 'r') as file:
                header = next(file, None)  # Παράκαμψη γραμμής επικεφαλίδων, αν υπάρχει
                for line in file:
                    parts = line.strip().split(',')
                    if len(parts) != 5:
                        continue

                    id_str, xmin_str, ymin_str, xmax_str, ymax_str = parts
                    try:
                        xmin = float(xmin_str)
                        ymin = float(ymin_str)
                        xmax = float(xmax_str)
                        ymax = float(ymax_str)

                        # Αν τα όρια είναι ασύμβατα, αγνοούμε αυτή τη γραμμή
                        if xmin > xmax or ymin > ymax:
                            continue

                        mbr = MBR(id_str, xmin, ymin, xmax, ymax)
                        data.append(mbr)
                    except ValueError:
                        continue
        except FileNotFoundError:
            print(f"[LinearScan] Το αρχείο '{self.filename}' δεν βρέθηκε.")
        except Exception as e:
            print(f"[LinearScan] Σφάλμα κατά τη φόρτωση του αρχείου '{self.filename}': {e}")

        return data

    def knn(self, qx, qy, k):
        """
        Εκτελεί k-NN αναζήτηση με γραμμική σάρωση:
          1. Υπολογίζει την απόσταση κάθε αντικειμένου (MBR) από το (qx, qy).
          2. Ταξινομεί τα αποτελέσματα κατά αύξουσα απόσταση.
          3. Επιστρέφει τα k πρώτα στοιχεία.

        :param qx: Συντεταγμένη x του query point.
        :param qy: Συντεταγμένη y του query point.
        :param k:  Αριθμός κοντινότερων γειτόνων που θέλουμε.
        :return: Μια πλειάδα (results[:k], stats_str):
            - results[:k]: Λίστα (απόσταση, MBR) για τους k πιο κοντινούς.
            - stats_str: Κείμενο με στατιστικά εκτέλεσης (π.χ. χρόνος, πόσες εγγραφές).
        """
        start_time = time.time()

        # Υπολογισμός αποστάσεων (π.χ. πραγματική Ευκλείδεια)
        results = []
        for obj in self.data:
            dist = obj.distance_to_point(qx, qy)  # μέθοδος του MBR
            results.append((dist, obj))

        # Ταξινόμηση των αποτελεσμάτων
        results.sort(key=lambda x: x[0])

        elapsed_time = time.time() - start_time
        total_records = len(self.data)

        # Διαμόρφωση στατιστικών
        stats_str = (
            "[LinearScan] k-NN Στατιστικά:\n"
            f" • Επεξεργαστήκαμε {total_records} εγγραφές με γραμμική σάρωση.\n"
            f" • Χρόνος εκτέλεσης: {elapsed_time:.4f} δευτερόλεπτα.\n"
            f" • Τελικός αριθμός γειτόνων (<=k): {min(k, total_records)}\n"
        )

        print(stats_str)
        return results[:k], stats_str
