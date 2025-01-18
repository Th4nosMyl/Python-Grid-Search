# planeSweep.py

class PlaneSweep:
    """
    Υλοποίηση Spatial Join με τη μέθοδο Plane Sweep. Η λογική βασίζεται κυρίως
    στον άξονα x, όπου δημιουργούμε events (start/end) για τα MBRs, και διατηρούμε
    λίστες ενεργών A και B για ελέγχους τομής κατά τον άξονα y.
    """

    @staticmethod
    def spatial_join(rectangles_A, rectangles_B):
        """
        Εκτελεί το Plane Sweep για Spatial Join μεταξύ δύο συνόλων ορθογωνίων (A και B).

        Διαδικασία:
          1. Δημιουργούμε "events" για κάθε ορθογώνιο:
             - (A_start, xmin, rect)
             - (A_end, xmax, rect)
             - (B_start, xmin, rect)
             - (B_end, xmax, rect)
          2. Ταξινομούμε όλα τα events κατά x (και, δευτερευόντως, κατά τύπο event).
          3. Διατηρούμε δύο λίστες ενεργών ορθογωνίων (active_A, active_B).
          4. Για κάθε event:
             - Αν είναι A_start, προσθέτουμε το rect στην active_A, ελέγχοντας τομή με κάθε B στην active_B.
             - Αν είναι A_end, αφαιρούμε το rect από την active_A.
             - Αν είναι B_start, προσθέτουμε το rect στην active_B, ελέγχοντας τομή με κάθε A στην active_A.
             - Αν είναι B_end, αφαιρούμε το rect από την active_B.
          5. Επιστρέφουμε όλα τα (rectA, rectB) ζεύγη που βρέθηκαν να τέμνονται.

        :param rectangles_A: Λίστα από MBRs (σύνολο A).
        :param rectangles_B: Λίστα από MBRs (σύνολο B).
        :return: Λίστα με ζεύγη (rectA, rectB) που τέμνονται.
        """
        events = []

        # Δημιουργία events για κάθε MBR του A
        for rect in rectangles_A:
            events.append(('A_start', rect.xmin, rect))
            events.append(('A_end', rect.xmax, rect))

        # Δημιουργία events για κάθε MBR του B
        for rect in rectangles_B:
            events.append(('B_start', rect.xmin, rect))
            events.append(('B_end', rect.xmax, rect))

        # Ταξινόμηση των events κατά x (και δευτερευόντως κατά event_type)
        events.sort(key=lambda event: (event[1], event[0]))

        active_A = []
        active_B = []
        result = []

        for event in events:
            event_type, x, rect = event

            if event_type == 'A_start':
                active_A.append(rect)
                # Έλεγχος τομής με όλα τα ενεργά B
                for b in active_B:
                    if PlaneSweep.mbr_intersect(rect, b):
                        result.append((rect, b))

            elif event_type == 'A_end':
                # Αφαιρούμε το rect από την active_A
                active_A.remove(rect)

            elif event_type == 'B_start':
                active_B.append(rect)
                # Έλεγχος τομής με όλα τα ενεργά A
                for a in active_A:
                    if PlaneSweep.mbr_intersect(a, rect):
                        result.append((a, rect))

            elif event_type == 'B_end':
                # Αφαιρούμε το rect από την active_B
                active_B.remove(rect)

        return result

    @staticmethod
    def mbr_intersect(rect1, rect2):
        """
        Ελέγχει αν δύο MBRs (rect1, rect2) τέμνονται, βάσει x- και y-συντεταγμένων.

        :param rect1: Πρώτο MBR.
        :param rect2: Δεύτερο MBR.
        :return: True αν έχουν τομή, αλλιώς False.
        """
        return not (
            rect1.xmax < rect2.xmin or
            rect1.xmin > rect2.xmax or
            rect1.ymax < rect2.ymin or
            rect1.ymin > rect2.ymax
        )
