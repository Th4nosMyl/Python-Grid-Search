# spatialJoinPBSM.py

from grid import Grid
from MBR import MBR

class SpatialJoinPBSM:
    def __init__(self, grid):
        self.grid = grid
        self.results = set()  # Χρήση set για αποφυγή διπλοτύπων

    def execute_join(self):
        """Εκτέλεση του Spatial Join χρησιμοποιώντας τον PBSM αλγόριθμο."""
        if 'A' not in self.grid.datasets or 'B' not in self.grid.datasets:
            print("Τα σύνολα A και B πρέπει να φορτωθούν πριν εκτελέσεις τον Spatial Join.")
            return []

        # Ανάγνωση datasets A και B
        data_A = self.grid.get_dataset('A')
        data_B = self.grid.get_dataset('B')

        # Επανάληψη σε κάθε κελί του grid
        for i in range(self.grid.m):
            for j in range(self.grid.m):
                cell = self.grid.cells[i][j]
                if not cell.objects_A or not cell.objects_B:
                    continue  # Αν ένα από τα datasets δεν έχει αντικείμενα στο κελί, παραλείπουμε
                for a in cell.objects_A:
                    for b in cell.objects_B:
                        if a.intersects(b):
                            self.results.add((a, b))  # Το set αποτρέπει τα διπλότυπα
        return list(self.results)
