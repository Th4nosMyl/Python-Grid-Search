class PlaneSweep:
    """
    Υλοποίηση του Spatial Join με χρήση Plane Sweep (επίπεδο σάρωσης).
    Δουλεύει κυρίως κατά τον άξονα x:
    1. Συγκεντρώνουμε "events" (ακμές έναρξης και τέλους) για κάθε MBR.
    2. Ταξινομούμε τα events κατά x.
    3. Διατηρούμε λίστα ενεργών A, B και ελέγχουμε τομή (intersection) 
       μόνο μεταξύ ενεργών (overlapping) MBRs κατά τον y άξονα.
    """

    @staticmethod
    def spatial_join(rectangles_A, rectangles_B):
        """
        Εφαρμογή του Plane Sweep για Spatial Join μεταξύ δύο συνόλων ορθογωνίων.
        
        :param rectangles_A: Λίστα από MBRs (σύνολο Α).
        :param rectangles_B: Λίστα από MBRs (σύνολο Β).
        :return: Μια λίστα με tuples (rectA, rectB) για κάθε ζεύγος ορθογωνίων που τέμνονται.
        """
        events = []
        # Δημιουργούμε events για κάθε MBR του A
        for rect in rectangles_A:
            events.append(('A_start', rect.xmin, rect))
            events.append(('A_end', rect.xmax, rect))
        # Δημιουργούμε events για κάθε MBR του B
        for rect in rectangles_B:
            events.append(('B_start', rect.xmin, rect))
            events.append(('B_end', rect.xmax, rect))

        # Ταξινόμηση γεγονότων κατά x (και δευτερευόντως ανά τύπο event)
        events.sort(key=lambda event: (event[1], event[0]))

        active_A = []
        active_B = []
        result = []

        for event in events:
            event_type, x, rect = event
            if event_type == 'A_start':
                # Προσθέτουμε το rect στην ενεργή λίστα του Α
                active_A.append(rect)
                # Ελέγχουμε τομή με όλα τα ενεργά B
                for b in active_B:
                    if PlaneSweep.mbr_intersect(rect, b):
                        result.append((rect, b))
            elif event_type == 'A_end':
                # Αφαιρούμε το rect από την ενεργή λίστα του Α
                active_A.remove(rect)
            elif event_type == 'B_start':
                # Προσθέτουμε το rect στην ενεργή λίστα του Β
                active_B.append(rect)
                # Ελέγχουμε τομή με όλα τα ενεργά A
                for a in active_A:
                    if PlaneSweep.mbr_intersect(a, rect):
                        result.append((a, rect))
            elif event_type == 'B_end':
                # Αφαιρούμε το rect από την ενεργή λίστα του Β
                active_B.remove(rect)

        return result

    @staticmethod
    def mbr_intersect(rect1, rect2):
        """
        Έλεγχος τομής δύο MBRs μέσω των x- και y-συντεταγμένων.
        
        :param rect1: Πρώτο MBR.
        :param rect2: Δεύτερο MBR.
        :return: True αν τέμνονται, αλλιώς False.
        """
        return not (
            rect1.xmax < rect2.xmin or
            rect1.xmin > rect2.xmax or
            rect1.ymax < rect2.ymin or
            rect1.ymin > rect2.ymax
        )
