import math

class MBR:
    """
    Η κλάση MBR (Minimum Bounding Rectangle) αναπαριστά ένα ορθογώνιο
    που ορίζεται από τις συντεταγμένες (xmin, ymin) και (xmax, ymax).
    Χρησιμοποιείται για διάφορες χωρικές πράξεις, όπως intersection κ.λπ.
    """

    def __init__(self, id, xmin, ymin, xmax, ymax):
        """
        :param id: Οποιοδήποτε αναγνωριστικό (π.χ. string ή αριθμός).
        :param xmin: Ελάχιστο x-όριο.
        :param ymin: Ελάχιστο y-όριο.
        :param xmax: Μέγιστο x-όριο.
        :param ymax: Μέγιστο y-όριο.
        """
        self.id = id
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmax
        self.ymax = ymax

    def intersects(self, other):
        """
        Ελέγχει αν δύο MBRs τέμνονται.
        :param other: Ένα άλλο MBR.
        :return: True αν τέμνονται, False διαφορετικά.
        """
        return not (
            self.xmax < other.xmin or
            self.xmin > other.xmax or
            self.ymax < other.ymin or
            self.ymin > other.ymax
        )

    def center(self):
        """
        Επιστρέφει το κέντρο του MBR ως tuple (x, y).
        :return: (center_x, center_y)
        """
        center_x = (self.xmin + self.xmax) / 2
        center_y = (self.ymin + self.ymax) / 2
        return (center_x, center_y)

    def contains_point(self, x, y):
        """
        Ελέγχει αν το σημείο (x, y) βρίσκεται μέσα στο MBR.
        :param x: Συντεταγμένη x του σημείου.
        :param y: Συντεταγμένη y του σημείου.
        :return: True αν ανήκει, False διαφορετικά.
        """
        return (self.xmin <= x <= self.xmax) and (self.ymin <= y <= self.ymax)

    def distance_to_point(self, x, y):
        """
        Υπολογίζει την ελάχιστη Ευκλείδεια απόσταση από το σημείο (x, y) μέχρι το MBR.
        :param x: Συντεταγμένη x του σημείου.
        :param y: Συντεταγμένη y του σημείου.
        :return: Απόσταση (float).
        """
        dx = max(self.xmin - x, 0, x - self.xmax)
        dy = max(self.ymin - y, 0, y - self.ymax)
        return math.sqrt(dx**2 + dy**2)

    def intersection_mbr(self, other):
        """
        Επιστρέφει το MBR της τομής ανάμεσα σε self και other, αν υπάρχει.
        :param other: Ένα άλλο MBR.
        :return: Ένα νέο MBR που ορίζει την τομή ή None αν δεν υπάρχει τομή.
        """
        if not self.intersects(other):
            return None
        return MBR(
            None,  # Το ID της τομής δεν είναι απαραίτητο
            max(self.xmin, other.xmin),
            max(self.ymin, other.ymin),
            min(self.xmax, other.xmax),
            min(self.ymax, other.ymax)
        )

    def __repr__(self):
        return (
            f"MBR(id={self.id}, "
            f"xmin={self.xmin}, ymin={self.ymin}, "
            f"xmax={self.xmax}, ymax={self.ymax})"
        )

    def __eq__(self, other):
        if isinstance(other, MBR):
            return (
                self.id == other.id and
                self.xmin == other.xmin and
                self.ymin == other.ymin and
                self.xmax == other.xmax and
                self.ymax == other.ymax
            )
        return False

    def __hash__(self):
        return hash((self.id, self.xmin, self.ymin, self.xmax, self.ymax))
