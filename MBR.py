# MBR.py

import math

class MBR:
    """
    Κλάση που αναπαριστά ένα Ορθογώνιο Ελάχιστης Περιβάλλουσας (MBR),
    οριζόμενο από τα όρια (xmin, ymin) και (xmax, ymax).
    Προσφέρει διάφορες χωρικές πράξεις (έλεγχος τομής, απόστασης κ.λπ.).
    """

    def __init__(self, id, xmin, ymin, xmax, ymax):
        """
        Αρχικοποιεί ένα MBR.

        :param id: Αναγνωριστικό (string ή αριθμός) του MBR.
        :param xmin: Ελάχιστη τιμή x.
        :param ymin: Ελάχιστη τιμή y.
        :param xmax: Μέγιστη τιμή x.
        :param ymax: Μέγιστη τιμή y.
        """
        self.id = id
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmax
        self.ymax = ymax

    def intersects(self, other):
        """
        Ελέγχει αν το τρέχον MBR τέμνεται με ένα άλλο MBR.

        :param other: Το άλλο MBR προς έλεγχο τομής.
        :return: True αν έχουν τομή, αλλιώς False.
        """
        return not (
            self.xmax < other.xmin or
            self.xmin > other.xmax or
            self.ymax < other.ymin or
            self.ymin > other.ymax
        )

    def center(self):
        """
        Υπολογίζει το κέντρο του MBR.

        :return: Ένα tuple (center_x, center_y).
        """
        center_x = (self.xmin + self.xmax) / 2
        center_y = (self.ymin + self.ymax) / 2
        return (center_x, center_y)

    def contains_point(self, x, y):
        """
        Ελέγχει αν ένα σημείο (x, y) βρίσκεται εντός αυτού του MBR.

        :param x: Συντεταγμένη x του σημείου.
        :param y: Συντεταγμένη y του σημείου.
        :return: True αν το σημείο ανήκει στο MBR, αλλιώς False.
        """
        return (self.xmin <= x <= self.xmax) and (self.ymin <= y <= self.ymax)

    def distance_to_point(self, x, y):
        """
        Υπολογίζει την ελάχιστη Ευκλείδεια απόσταση από το σημείο (x, y)
        μέχρι το MBR.

        :param x: Συντεταγμένη x του σημείου.
        :param y: Συντεταγμένη y του σημείου.
        :return: Απόσταση σε float.
        """
        dx = max(self.xmin - x, 0, x - self.xmax)
        dy = max(self.ymin - y, 0, y - self.ymax)
        return math.sqrt(dx**2 + dy**2)

    def intersection_mbr(self, other):
        """
        Υπολογίζει το MBR που αντιστοιχεί στην τομή με ένα άλλο MBR,
        αν υπάρχει.

        :param other: Το άλλο MBR.
        :return: Ένα νέο MBR που αναπαριστά την τομή τους ή None αν δεν τέμνονται.
        """
        if not self.intersects(other):
            return None
        return MBR(
            None,
            max(self.xmin, other.xmin),
            max(self.ymin, other.ymin),
            min(self.xmax, other.xmax),
            min(self.ymax, other.ymax)
        )

    def __repr__(self):
        """
        Επιστρέφει μια συμβολοσειρά που περιγράφει το τρέχον MBR,
        εμφανίζοντας ID και όρια.
        """
        return (
            f"MBR(id={self.id}, "
            f"xmin={self.xmin}, ymin={self.ymin}, "
            f"xmax={self.xmax}, ymax={self.ymax})"
        )

    def __eq__(self, other):
        """
        Ορίζει την ισότητα δύο MBRs βάσει του ID και των ορίων (xmin, ymin, xmax, ymax).
        """
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
        """
        Επιτρέπει τη χρήση ενός MBR σε δομές όπως set ή dictionary keys,
        ορίζοντας ένα hash που βασίζεται στα (id, xmin, ymin, xmax, ymax).
        """
        return hash((self.id, self.xmin, self.ymin, self.xmax, self.ymax))
