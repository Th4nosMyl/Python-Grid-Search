# 🌐 Grid-Based Spatial Data Processing

## 📚 Εισαγωγή

Στη σύγχρονη εποχή, όπου τα γεωγραφικά δεδομένα (MBRs, πολυγωνικά σχήματα κ.λπ.) αυξάνονται συνεχώς, η ανάγκη για αποδοτικούς αλγορίθμους **χωρικής επεξεργασίας** γίνεται επιτακτική. Αυτή η εφαρμογή, υλοποιημένη σε **Streamlit**, αξιοποιεί ένα **Grid-based** μοντέλο διαμέρισης του χώρου, επιτρέποντας την υλοποίηση και διεπαφή με βασικούς αλγόριθμους χωρικών ερωτημάτων.

Με απλά λόγια, μπορούμε:
- Να δημιουργήσουμε ή να φορτώσουμε δεδομένα ορθογωνίων (MBRs),
- Να τρέξουμε ερωτήματα όπως **k-Nearest Neighbors**, **Linear Scan**, **Spatial Join** (PBSM ή Naive), **Skyline Query** κ.ά.,
- Να δούμε αποτελέσματα & στατιστικά,
- Και (προαιρετικά) να εμφανίσουμε σημεία σε διαδραστικό χάρτη **Folium**.

---

## 🎥 Live Demo

Αν επιθυμείτε να δοκιμάσετε την εφαρμογή on-line, ακολουθήστε τον σύνδεσμο:

🔗 [Live Demo](https://grid-search-th4nosmyl.streamlit.app/)

(Σε περίπτωση που δεν είναι διαθέσιμος, μπορείτε να τρέξετε τοπικά, ακολουθώντας τις οδηγίες παρακάτω.)

---

## 🎯 Στόχος του Project

Ο στόχος αυτής της εφαρμογής είναι να προσφέρει ένα **φιλικό** προς τον χρήστη περιβάλλον για:

1. **Δημιουργία Δεδομένων**: Τυχαία ορθογώνια (MBRs) μέσω `PointGeneratorUnif`.
2. **Φόρτωση Δεδομένων**: CSV αρχείων με μορφή `ID,xmin,ymin,xmax,ymax`.
3. **Εκτέλεση Χωρικών Αλγορίθμων**:
   - **Linear Scan (k-NN)**: Γραμμική σάρωση για αναζήτηση γειτόνων.
   - **Grid-based k-NN**: Αξιοποίηση του grid για k-Nearest Neighbors.
   - **Spatial Join (PBSM)**: Partition-Based Spatial Merge μεταξύ δύο συνόλων A,B.
   - **Naive Spatial Join**: Αφελής διπλός βρόχος για τομές.
   - **Skyline Query**: Εντοπισμός αντικειμένων που δεν κυριαρχούνται (Pareto set).
4. **Λήψη & Οπτικοποίηση**: Αποθήκευση αποτελεσμάτων ως `.txt` & εμφάνιση δεδομένων σε χάρτη (Folium).

---

## 🛠️ Τεχνολογίες που Χρησιμοποιήθηκαν

- **Python**: Η κύρια γλώσσα προγραμματισμού.
- **Streamlit**: Για τη γρήγορη ανάπτυξη διαδραστικού Web UI.
- **Pandas**: Για φόρτωση/επεξεργασία CSV αρχείων.
- **Folium & streamlit-folium**: Για την εμφάνιση δεδομένων πάνω σε διαδραστικό χάρτη.
- **Τυπικές Python βιβλιοθήκες** (π.χ. `math`, `random`, `heapq`, κ.λπ.): Γενικοί υπολογισμοί και βοηθητικά.

---

## 🗂️ Δομή Δεδομένων & Grid

Η εφαρμογή χρησιμοποιεί μια κλάση **`Grid`** που ορίζει τα όρια \((xL, yL)\) - \((xU, yU)\) και διαμερίζει τον χώρο σε \(m \times m\) **κελιά**. Κάθε κελί (Cell) διατηρεί λίστες MBRs (π.χ. `cell.objects['default']`, `cell.objects['A']` κ.ο.κ.). Όταν τρέχουμε αλγόριθμους (π.χ. k-NN), σαρώνουμε κελιά γύρω από το σημείο ενδιαφέροντος· για Spatial Join (PBSM), ελέγχουμε μόνο τα κελιά που έχουν ταυτόχρονα αντικείμενα A & B.

---

## 📊 Αλγόριθμοι που Χρησιμοποιήθηκαν

1. **Linear Scan (k-NN)**
   - Διαβάζει το CSV, υπολογίζει την απόσταση όλων των MBRs από ένα query point, ταξινομεί, και επιστρέφει τα \(k\) πιο κοντινά.

2. **k-NN με Grid**
   - Ξεκινά από το κελί που περιέχει το query point \((qx, qy)\), επεκτείνεται σε “hops” όταν χρειάζεται. Αξιοποιεί το **mindist** για να διακόπτει πρόωρα την αναζήτηση.

3. **Spatial Join (PBSM)**
   - Έλεγχος τομών μόνο μεταξύ αντικειμένων (A, B) που πέφτουν στο ίδιο κελί. Περιορίζουμε έτσι δραστικά τις συγκρίσεις.

4. **Naive Spatial Join**
   - Για κάθε a ∈ A, και κάθε b ∈ B, ελέγχουμε αν τέμνονται. Ξεκάθαρος διπλός βρόχος.

5. **Skyline Query**
   - Βρίσκει τα MBRs που δεν κυριαρχούνται από κανένα άλλο, εκμεταλλευόμενο τη δυνατότητα να skip-άρει ολόκληρα κελιά που είναι ήδη dominated.

---

## 🌟 Χαρακτηριστικά της Εφαρμογής

- **Δημιουργία Τυχαίων Δεδομένων** με `PointGeneratorUnif`: Δεν απαιτείται εξωτερικό dataset.
- **Φόρτωση CSV**: Επιτρέπει την επιλογή "A", "B", "default" για τα δεδομένα.
- **Download Αποτελεσμάτων**: Παράγει `.txt` που περιέχει τόσο τα αποτελέσματα (π.χ. ποια ζεύγη τέμνονται) όσο και τα στατιστικά (χρόνος, πόσα ζεύγη ελέγχθηκαν, κ.ο.κ.).
- **Εμφάνιση σε Χάρτη**: Αν ενεργοποιήσεις το checkbox, μπορείς να δεις τα αντικείμενα σε διαδραστικό **Folium** map.

---

## 📄 Πώς να Ξεκινήσετε Τοπικά

1. **Κλώνος ή Λήψη**:  
   ```bash
   git clone https://github.com/YourUsername/GridBasedSpatialApp.git
   cd GridBasedSpatialApp
2. **Εγκατάσταση Βιβλιοθηκών (μέσω requirements.txt):**
    ```bash
    pip install -r requirements.txt
3. **Εκτέλεση Εφαρμογής:**
    ```bash
    streamlit run main.py
4. **Πρόσβαση: Ανοίγετε τον browser σας στο http://localhost:8501.**

## 💻 Χρήση της Εφαρμογής

- **Grid Settings** (στην sidebar): Καθορίστε τα όρια \((xL, yL)\) - \((xU, yU)\) και το \(m\) (πόσα κελιά/άξονα). Πατώντας “Create/Reset Grid” δημιουργείται νέο Grid.
- **Μενού Επιλογών**:
  1. **Δημιουργία Αρχείου Δεδομένων**: Παράγει τυχαία ορθογώνια σε CSV και επιτρέπει download.
  2. **Linear Scan (k-NN)**: Αναζήτηση κοντινότερων γειτόνων με γραμμική σάρωση.
  3. **k-NN με Grid**: Πιο αποδοτικό k-NN χρησιμοποιώντας το grid.
  4. **Spatial Join (PBSM)**: Συγκρίνει μόνο τα MBRs που βρίσκονται στο ίδιο κελί.
  5. **Naive Spatial Join**: Διπλός βρόχος για όλα τα (a, b).
  6. **Skyline Query**: Βρίσκει τα μη κυριαρχούμενα σημεία.
- **Αποθήκευση**: Στο τέλος κάθε αλγορίθμου, μπορείτε να κάνετε λήψη των αποτελεσμάτων και των στατιστικών ως `.txt`.
- **Προβολή σε Χάρτη**: Επιλέξτε “Προβολή σε χάρτη” (σε συγκεκριμένα ερωτήματα, όπως το Skyline) για να οπτικοποιήσετε τα δεδομένα σε διαδραστικό χάρτη Folium.

---

## 📊 Παραδείγματα

1. **PBSM Join**  
   - Φορτώστε δύο CSV, π.χ. `A.csv` και `B.csv`.  
   - Για κάθε κελί, εξετάζονται μόνο τα MBRs από το A και το B που “πέφτουν” σε αυτό.  
   - Εμφανίζεται ο συνολικός χρόνος, πόσα κελιά παραλείφθηκαν επειδή ήταν άδεια κ.ο.κ.

2. **Skyline**  
   - Με π.χ. 50 τυχαία ορθογώνια (“data.csv”), φορτώνεται στο Grid.  
   - Η εφαρμογή ταξινομεί τα κελιά κατά `xmin, ymin`, κάνει skip εκείνα που κυριαρχούνται πλήρως.  
   - Τέλος, αναφέρει πόσα αντικείμενα εξετάστηκαν, πόσα παραλήφθηκαν (dominated), και πόσα βρέθηκαν στο Skyline.

---

## 🚀 Οφέλη

- **Απλό & Ευέλικτο**  
  Ο χρήστης δεν χρειάζεται καμία γνώση προγραμματισμού για να εκτελέσει κλασικούς αλγορίθμους χωρικής επεξεργασίας.

- **Grid-based**  
  Το μοντέλο διαμέρισης (grid) μειώνει δραστικά τις περιττές συγκρίσεις σε ερωτήματα όπως Spatial Join, k-NN, Skyline.

- **Εκπαιδευτικό**  
  Αποτελεί παράδειγμα εφαρμογής βασικών τεχνικών (dominance checks, PBSM κ.λπ.) σε Python/Streamlit, μαζί με απλή χαρτογραφική απεικόνιση (Folium).

---

## 📩 Επικοινωνία

- **Προγραμματιστής:** [Θανάσης Μυλωνάς](mailto:Th4nosMylonas@gmail.com)
- **GitHub:** [Th4nosMyl](https://github.com/Th4nosMyl)

Είστε ελεύθεροι να ανοίξετε **issues** ή pull requests αν θέλετε να προτείνετε βελτιώσεις ή να αναφέρετε σφάλματα!