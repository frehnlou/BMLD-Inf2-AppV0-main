import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd
from utils.data_manager import DataManager
from utils.login_manager import LoginManager

# ✅ MUSS als erstes stehen
st.set_page_config(page_title="Blutzucker Tracker", layout="wide")

# ====== Login-Check ======
data_manager = DataManager(fs_protocol='webdav', fs_root_folder="BMLD_cblsf_App")
login_manager = LoginManager(data_manager)
login_manager.go_to_login('Start.py')

# 🔹 Navigation
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🏠 Startseite"):
        st.session_state.seite = "Startseite"

with col2:
    if st.button("🩸 Blutzucker-Tracker"):
        st.session_state.seite = "Blutzucker-Tracker"

with col3:
    if st.button("📋 Blutzucker-Werte"):
        st.session_state.seite = "Blutzucker-Werte"

with col4:
    if st.button("📊 Blutzucker-Grafik"):
        st.session_state.seite = "Blutzucker-Grafik"

# 📌 Nutzername holen
username = st.session_state.get("username", "Gast")

# 📌 Daten laden
user_data = data_manager.load_user_data(
    session_state_key="user_data",
    file_name="data.csv",
    initial_value=pd.DataFrame(columns=["username", "datum_zeit", "blutzuckerwert", "zeitpunkt"]),
    parse_dates=["datum_zeit"]
)

# 🔥 Startseite
def startseite():
    st.markdown("## 🏠 Willkommen auf der Startseite!")
    st.write("""
    Liebe Diabetikerinnen und Diabetiker! 🩸

    Mit diesem Blutzucker-Tracker kannst du deine Werte einfach eingeben, speichern und analysieren – alles an einem Ort!  
    """)

    st.markdown("""
    **✅ Funktionen:**  
    - ✏️ **Eingabe deiner Blutzuckerwerte (mg/dL)**  
    - ⏰ **Messzeitpunkt wählen:** (Nüchtern oder nach dem Essen)  
    - 📋 **Übersichtliche Tabelle mit all deinen Werten**  
    - 📊 **Grafische Auswertung zur besseren Analyse**  
    """)

# 🔥 Blutzucker-Tracker
def blutzucker_tracker():
    st.markdown("## 🩸 Blutzucker-Tracker")

    with st.form(key='blutzucker_form'):
        blutzuckerwert = st.number_input("Blutzuckerwert (mg/dL)", min_value=0, step=1)
        zeitpunkt = st.selectbox("Zeitpunkt", ["Nüchtern", "Nach dem Essen"])
        submit_button = st.form_submit_button(label='Eintrag hinzufügen')

    if submit_button:
        datum_zeit = datetime.now(ZoneInfo("Europe/Zurich")).strftime("%Y-%m-%d %H:%M:%S")
        result = {
            "username": username,
            "blutzuckerwert": blutzuckerwert,
            "zeitpunkt": zeitpunkt,
            "datum_zeit": datum_zeit
        }
        data_manager.append_record("data.csv", result)
        st.success("✅ Eintrag hinzugefügt!")
        st.rerun()

    # 📌 Daten filtern NUR für den aktuellen Benutzer
    user_data_filtered = user_data[user_data["username"] == username]

    if not user_data_filtered.empty:
        st.markdown("### 🔢 Gespeicherte Blutzuckerwerte")
        st.table(user_data_filtered[["datum_zeit", "blutzuckerwert", "zeitpunkt"]])

        durchschnitt = user_data_filtered["blutzuckerwert"].mean()
        st.markdown(f"📊 **Durchschnittlicher Wert:** `{durchschnitt:.2f} mg/dL`")
    else:
        st.warning("⚠️ Noch keine Daten vorhanden.")

# 🔥 Blutzucker-Werte
def blutzucker_werte():
    st.markdown("## 📋 Blutzucker-Werte")

    user_data_filtered = user_data[user_data["username"] == username]

    if not user_data_filtered.empty:
        st.markdown("### 📄 Gespeicherte Blutzuckerwerte")
        st.table(user_data_filtered[["datum_zeit", "blutzuckerwert", "zeitpunkt"]])
    else:
        st.warning("⚠️ Noch keine Werte gespeichert.")

# 🔥 Blutzucker-Grafik
def blutzucker_grafik():
    st.markdown("## 📊 Blutzucker-Grafik")

    user_data_filtered = user_data[user_data["username"] == username]

    if not user_data_filtered.empty:
        st.markdown("### 📈 Verlauf der Blutzuckerwerte")
        chart_data = user_data_filtered.set_index("datum_zeit")[["blutzuckerwert"]]
        st.line_chart(chart_data)
    else:
        st.warning("⚠️ Noch keine Werte vorhanden.")

# 🔄 Seitenwechsel OHNE `st.switch_page()`
if "seite" not in st.session_state:
    st.session_state.seite = "Startseite"

if st.session_state.seite == "Blutzucker-Tracker":
    blutzucker_tracker()
elif st.session_state.seite == "Startseite":
    startseite()
elif st.session_state.seite == "Blutzucker-Werte":
    blutzucker_werte()
elif st.session_state.seite == "Blutzucker-Grafik":
    blutzucker_grafik()
