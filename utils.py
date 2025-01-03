# utils.py

import math

class Utils:
    @staticmethod
    def squared_distance(x1, y1, x2, y2):
        """Υπολογίζει την τετραγωνική Ευκλείδεια απόσταση μεταξύ δύο σημείων."""
        return (x1 - x2) ** 2 + (y1 - y2) ** 2

    @staticmethod
    def mindist_squared(x, y, mbr):
        """Υπολογίζει την τετραγωνική ελάχιστη απόσταση μεταξύ ενός σημείου και ενός MBR."""
        dx = max(mbr.xmin - x, 0, x - mbr.xmax)
        dy = max(mbr.ymin - y, 0, y - mbr.ymax)
        return dx**2 + dy**2
