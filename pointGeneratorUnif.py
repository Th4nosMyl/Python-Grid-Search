import random

class PointGeneratorUnif:
    """
    Δημιουργεί τυχαία ορθογώνια (MBRs) εντός ενός πλαισίου (xL, xU, yL, yU)
    και τα αποθηκεύει σε ένα CSV αρχείο.
    """

    def __init__(self, filename, xL=0, yL=0, xU=1, yU=1):
        """
        :param filename: Όνομα του αρχείου στο οποίο θα γραφτούν τα δεδομένα.
        :param xL: Ελάχιστο x-όριο για τη γεννήτρια.
        :param yL: Ελάχιστο y-όριο για τη γεννήτρια.
        :param xU: Μέγιστο x-όριο για τη γεννήτρια.
        :param yU: Μέγιστο y-όριο για τη γεννήτρια.
        """
        self.filename = filename
        self.xL = xL
        self.yL = yL
        self.xU = xU
        self.yU = yU

    def generate_rectangles(self, n, include_id=False, dataset_label='A',
                            max_width=1.0, max_height=1.0):
        """
        Δημιουργεί και αποθηκεύει n ορθογώνια (MBRs) σε μορφή CSV.
        
        * Αν δεν θέλεις τυχαίο πλάτος/ύψος, μπορείς να ορίσεις max_width=1, max_height=1,
          και θα παράγονται ορθογώνια περίπου 1x1.
        * Αν θες, π.χ., ορθογώνια έως 5x5, βάζεις max_width=5, max_height=5.
        
        :param n: Αριθμός ορθογωνίων που θα δημιουργηθούν.
        :param include_id: Αν True, θα συμπεριληφθεί στήλη ID (π.χ. "A1").
        :param dataset_label: Αν include_id=True, χρησιμοποιείται ως prefix (π.χ. "A1").
        :param max_width: Μέγιστο τυχαίο πλάτος ορθογωνίων.
        :param max_height: Μέγιστο τυχαίο ύψος ορθογωνίων.
        """
        try:
            with open(self.filename, 'w') as file:
                # Επικεφαλίδες
                if include_id:
                    file.write("ID,xmin,ymin,xmax,ymax\n")
                else:
                    file.write("xmin,ymin,xmax,ymax\n")

                for i in range(1, n + 1):
                    # Τυχαίο πλάτος & ύψος εντός [0, max_width], [0, max_height]
                    w = random.uniform(0, max_width)
                    h = random.uniform(0, max_height)

                    # Διασφαλίζουμε ότι υπάρχει χώρος: 
                    # xmin επιλέγεται έτσι ώστε xmin+w <= xU
                    # ymin επιλέγεται έτσι ώστε ymin+h <= yU
                    # Άρα το πάνω όριο για xmin είναι (xU - w), κ.ο.κ.
                    if (self.xU - w) < self.xL or (self.yU - h) < self.yL:
                        # Αν για κάποιο λόγο max_width ή max_height δεν ταιριάζουν
                        # με το (xL, xU, yL, yU), απλώς αγνόησε/μείωσε w ή h:
                        # ή μπορείς να βάλεις continue για να μην παραχθεί αυτό το ορθογώνιο.
                        # Εδώ απλά συνεχίζουμε με w,h=0 (σημαίνει degenerate rectangle)
                        w = max(0, self.xU - self.xL)
                        h = max(0, self.yU - self.yL)

                    xmin = random.uniform(self.xL, self.xU - w)
                    ymin = random.uniform(self.yL, self.yU - h)

                    xmax = xmin + w
                    ymax = ymin + h

                    if include_id:
                        obj_id = f"{dataset_label}{i}"
                        file.write(f"{obj_id},{xmin},{ymin},{xmax},{ymax}\n")
                    else:
                        file.write(f"{xmin},{ymin},{xmax},{ymax}\n")

            print(
                f"Δημιουργήθηκε το αρχείο {self.filename} με {n} ορθογώνια εντός: "
                f"x=[{self.xL}, {self.xU}], y=[{self.yL}, {self.yU}], "
                f"max_width={max_width}, max_height={max_height}"
            )

        except IOError as e:
            print(f"Σφάλμα κατά τη δημιουργία του αρχείου: {e}")
