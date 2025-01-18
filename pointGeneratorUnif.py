import random
import io

class PointGeneratorUnif:
    """
    Κλάση που δημιουργεί τυχαία ορθογώνια (MBRs) εντός ενός ορθογωνίου πλαισίου
    [xL, xU] x [yL, yU], και τα αποθηκεύει σε αρχείο CSV ή τα επιστρέφει
    ως in-memory string (ανάλογα με τη μέθοδο που καλείται).
    """

    def __init__(self, filename, xL=0, yL=0, xU=1, yU=1):
        """
        Αρχικοποιεί τη γεννήτρια τυχαίων MBRs.

        :param filename: Όνομα αρχείου CSV στο οποίο θα γράφει η generate_rectangles(...).
        :param xL: Ελάχιστη τιμή x.
        :param yL: Ελάχιστη τιμή y.
        :param xU: Μέγιστη τιμή x.
        :param yU: Μέγιστη τιμή y.
        """
        self.filename = filename
        self.xL = xL
        self.yL = yL
        self.xU = xU
        self.yU = yU

    def generate_rectangles(self, n, include_id=False, dataset_label='A',
                            max_width=1.0, max_height=1.0):
        """
        Δημιουργεί n τυχαία ορθογωνία και τα αποθηκεύει σε ένα αρχείο CSV (self.filename).

        :param n: Πλήθος ορθογωνίων.
        :param include_id: Αν True, περιλαμβάνεται στήλη ID (π.χ. "A1").
        :param dataset_label: Ετικέτα ID αν include_id=True.
        :param max_width: Μέγιστο τυχαίο πλάτος.
        :param max_height: Μέγιστο τυχαίο ύψος.
        """
        try:
            with open(self.filename, 'w') as file:
                if include_id:
                    file.write("ID,xmin,ymin,xmax,ymax\n")
                else:
                    file.write("xmin,ymin,xmax,ymax\n")

                for i in range(1, n + 1):
                    w = random.uniform(0, max_width)
                    h = random.uniform(0, max_height)

                    if (self.xU - w) < self.xL or (self.yU - h) < self.yL:
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
                f"Δημιουργήθηκε το αρχείο '{self.filename}' με {n} ορθογώνια εντός "
                f"x=[{self.xL}, {self.xU}], y=[{self.yL}, {self.yU}], "
                f"max_width={max_width}, max_height={max_height}"
            )

        except IOError as e:
            print(f"Σφάλμα κατά τη δημιουργία του αρχείου: {e}")


    def generate_rectangles_in_memory(self, n, include_id=False, dataset_label='A',
                                      max_width=1.0, max_height=1.0):
        """
        Δημιουργεί n τυχαία ορθογώνια (MBRs) και ΕΠΙΣΤΡΕΦΕΙ τα δεδομένα ως string CSV
        αντί να τα γράψει σε αρχείο. Ιδανικό για χρήση με Streamlit
        (π.χ. st.download_button).

        :param n: Πλήθος ορθογωνίων.
        :param include_id: Αν True, περιλαμβάνεται στήλη ID (π.χ. "A1").
        :param dataset_label: Ετικέτα ID αν include_id=True.
        :param max_width: Μέγιστο τυχαίο πλάτος.
        :param max_height: Μέγιστο τυχαίο ύψος.
        :return: Ένα string που περιέχει το CSV.
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
