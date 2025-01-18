# main.py

import streamlit as st
import os
import pandas as pd
import statistics
import io

from pointGeneratorUnif import PointGeneratorUnif
from grid import Grid
from kNN import kNN  # kNN.knn() -> (results, stats_str)
from linearScan import LinearScan  # ls.knn() -> (results, stats_str)
from spatialJoinPBSM import SpatialJoinPBSM  # pbsmsj.execute_join() -> (results, stats_str)
from naiveSpatialJoin import NaiveSpatialJoin  # naive_sj.execute_join() -> (results, stats_str)
from skyline_query import SkylineQuery  # sq.sky_query() -> (results, sky_stats)

import folium
from streamlit_folium import st_folium


def save_results(results, algorithm_name, stats=None):
    """
    Αποθηκεύει τα αποτελέσματα ενός αλγορίθμου (π.χ. k-NN, PBSM, Naive Spatial Join, Skyline)
    μαζί με τυχόν στατιστικά σε ένα αρχείο .txt, το οποίο προσφέρεται για download
    μέσω Streamlit. Χρησιμοποιεί in-memory StringIO, ώστε να μη δημιουργεί φυσικό αρχείο
    στον δίσκο.

    :param results: Τα αποτελέσματα προς αποθήκευση (λίστα).
    :param algorithm_name: Το όνομα του αλγορίθμου (string).
    :param stats: (Προαιρετικά) μια συμβολοσειρά που περιέχει στατιστικά στοιχεία (χρόνος, checks κλπ.).
    """
    if not results:
        st.warning(f"Δεν υπάρχουν αποτελέσματα για αποθήκευση στον {algorithm_name}.")
        return

    st.info(f"Αποθήκευση αποτελεσμάτων {algorithm_name} σε τοπικό αρχείο (.txt):")

    output = io.StringIO()

    # 1. Αν υπάρχουν στατιστικά, τα γράφουμε πρώτα
    if stats:
        output.write(stats)
        output.write("\n")

    # 2. Γράφουμε επικεφαλίδες
    if algorithm_name in ['PBSM', 'Naive']:
        output.write("Dataset_A_ID\tDataset_B_ID\n")
    elif algorithm_name in ['k-NN', 'Linear Scan']:
        output.write("Dataset_ID\tDistance\n")
    elif algorithm_name == 'Skyline':
        output.write("Skyline Points (ID, xmin, ymin, xmax, ymax):\n")

    # 3. Γράφουμε τα αποτελέσματα γραμμή-γραμμή
    for pair in results:
        if algorithm_name in ['PBSM', 'Naive']:
            a, b = pair
            output.write(f"{a.id}\t{b.id}\n")
        elif algorithm_name in ['k-NN', 'Linear Scan']:
            dist, obj = pair
            output.write(f"{obj.id}\t{dist:.4f}\n")
        elif algorithm_name == 'Skyline':
            obj = pair
            output.write(f"{obj.id}, {obj.xmin}, {obj.ymin}, {obj.xmax}, {obj.ymax}\n")

    data_str = output.getvalue()
    output.close()

    default_filename = f"results_{algorithm_name}.txt"

    st.download_button(
        label="Κατέβασε το αρχείο αποτελεσμάτων",
        data=data_str,
        file_name=default_filename,
        mime="text/plain"
    )


def display_map(all_points, skyline_points=None):
    """
    Δημιουργεί κι εμφανίζει έναν διαδραστικό χάρτη Folium μέσα σε Streamlit,
    επιτρέποντας οπτικοποίηση των MBR points και (προαιρετικά) των Skyline points
    σε διαφορετικό χρώμα.

    :param all_points: Λίστα με σημεία (MBRs) που εμφανίζονται ως μπλε markers.
    :param skyline_points: (Προαιρετικά) λίστα με Skyline points, που εμφανίζονται κόκκινα.
    """
    if not all_points:
        st.info("Δεν υπάρχουν δεδομένα για εμφάνιση στον χάρτη.")
        return

    lats = [p.ymin for p in all_points]
    lons = [p.xmin for p in all_points]
    center_lat = statistics.mean(lats)
    center_lon = statistics.mean(lons)

    folium_map = folium.Map(location=[center_lat, center_lon], zoom_start=12)

    # Μπλε markers = all_points
    for p in all_points:
        lat = p.ymin
        lon = p.xmin
        popup_text = f"ID: {p.id}"
        folium.Marker(
            [lat, lon],
            popup=popup_text,
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(folium_map)

    # Κόκκινα markers = skyline_points
    if skyline_points:
        for sp in skyline_points:
            lat = sp.ymin
            lon = sp.xmin
            popup_text = f"Skyline ID: {sp.id}"
            folium.Marker(
                [lat, lon],
                popup=popup_text,
                icon=folium.Icon(color='red', icon='star')
            ).add_to(folium_map)

    st_folium(folium_map, width=700, height=500)


def main():
    """
    Κύρια συνάρτηση εκτέλεσης της εφαρμογής σε Streamlit. Δημιουργεί ένα μενού,
    επιτρέπει τη ρύθμιση των ορίων του Grid, και προσφέρει επιλογές εκτέλεσης
    διαφόρων αλγορίθμων (π.χ. Linear Scan, k-NN, PBSM, Naive Join, Skyline).

    Χρησιμοποιεί sessions (st.session_state) για να διατηρεί το Grid μεταξύ των
    διαφορετικών επιλογών του χρήστη. 
    """
    st.title("Interactive Grid Search for Spatial Data")
    st.write("""
    Καλώς ήρθατε στην εφαρμογή μας για χωρική επεξεργασία δεδομένων!
    
    **Τι κάνει η εφαρμογή**:
    - Παρέχει ένα Grid (διαμέριση του χώρου) όπου μπορούμε να φορτώσουμε 
      και να επεξεργαστούμε δεδομένα MBR (ορθογωνίων).
    - Προσφέρει διάφορους αλγορίθμους/επιλογές:
      1) **Δημιουργία Αρχείου Δεδομένων** (PointGeneratorUnif): Δημιουργεί τυχαία ορθογώνια σε CSV.
      2) **Linear Scan (k-NN)**: Γραμμική σάρωση για εύρεση k κοντινότερων γειτόνων.
      3) **k-NN με Grid**: Χρησιμοποιεί το Grid για πιο αποδοτική εύρεση k-NN.
      4) **Spatial Join PBSM**: Ελέγχει τομή μεταξύ συνόλων A,B μέσω Partition Based Spatial Merge.
      5) **Naive Spatial Join**: Αφελής προσέγγιση για Join, εξετάζοντας κάθε ζεύγος (A,B).
      6) **Skyline Query με Grid**: Βρίσκει αντικείμενα που δεν κυριαρχούνται από κανένα άλλο.
    
    Σε κάθε επιλογή μπορούμε να **φορτώσουμε** ή **δημιουργήσουμε** datasets,
    να πάρουμε **αποτελέσματα** και **στατιστικά**, και προαιρετικά 
    να τα **κατεβάσουμε** ή να τα **προβάλουμε** πάνω σε διαδραστικό χάρτη (Folium).
    """)

    # -- Δημιουργία / επιλογή του Grid --
    with st.sidebar:
        st.header("Grid Settings")
        xL = st.number_input("xL", value=0.0)
        yL = st.number_input("yL", value=0.0)
        xU = st.number_input("xU", value=100.0)
        yU = st.number_input("yU", value=100.0)
        m = st.number_input("m (διαμερίσεις)", min_value=1, value=10)
        if st.button("Create/Reset Grid"):
            st.session_state["grid"] = Grid(xL, yL, xU, yU, m)
            st.success(f"Δημιουργήθηκε νέο Grid με m={m} [{xL},{yL}] - [{xU},{yU}]")

    # Αν δεν έχει οριστεί Grid στο session_state, δημιουργούμε ένα default
    if "grid" not in st.session_state:
        st.session_state["grid"] = Grid(0, 0, 100, 100, 10)

    grid = st.session_state["grid"]

    st.write("## Επιλογές Ενεργειών")
    menu = [
        "1. Δημιουργία Αρχείου Δεδομένων (PointGeneratorUnif)",
        "2. Εκτέλεση Linear Scan (Γραμμική Σάρωση)",
        "3. Εκτέλεση k-NN Αναζήτησης με Grid",
        "4. Εκτέλεση Spatial Join με PBSM",
        "5. Εκτέλεση Naive Spatial Join",
        "6. Εκτέλεση Skyline Query με Grid"
    ]
    choice = st.selectbox("Επίλεξε ενέργεια:", menu)

    # ------------------------------------
    # 1. Δημιουργία Αρχείου Δεδομένων
    # ------------------------------------
    if choice == menu[0]:
        st.subheader("Δημιουργία Αρχείου Δεδομένων (CSV)")
        filename = st.text_input("Δώσε όνομα CSV (π.χ. data1.csv):", value="data1.csv")
        num_rect = st.number_input("Αριθμός ορθογωνίων:", min_value=1, value=10)
        dataset_label = st.selectbox("Label dataset", ["A", "B", "default"])
        max_width = st.number_input("Μέγιστο πλάτος", min_value=0.0, value=1.0)
        max_height = st.number_input("Μέγιστο ύψος", min_value=0.0, value=1.0)

        if st.button("Δημιουργία & Λήψη"):
            # 1. Φτιάχνουμε generator όπως πριν, (μπορείς να αγνοήσεις το self.filename αν δε το χρησιμοποιείς)
            generator = PointGeneratorUnif(
                filename="ignored.csv",  # ή απλά κάτι placeholder
                xL=grid.xL, yL=grid.yL,
                xU=grid.xU, yU=grid.yU
            )

            try:
                # 2. Παίρνουμε το CSV σαν string από την in_memory μέθοδο
                csv_data = generator.generate_rectangles_in_memory(
                    n=num_rect,
                    include_id=True,
                    dataset_label=dataset_label,
                    max_width=max_width,
                    max_height=max_height
                )

                # 3. Ενημερώνουμε το χρήστη
                st.success(f"Δημιουργήθηκαν {num_rect} ορθογώνια σε CSV μορφή in-memory.")

                # 4. Δίνουμε κουμπί download
                st.download_button(
                    label="Κατέβασε το CSV",
                    data=csv_data,
                    file_name=filename,   # π.χ. "data1.csv"
                    mime="text/csv"
                )

            except Exception as e:
                st.error(f"Σφάλμα κατά τη δημιουργία του CSV: {e}")


    # ------------------------------------
    # 2. Linear Scan
    # ------------------------------------
    elif choice == menu[1]:
        st.subheader("Εκτέλεση Linear Scan k-NN")
        uploaded_file = st.file_uploader("Φόρτωσε CSV (ID,xmin,ymin,xmax,ymax)", type="csv")
        if uploaded_file:
            temp_file = "temp_linear.csv"
            with open(temp_file, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"Το αρχείο ανέβηκε ως {temp_file}.")

            qx = st.number_input("x (query)", value=10.0)
            qy = st.number_input("y (query)", value=10.0)
            k = st.number_input("k (κοντινότεροι γείτονες)", min_value=1, value=3)

            if st.button("Εκτέλεση Linear Scan"):
                try:
                    ls = LinearScan(temp_file)
                    results, lscan_stats = ls.knn(qx, qy, k)

                    st.write(f"Βρέθηκαν {len(results)} κοντινότεροι γείτονες:")
                    st.write(lscan_stats)

                    for dist, obj in results:
                        st.write(f"{obj} - dist={dist:.4f}")

                    save_results(results, "Linear Scan", stats=lscan_stats)

                finally:
                    try:
                        os.remove(temp_file)
                        st.info(f"Διαγράφηκε προσωρινό αρχείο '{temp_file}'.")
                    except FileNotFoundError:
                        pass
        else:
            st.info("Φόρτωσε ένα CSV για να κάνουμε Linear Scan.")

    # ------------------------------------
    # 3. k-NN με Grid
    # ------------------------------------
    elif choice == menu[2]:
        st.subheader("Εκτέλεση k-NN με Grid")
        uploaded_file = st.file_uploader("Φόρτωσε CSV (ID,xmin,ymin,xmax,ymax) για Grid", type="csv")

        if uploaded_file:
            temp_file = "temp_knn.csv"
            with open(temp_file, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"Το αρχείο ανέβηκε ως {temp_file}.")

            qx = st.number_input("x (query)", value=10.0)
            qy = st.number_input("y (query)", value=10.0)
            k = st.number_input("k γείτονες:", min_value=1, value=3)

            if st.button("Φόρτωση + k-NN"):
                try:
                    grid.load(temp_file, dataset_label="default")
                    st.success("Το dataset φορτώθηκε στο Grid (default).")

                    results, knn_stats = kNN.knn(grid, qx, qy, k)

                    st.write(f"Βρέθηκαν {len(results)} γείτονες:")
                    st.write(knn_stats)

                    for dist, obj in results:
                        st.write(f"{obj} - dist={dist:.4f}")

                    save_results(results, "k-NN", stats=knn_stats)

                finally:
                    try:
                        os.remove(temp_file)
                        st.info(f"Διαγράφηκε προσωρινό αρχείο '{temp_file}'.")
                    except FileNotFoundError:
                        pass
        else:
            st.info("Φόρτωσε CSV για k-NN με Grid.")

    # ------------------------------------
    # 4. Spatial Join PBSM
    # ------------------------------------
    elif choice == menu[3]:
        st.subheader("Εκτέλεση Spatial Join PBSM")
        fileA = st.file_uploader("CSV για σύνολο A", type="csv", key="pbsmA")
        fileB = st.file_uploader("CSV για σύνολο B", type="csv", key="pbsmB")

        if fileA and fileB:
            tempA = "temp_pbsmA.csv"
            tempB = "temp_pbsmB.csv"
            with open(tempA, "wb") as f:
                f.write(fileA.getbuffer())
            with open(tempB, "wb") as f:
                f.write(fileB.getbuffer())
            st.success("Αρχεία A,B φορτώθηκαν προσωρινά.")

            if st.button("Φόρτωση + PBSM"):
                try:
                    grid.load(tempA, dataset_label='A')
                    grid.load(tempB, dataset_label='B')
                    pbsmsj = SpatialJoinPBSM(grid)
                    results, pbsm_stats = pbsmsj.execute_join()

                    st.write(f"Αποτελέσματα PBSM: {len(results)} ζεύγη.")
                    st.write(pbsm_stats)

                    save_results(results, "PBSM", stats=pbsm_stats)
                finally:
                    for tmp in [tempA, tempB]:
                        try:
                            os.remove(tmp)
                            st.info(f"Διαγράφηκε προσωρινό αρχείο '{tmp}'.")
                        except FileNotFoundError:
                            pass
        else:
            st.info("Παρακαλώ φόρτωσε 2 αρχεία (A,B) για PBSM.")

    # ------------------------------------
    # 5. Naive Spatial Join
    # ------------------------------------
    elif choice == menu[4]:
        st.subheader("Naive Spatial Join")
        fileA = st.file_uploader("CSV για σύνολο A", type="csv", key="naiveA")
        fileB = st.file_uploader("CSV για σύνολο B", type="csv", key="naiveB")

        if fileA and fileB:
            tempA = "temp_naiveA.csv"
            tempB = "temp_naiveB.csv"
            with open(tempA, "wb") as f:
                f.write(fileA.getbuffer())
            with open(tempB, "wb") as f:
                f.write(fileB.getbuffer())
            st.success("Αρχεία A,B φορτώθηκαν προσωρινά.")

            if st.button("Φόρτωση + Naive Join"):
                try:
                    grid.load(tempA, 'A')
                    grid.load(tempB, 'B')
                    naive_sj = NaiveSpatialJoin(grid.get_dataset('A'), grid.get_dataset('B'))
                    results, naive_stats = naive_sj.execute_join()

                    st.write(f"Naive αποτελέσματα: {len(results)}")
                    st.write(naive_stats)

                    save_results(results, "Naive", stats=naive_stats)

                finally:
                    for tmp in [tempA, tempB]:
                        try:
                            os.remove(tmp)
                            st.info(f"Διαγράφηκε προσωρινό αρχείο '{tmp}'.")
                        except FileNotFoundError:
                            pass
        else:
            st.info("Παρακαλώ φόρτωσε αρχεία για A,B.")

    # ------------------------------------
    # 6. Skyline Query
    # ------------------------------------
    elif choice == menu[5]:
        st.subheader("Skyline Query (Grid)")
        fileSky = st.file_uploader("CSV για Skyline", type="csv")

        if fileSky:
            temp_file = "temp_sky.csv"
            with open(temp_file, "wb") as f:
                f.write(fileSky.getbuffer())
            st.success(f"CSV φορτώθηκε προσωρινά ως {temp_file}")

            if st.button("Φόρτωση + Skyline"):
                try:
                    grid.load(temp_file, dataset_label='default')
                    sq = SkylineQuery(grid)
                    skyline_points, sky_stats = sq.sky_query()

                    st.write(f"Βρέθηκαν {len(skyline_points)} σημεία Skyline:")
                    st.write(sky_stats)

                    for sp in skyline_points:
                        st.write(str(sp))

                    save_results(skyline_points, "Skyline", stats=sky_stats)

                    # Αποθήκευση αντικειμένων για πιθανή προβολή σε χάρτη
                    df = pd.read_csv(temp_file)
                    pseudo_list = []
                    for idx, row in df.iterrows():
                        class PseudoObj:
                            def __init__(self, id, xmin, ymin, xmax, ymax):
                                self.id = id
                                self.xmin = float(xmin)
                                self.ymin = float(ymin)
                                self.xmax = float(xmax)
                                self.ymax = float(ymax)
                        p = PseudoObj(row["ID"], row["xmin"], row["ymin"], row["xmax"], row["ymax"])
                        pseudo_list.append(p)

                    st.session_state["skyline_all_points"] = pseudo_list
                    st.session_state["skyline_points"] = skyline_points

                finally:
                    try:
                        os.remove(temp_file)
                        st.info(f"Διαγράφηκε προσωρινό αρχείο '{temp_file}'.")
                    except FileNotFoundError:
                        pass
        else:
            st.info("Φόρτωσε ένα CSV για Skyline.")

        show_map = st.checkbox("Προβολή σε χάρτη")
        if show_map:
            if "skyline_all_points" in st.session_state and "skyline_points" in st.session_state:
                display_map(st.session_state["skyline_all_points"], st.session_state["skyline_points"])
            else:
                st.warning("Δεν υπάρχουν δεδομένα για εμφάνιση σε χάρτη.")


if __name__ == "__main__":
    main()
