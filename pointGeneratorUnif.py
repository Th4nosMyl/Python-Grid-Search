# pointGeneratorUnif.py

import random

class PointGeneratorUnif:
    """
    Κλάση που δημιουργεί τυχαία ορθογώνια (MBRs) εντός ενός ορθογωνίου πλαισίου
    [xL, xU] x [yL, yU], και τα αποθηκεύει σε ένα αρχείο CSV.
    Επιτρέπει επιλογές για τυχαίο πλάτος και ύψος (max_width, max_height).
    """

    def __init__(self, filename, xL=0, yL=0, xU=1, yU=1):
        """
        Αρχικοποιεί τη γεννήτρια τυχαίων MBRs.

        :param filename: Όνομα του αρχείου CSV που θα γραφτούν τα δεδομένα.
        :param xL: Ελάχιστη τιμή x (αριστερό όριο του πλαισίου).
        :param yL: Ελάχιστη τιμή y (κάτω όριο του πλαισίου).
        :param xU: Μέγιστη τιμή x (δεξιό όριο του πλαισίου).
        :param yU: Μέγιστη τιμή y (άνω όριο του πλαισίου).
        """
        self.filename = filename
        self.xL = xL
        self.yL = yL
        self.xU = xU
        self.yU = yU

    def generate_rectangles(self, n, include_id=False, dataset_label='A',
                            max_width=1.0, max_height=1.0):
        """
        Δημιουργεί n τυχαία ορθογώνια (MBRs) και τα αποθηκεύει σε μορφή CSV αρχείου.

        - Αν include_id=True, συμπεριλαμβάνεται στήλη ID (π.χ. "A1").
        - Αν θες συγκεκριμένες διαστάσεις, ορίζεις max_width και max_height.
          Π.χ. max_width=5, max_height=5 για ορθογώνια έως 5x5.

        :param n: Αριθμός ορθογωνίων που θα δημιουργηθούν.
        :param include_id: Αν True, δημιουργεί στήλη ID ως dataset_label + running_number.
        :param dataset_label: Πρόθεμα ID αν include_id=True (π.χ. 'A', 'B').
        :param max_width: Μέγιστο τυχαίο πλάτος ορθογωνίων.
        :param max_height: Μέγιστο τυχαίο ύψος ορθογωνίων.
        """
        try:
            with open(self.filename, 'w') as file:
                # Γράφουμε επικεφαλίδες στο CSV
                if include_id:
                    file.write("ID,xmin,ymin,xmax,ymax\n")
                else:
                    file.write("xmin,ymin,xmax,ymax\n")

                for i in range(1, n + 1):
                    # 1. Τυχαίο πλάτος & ύψος εντός [0, max_width/height]
                    w = random.uniform(0, max_width)
                    h = random.uniform(0, max_height)

                    # 2. Διασφαλίζουμε ότι έχουμε περιθώριο:
                    #    xmin+w <= xU  και  ymin+h <= yU
                    if (self.xU - w) < self.xL or (self.yU - h) < self.yL:
                        # Σε περίπτωση ασύμβατων παραμέτρων, φτιάχνουμε degenerate rectangle (w=0,h=0)
                        w = max(0, self.xU - self.xL)
                        h = max(0, self.yU - self.yL)

                    # 3. Επιλέγουμε τυχαίο xmin, ymin ώστε να χωράει το (w, h)
                    xmin = random.uniform(self.xL, self.xU - w)
                    ymin = random.uniform(self.yL, self.yU - h)

                    xmax = xmin + w
                    ymax = ymin + h

                    # 4. Γράφουμε στο αρχείο CSV, με ή χωρίς ID στήλη
                    if include_id:
                        obj_id = f"{dataset_label}{i}"
                        file.write(f"{obj_id},{xmin},{ymin},{xmax},{ymax}\n")
                    else:
                        file.write(f"{xmin},{ymin},{xmax},{ymax}\n")

            print(
                f"Δημιουργήθηκε το αρχείο '{self.filename}' με {n} ορθογώνια εντός "
                f"x=[{self.xL}, {self.xU}], y=[{self.yL}, {self.yU}], "
                f"max_width={max_width}, max_height={max_height}"
            )

        except IOError as e:
            print(f"Σφάλμα κατά τη δημιουργία του αρχείου: {e}")
