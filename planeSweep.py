# planeSweep.py

class PlaneSweep:
    @staticmethod
    def spatial_join(rectangles_A, rectangles_B):
        """Εφαρμογή του Plane Sweep για Spatial Join μεταξύ δύο συνόλων ορθογωνίων."""
        events = []
        for rect in rectangles_A:
            events.append(('A_start', rect.xmin, rect))
            events.append(('A_end', rect.xmax, rect))
        for rect in rectangles_B:
            events.append(('B_start', rect.xmin, rect))
            events.append(('B_end', rect.xmax, rect))

        # Ταξινόμηση γεγονότων κατά x
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
                active_A.remove(rect)
            elif event_type == 'B_start':
                active_B.append(rect)
                # Έλεγχος τομής με όλα τα ενεργά A
                for a in active_A:
                    if PlaneSweep.mbr_intersect(a, rect):
                        result.append((a, rect))
            elif event_type == 'B_end':
                active_B.remove(rect)

        return result

    @staticmethod
    def mbr_intersect(rect1, rect2):
        """Έλεγχος τομής δύο MBR."""
        return not (rect1.xmax < rect2.xmin or rect1.xmin > rect2.xmax or
                    rect1.ymax < rect2.ymin or rect1.ymin > rect2.ymax)
