# pointGeneratorUnif.py

import random
import io

class PointGeneratorUnif:
    """
    Κλάση που δημιουργεί τυχαία ορθογώνια (MBRs) εντός ενός πλαισίου (xL, yL, xU, yU)
    και τα επιστρέφει είτε σε αρχείο CSV είτε ως in-memory string.
    """

    def __init__(self, xL=0, yL=0, xU=1, yU=1):
        """
        :param xL: Ελάχιστο x-όριο για τη γεννήτρια.
        :param yL: Ελάχιστο y-όριο για τη γεννήτρια.
        :param xU: Μέγιστο x-όριο για τη γεννήτρια.
        :param yU: Μέγιστο y-όριο για τη γεννήτρια.
        """
        self.xL = xL
        self.yL = yL
        self.xU = xU
        self.yU = yU

    def generate_rectangles_in_memory(self, n, include_id=False, dataset_label='A',
                                      max_width=1.0, max_height=1.0):
        """
        Παράγει n τυχαία ορθογώνια σε μορφή CSV (in-memory) και επιστρέφει το περιεχόμενο
        ως string.

        :param n: Πλήθος ορθογωνίων προς δημιουργία.
        :param include_id: Αν True, συμπεριλαμβάνεται στήλη ID (π.χ. "A1").
        :param dataset_label: Ετικέτα στο ID αν include_id=True (π.χ. 'A').
        :param max_width: Μέγιστο τυχαίο πλάτος.
        :param max_height: Μέγιστο τυχαίο ύψος.
        :return: Ένα string που περιέχει τα δεδομένα σε CSV μορφή.
        """
        output = io.StringIO()
        # Επικεφαλίδες
        if include_id:
            output.write("ID,xmin,ymin,xmax,ymax\n")
        else:
            output.write("xmin,ymin,xmax,ymax\n")

        for i in range(1, n + 1):
            w = random.uniform(0, max_width)
            h = random.uniform(0, max_height)

            if (self.xU - w) < self.xL or (self.yU - h) < self.yL:
                # Αν δεν υπάρχει αρκετός χώρος, χειριζόμαστε το edge case
                w = max(0, self.xU - self.xL)
                h = max(0, self.yU - self.yL)

            xmin = random.uniform(self.xL, self.xU - w)
            ymin = random.uniform(self.yL, self.yU - h)
            xmax = xmin + w
            ymax = ymin + h

            if include_id:
                obj_id = f"{dataset_label}{i}"
                output.write(f"{obj_id},{xmin},{ymin},{xmax},{ymax}\n")
            else:
                output.write(f"{xmin},{ymin},{xmax},{ymax}\n")

        return output.getvalue()
