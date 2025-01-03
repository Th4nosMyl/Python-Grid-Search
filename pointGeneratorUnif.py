# pointGeneratorUnif.py

import random

class PointGeneratorUnif:
    def __init__(self, filename, xL=0, yL=0, xU=1, yU=1):
        self.filename = filename
        self.xL = xL
        self.yL = yL
        self.xU = xU
        self.yU = yU

    def generate_rectangles(self, n, include_id=False, dataset_label='A'):
        """Δημιουργία τυχαίων ορθογωνίων εντός των ορίων του grid."""
        try:
            with open(self.filename, 'w') as file:
                if include_id:
                    file.write("ID,xmin,ymin,xmax,ymax\n")  # Επικεφαλίδες
                else:
                    file.write("xmin,ymin,xmax,ymax\n")  # Επικεφαλίδες χωρίς ID
                for i in range(1, n + 1):
                    xmin = random.uniform(self.xL, self.xU - 1)  # Έστω πλάτος=1
                    ymin = random.uniform(self.yL, self.yU - 1)  # Έστω ύψος=1
                    xmax = xmin + 1.0
                    ymax = ymin + 1.0
                    if include_id:
                        id = f"{dataset_label}{i}"
                        file.write(f"{id},{xmin},{ymin},{xmax},{ymax}\n")
                    else:
                        file.write(f"{xmin},{ymin},{xmax},{ymax}\n")
            print(f"Δημιουργήθηκε το αρχείο {self.filename} με {n} ορθογωνία εντός του grid: "
                  f"x=[{self.xL}, {self.xU}], y=[{self.yL}, {self.yU}]")
        except IOError as e:
            print(f"Σφάλμα κατά τη δημιουργία του αρχείου: {e}")
