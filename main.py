# main.py

import os
from pointGeneratorUnif import PointGeneratorUnif
from grid import Grid
from kNN import kNN
from linearScan import LinearScan
from spatialJoinPBSM import SpatialJoinPBSM
from naiveSpatialJoin import NaiveSpatialJoin
from utils import Utils

def clear_screen():
    """Καθαρισμός οθόνης."""
    os.system('cls' if os.name == 'nt' else 'clear')

def pause():
    """Περιμένει από τον χρήστη να πατήσει Enter."""
    input("\nΠάτα Enter για να συνεχίσεις...")

def save_results(results, algorithm_name):
    """Αποθηκεύει τα αποτελέσματα σε αρχείο .txt αν ο χρήστης το επιθυμεί."""
    if not results:
        print(f"Δεν υπάρχουν αποτελέσματα για αποθήκευση στον {algorithm_name} Spatial Join.")
        return

    save_option = input(f"\nΘέλεις να αποθηκεύσεις τα αποτελέσματα του {algorithm_name} Spatial Join σε αρχείο .txt; (ναι/όχι): ").strip().lower()
    if save_option in ['ναι', 'yes']:
        filename = input("Δώσε το όνομα του αρχείου (π.χ., results_kNN.txt): ").strip()
        if not filename.endswith('.txt'):
            filename += '.txt'
        try:
            with open(filename, 'w') as f:
                # Γράψε μια επικεφαλίδα για καλύτερη κατανόηση
                if algorithm_name in ['PBSM', 'Naive']:
                    f.write("Dataset_A_ID\tDataset_B_ID\n")  # Για Spatial Joins
                elif algorithm_name in ['k-NN', 'Linear Scan']:
                    f.write("Dataset_ID\tDistance\n")  # Για k-NN και Linear Scan k-NN
                # Προσθέστε περισσότερες επικεφαλίδες αν χρειάζεται

                for pair in results:
                    if algorithm_name in ['PBSM', 'Naive']:
                        a, b = pair
                        f.write(f"{a}\t{b}\n")  # Αποθήκευση με tab ως διαχωριστή
                    elif algorithm_name in ['k-NN', 'Linear Scan']:
                        dist, obj = pair
                        f.write(f"{obj.id}\t{dist:.4f}\n")  # Αποθήκευση ID και απόστασης
            print(f"Τα αποτελέσματα αποθηκεύτηκαν επιτυχώς στο αρχείο '{filename}'.")
        except Exception as e:
            print(f"Σφάλμα κατά την αποθήκευση του αρχείου: {e}")
    else:
        print("Τα αποτελέσματα δεν αποθηκεύτηκαν.")

def main_menu():
    clear_screen()
    print("\n=== Μενού Επιλογών ===")
    print("1. Δημιουργία Αρχείου Δεδομένων")
    print("2. Εκτέλεση Linear Scan (Γραμμική Σάρωση)")
    print("3. Εκτέλεση k-NN Αναζήτησης με Grid")
    print("4. Εκτέλεση Spatial Join με PBSM")
    print("5. Εκτέλεση Naive Spatial Join")
    print("6. Έξοδος")
    print("=======================")

def create_data_file(grid):
    """Δημιουργία αρχείου δεδομένων."""
    clear_screen()
    filename = input("Δώσε όνομα αρχείου για το dataset (π.χ., data1.csv): ").strip()
    if not filename:
        print("Το όνομα αρχείου δεν μπορεί να είναι κενό.")
        pause()
        return
    try:
        num_rectangles = int(input("Δώσε τον αριθμό ορθογωνίων που θέλεις να δημιουργήσεις: "))
    except ValueError:
        print("Μη έγκυρος αριθμός. Παρακαλώ εισήγαγε έναν ακέραιο.")
        pause()
        return
    try:
        # Ζητάμε από τον χρήστη να καθορίσει σε ποιο σύνολο θα ανήκει το dataset (A ή B)
        dataset_label = input("Δώσε το label του dataset (A ή B): ").strip().upper()
        if dataset_label not in ['A', 'B']:
            print("Μη έγκυρο label. Χρησιμοποίησε 'A' ή 'B'.")
            pause()
            return
        generator = PointGeneratorUnif(filename, grid.xL, grid.yL, grid.xU, grid.yU)
        generator.generate_rectangles(num_rectangles, include_id=True, dataset_label=dataset_label)
    except Exception as e:
        print(f"Σφάλμα κατά τη δημιουργία των ορθογωνίων: {e}")
        pause()
        return
    print(f"Το αρχείο '{filename}' δημιουργήθηκε με {num_rectangles} ορθογωνία εντός του Grid.")
    pause()

def execute_linear_scan():
    """Εκτέλεση Linear Scan k-NN."""
    clear_screen()
    filename = input("Δώσε το όνομα αρχείου δεδομένων (π.χ., data1.csv): ").strip()
    if not os.path.exists(filename):
        print(f"Το αρχείο '{filename}' δεν υπάρχει. Δημιουργήστε το πρώτα.")
        pause()
        return
    ls = LinearScan(filename)
    try:
        qx = float(input("Δώσε x-συντεταγμένη για το σημείο αναζήτησης: "))
        qy = float(input("Δώσε y-συντεταγμένη για το σημείο αναζήτησης: "))
        k = int(input("Δώσε τον αριθμό k για τους κοντινότερους γείτονες: "))
    except ValueError:
        print("Μη έγκυρες τιμές εισόδου. Παρακαλώ εισήγαγε αριθμούς.")
        pause()
        return
    results = ls.knn(qx, qy, k)
    print(f"\nΒρέθηκαν {len(results)} κοντινότεροι γείτονες (Linear Scan):")
    for dist, obj in results:
        print(f"{obj} με απόσταση {dist:.4f}")
    # Πρόσθεση της δυνατότητας αποθήκευσης
    save_results(results, "Linear Scan")
    pause()

def knn_with_grid(grid):
    """Εκτέλεση k-NN με χρήση Grid."""
    clear_screen()
    filename = input("Δώσε το όνομα αρχείου δεδομένων για τον k-NN αλγόριθμο (π.χ., data1.csv): ").strip()
    if not os.path.exists(filename):
        print(f"Το αρχείο '{filename}' δεν υπάρχει. Δημιουργήστε το πρώτα.")
        pause()
        return
    try:
        qx = float(input("Δώσε x-συντεταγμένη για το σημείο αναζήτησης: "))
        qy = float(input("Δώσε y-συντεταγμένη για το σημείο αναζήτησης: "))
        k = int(input("Δώσε τον αριθμό k για τους κοντινότερους γείτονες: "))
    except ValueError:
        print("Μη έγκυρες τιμές εισόδου. Παρακαλώ εισήγαγε αριθμούς.")
        pause()
        return
    # Φόρτωση του dataset στον Grid ως 'single'
    grid.load(filename, dataset_label='single')
    results = kNN.knn(grid, qx, qy, k)
    print(f"\nΒρέθηκαν {len(results)} κοντινότεροι γείτονες (Grid k-NN):")
    for dist, res in results:
        print(f"{res} με απόσταση {dist:.4f}")
    # Πρόσθεση της δυνατότητας αποθήκευσης
    save_results(results, "k-NN")
    pause()

def execute_spatial_join_pbsm(grid):
    """Εκτέλεση Spatial Join με PBSM."""
    clear_screen()
    print("Θα χρειαστεί να καθορίσεις δύο datasets για τον Spatial Join με PBSM.")
    filename_A = input("Δώσε το όνομα αρχείου δεδομένων για το σύνολο A (π.χ., dataA.csv): ").strip()
    filename_B = input("Δώσε το όνομα αρχείου δεδομένων για το σύνολο B (π.χ., dataB.csv): ").strip()
    if not os.path.exists(filename_A):
        print(f"Το αρχείο '{filename_A}' δεν υπάρχει. Δημιουργήστε το πρώτα.")
        pause()
        return
    if not os.path.exists(filename_B):
        print(f"Το αρχείο '{filename_B}' δεν υπάρχει. Δημιουργήστε το πρώτα.")
        pause()
        return
    grid.load(filename_A, dataset_label='A')
    grid.load(filename_B, dataset_label='B')
    print("Εκτέλεση Spatial Join με PBSM...")
    pbsmsj = SpatialJoinPBSM(grid)
    pbsmsj_results = pbsmsj.execute_join()
    print(f"Αποτελέσματα PBSM: {len(pbsmsj_results)} ζεύγη.")

    # Πρόσθεση της δυνατότητας αποθήκευσης
    save_results(pbsmsj_results, "PBSM")
    
    pause()

def execute_naive_spatial_join(grid):
    """Εκτέλεση Naive Spatial Join."""
    clear_screen()
    print("Θα χρειαστεί να καθορίσεις δύο datasets για τον Naive Spatial Join.")
    filename_A = input("Δώσε το όνομα αρχείου δεδομένων για το σύνολο A (π.χ., dataA.csv): ").strip()
    filename_B = input("Δώσε το όνομα αρχείου δεδομένων για το σύνολο B (π.χ., dataB.csv): ").strip()
    if not os.path.exists(filename_A):
        print(f"Το αρχείο '{filename_A}' δεν υπάρχει. Δημιουργήστε το πρώτα.")
        pause()
        return
    if not os.path.exists(filename_B):
        print(f"Το αρχείο '{filename_B}' δεν υπάρχει. Δημιουργήστε το πρώτα.")
        pause()
        return
    grid.load(filename_A, dataset_label='A')
    grid.load(filename_B, dataset_label='B')
    print("Εκτέλεση Naive Spatial Join...")
    naive_sj = NaiveSpatialJoin(grid.get_dataset('A'), grid.get_dataset('B'))
    naive_sj_results = naive_sj.execute_join()
    print(f"Αποτελέσματα Naive: {len(naive_sj_results)} ζεύγη.")

    # Πρόσθεση της δυνατότητας αποθήκευσης
    save_results(naive_sj_results, "Naive")
    
    pause()

def main():
    """Κύρια λειτουργία του προγράμματος."""
    # Καθορισμός σταθερών ορίων για το grid
    grid = Grid(0, 0, 100, 100, 10)  # Δημιουργία Grid με τα όρια που θέλουμε

    while True:
        main_menu()
        choice = input("Δώσε την επιλογή σου: ").strip()
        if choice == "1":
            create_data_file(grid)  # Δημιουργία δεδομένων χωρίς ανάθεση σε σύνολο
        elif choice == "2":
            execute_linear_scan()
        elif choice == "3":
            knn_with_grid(grid)
        elif choice == "4":
            execute_spatial_join_pbsm(grid)
        elif choice == "5":
            execute_naive_spatial_join(grid)
        elif choice == "6":
            print("Έξοδος από το πρόγραμμα.")
            break
        else:
            print("Μη έγκυρη επιλογή. Προσπαθήστε ξανά.")
            pause()

if __name__ == "__main__":
    main()