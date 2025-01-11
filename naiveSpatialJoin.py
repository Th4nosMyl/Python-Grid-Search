import time
from MBR import MBR

class NaiveSpatialJoin:
    """
    Υλοποίηση του Naive Spatial Join (ή αλλιώς Brute-force Spatial Join) 
    μεταξύ δύο συνόλων ορθογωνίων (A και B), χρησιμοποιώντας διπλό βρόχο.
    """

    def __init__(self, data_A, data_B):
        """
        :param data_A: Λίστα από MBRs (σύνολο Α).
        :param data_B: Λίστα από MBRs (σύνολο Β).
        """
        self.data_A = data_A
        self.data_B = data_B
        self.results = []

    def execute_join(self):
        """
        Εκτέλεση του Naive Spatial Join με χρονομέτρηση:
          1. Για κάθε ορθογώνιο 'a' στο A
          2. Για κάθε ορθογώνιο 'b' στο B
          3. Ελέγχουμε αν τέμνονται (a.intersects(b)).
          4. Αν τέμνονται, προσθέτουμε το tuple (a, b) στα αποτελέσματα.

        :return: (list_of_results, stats_str)
                 όπου:
                   list_of_results = λίστα από tuples (a, b) όπου a, b τέμνονται
                   stats_str = κείμενο με στατιστικά (π.χ. χρόνος εκτέλεσης, total checks κ.λπ.)
        """
        start_time = time.time()  # Έναρξη χρονομέτρησης

        total_checks = 0  # πόσα ζεύγη (a, b) εξετάστηκαν

        for a in self.data_A:
            for b in self.data_B:
                total_checks += 1
                if a.intersects(b):
                    self.results.append((a, b))

        end_time = time.time()
        elapsed = end_time - start_time

        # Στατιστικά
        join_count = len(self.results)  # πόσα ζεύγη τελικά βρέθηκαν να τέμνονται
        stats_str = (
            "[NaiveSpatialJoin] Στατιστικά:\n"
            f" • Συνολικά ζεύγη (A,B) εξετάστηκαν: {total_checks}\n"
            f" • Ζεύγη που τέμνονται: {join_count}\n"
            f" • Χρόνος εκτέλεσης: {elapsed:.4f} δευτερόλεπτα.\n"
        )

        # Εκτυπώνουμε προαιρετικά στο console
        print(stats_str)

        return self.results, stats_str
