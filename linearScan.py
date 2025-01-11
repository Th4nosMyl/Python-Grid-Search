import time
from MBR import MBR
from utils import Utils

class LinearScan:
    """
    Κλάση που υλοποιεί την αναζήτηση k-Nearest Neighbors (k-NN)
    μέσω γραμμικής σάρωσης (linear scan) ενός αρχείου CSV.
    """

    def __init__(self, filename):
        """
        :param filename: Όνομα του CSV αρχείου που περιέχει τα δεδομένα (MBRs).
        """
        self.filename = filename
        self.data = self.load_data()

    def load_data(self):
        """
        Φορτώνει τα δεδομένα MBR από το CSV αρχείο.
        Αναμένουμε format: ID,xmin,ymin,xmax,ymax (5 στήλες).

        :return: Λίστα με MBR αντικείμενα.
        """
        data = []
        try:
            with open(self.filename, 'r') as file:
                header = next(file, None)  # Προσπερνάμε τη γραμμή επικεφαλίδων
                for line in file:
                    parts = line.strip().split(',')
                    if len(parts) != 5:
                        continue  # Παράλειψη μη έγκυρων γραμμών
                    id_str, xmin_str, ymin_str, xmax_str, ymax_str = parts
                    try:
                        xmin = float(xmin_str)
                        ymin = float(ymin_str)
                        xmax = float(xmax_str)
                        ymax = float(ymax_str)

                        # Προαιρετικός έλεγχος εγκυρότητας
                        if xmin > xmax or ymin > ymax:
                            continue
                        mbr = MBR(id_str, xmin, ymin, xmax, ymax)
                        data.append(mbr)
                    except ValueError:
                        # Αν κάποιο πεδίο δεν μπορεί να γίνει float, το προσπερνάμε.
                        continue
        except FileNotFoundError:
            print(f"[LinearScan] Το αρχείο '{self.filename}' δεν βρέθηκε.")
        except Exception as e:
            print(f"[LinearScan] Σφάλμα κατά τη φόρτωση του αρχείου '{self.filename}': {e}")
        return data

    def knn(self, qx, qy, k):
        """
        Εκτελεί k-NN αναζήτηση (k γειτονικών αντικειμένων) με γραμμική σάρωση.
        1. Υπολογίζει την απόσταση από το query point (qx, qy) σε κάθε MBR.
        2. Ταξινομεί τη λίστα με βάση την απόσταση.
        3. Επιστρέφει τα k πρώτα.

        :param qx: Συντεταγμένη x του query point.
        :param qy: Συντεταγμένη y του query point.
        :param k: Αριθμός κοντινότερων γειτόνων που θέλουμε.
        :return: (results_list, stats_str)
                 όπου:
                   results_list = λίστα από tuples (distance, MBR), ταξινομημένα αύξουσα
                   stats_str = κείμενο με στατιστικά (π.χ. χρόνος εκτέλεσης, πόσες εγγραφές κ.λπ.)
        """
        start_time = time.time()

        # Υπολογίζουμε την πραγματική Ευκλείδεια απόσταση (ή squared_distance)
        # Εδώ χρησιμοποιείται η MBR μέθοδος distance_to_point (ελάχιστη απόσταση MBR->σημείο).
        results = []
        for obj in self.data:
            dist = obj.distance_to_point(qx, qy)
            results.append((dist, obj))

        # Ταξινόμηση με βάση την απόσταση
        results.sort(key=lambda x: x[0])

        elapsed_time = time.time() - start_time

        # Στατιστικά
        total_records = len(self.data)
        stats_str = (
            "[LinearScan] k-NN Στατιστικά:\n"
            f" • Επεξεργαστήκαμε {total_records} εγγραφές με γραμμική σάρωση.\n"
            f" • Χρόνος εκτέλεσης: {elapsed_time:.4f} δευτερόλεπτα.\n"
            f" • Τελικός αριθμός γειτόνων (<=k): {min(k, total_records)}\n"
        )

        print(stats_str)

        # Επιστρέφουμε τα k πρώτα αντικείμενα + τα στατιστικά
        return results[:k], stats_str
