# naiveSpatialJoin.py

from MBR import MBR

class NaiveSpatialJoin:
    def __init__(self, data_A, data_B):
        self.data_A = data_A
        self.data_B = data_B
        self.results = []

    def execute_join(self):
        """Εκτέλεση του Naive Spatial Join με διπλό βρόχο."""
        for a in self.data_A:
            for b in self.data_B:
                if a.intersects(b):
                    self.results.append((a, b))
        return self.results
