# naiveSpatialJoin.py

import time
from MBR import MBR

class NaiveSpatialJoin:
    """
    Υλοποιεί τον αφελή (brute-force) Spatial Join μεταξύ δύο συνόλων ορθογωνίων (A και B).
    Χρησιμοποιεί διπλό βρόχο: για κάθε 'a' στο A, ελέγχει για κάθε 'b' στο B
    αν τα δύο MBR τέμνονται. Αν ναι, προσθέτει το ζεύγος (a, b) στα αποτελέσματα.
    """

    def __init__(self, data_A, data_B):
        """
        Αρχικοποιεί τη δομή με δύο λίστες από MBRs, την A και τη B.

        :param data_A: Λίστα με MBR αντικείμενα του συνόλου A.
        :param data_B: Λίστα με MBR αντικείμενα του συνόλου B.
        """
        self.data_A = data_A
        self.data_B = data_B
        self.results = []

    def execute_join(self):
        """
        Εκτελεί το Naive Spatial Join με μέτρηση χρόνου εκτέλεσης και πλήθος ελέγχων:

        1. Διατρέχει κάθε MBR 'a' στη λίστα A.
        2. Για το καθένα, διατρέχει κάθε MBR 'b' στη λίστα B.
        3. Ελέγχει αν a.intersects(b). Αν ναι, προσθέτει (a, b) στα αποτελέσματα.
        4. Επιστρέφει την τελική λίστα αποτελεσμάτων μαζί με μια συμβολοσειρά στατιστικών.

        :return: Ένα tuple (results_list, stats_str), όπου:
            - results_list: λίστα (a, b) για όσα ζεύγη τέμνονται.
            - stats_str: συμβολοσειρά με στατιστικά (π.χ. πλήθος ελέγχων, χρόνος).
        """
        start_time = time.time()
        total_checks = 0  # Πόσα ζεύγη (a, b) εξετάστηκαν

        for a in self.data_A:
            for b in self.data_B:
                total_checks += 1
                if a.intersects(b):
                    self.results.append((a, b))

        elapsed = time.time() - start_time
        join_count = len(self.results)

        stats_str = (
            "[NaiveSpatialJoin] Στατιστικά:\n"
            f" • Συνολικά ζεύγη (A,B) εξετάστηκαν: {total_checks}\n"
            f" • Ζεύγη που τέμνονται: {join_count}\n"
            f" • Χρόνος εκτέλεσης: {elapsed:.4f} δευτερόλεπτα.\n"
        )

        print(stats_str)
        return self.results, stats_str
