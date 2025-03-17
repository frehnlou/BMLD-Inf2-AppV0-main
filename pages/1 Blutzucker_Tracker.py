import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo
from utils.data_manager import DataManager
from utils.login_manager import LoginManager  # 🔐 Login-Manager hinzufügen
import pandas as pd

# ✅ `st.set_page_config` MUSS als erstes Streamlit-Kommando stehen!
st.set_page_config(page_title="Blutzucker Tracker", layout="wide")

# ====== Start Login Block ======
login_manager = LoginManager()
login_manager.go_to_login('Start.py') 
# ====== End Login Block ======

# Initialisierung des Data Managers
data_manager = DataManager(fs_protocol='webdav', fs_root_folder="BMLD_cblsf_App")

# Abstand nach oben für bessere Platzierung
st.markdown("<br>", unsafe_allow_html=True)

# Navigation über vier Spalten
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

def blutzucker_tracker():
    st.markdown("## 🩸 Blutzucker-Tracker")

    # Nutzername aus Session holen
    username = st.session_state.get("username", "Gast")

    with st.form(key='blutzucker_form'):
        blutzuckerwert = st.number_input("Gib deinen Blutzuckerwert ein", min_value=0, step=1)
        zeitpunkt = st.selectbox("Zeitpunkt", ["Nüchtern", "Nach dem Essen"])
        submit_button = st.form_submit_button(label='Eintrag hinzufügen')

    # Datenbank für den Nutzer laden
    user_data = data_manager.load_user_data(
        session_state_key="user_data",
        file_name="data.csv",
        parse_dates=["datum_zeit"]
    )

    if submit_button:
        datum_zeit = datetime.now(ZoneInfo("Europe/Zurich")).strftime("%d.%m.%Y %H:%M:%S")
        result = {
            "username": username,  # Nutzername speichern
            "blutzuckerwert": blutzuckerwert,
            "zeitpunkt": zeitpunkt,
            "datum_zeit": datum_zeit
        }

        # 🔥 Daten speichern
        data_manager.append_record("data.csv", result)
        st.success("Eintrag erfolgreich hinzugefügt")
        st.rerun()

    # 🔹 Tabelle mit gespeicherten Blutzuckerwerten des eingeloggten Nutzers anzeigen
    if not user_data.empty:
        st.markdown("### Gespeicherte Blutzuckerwerte")
        st.table(user_data[["datum_zeit", "blutzuckerwert", "zeitpunkt"]])

        # Durchschnitt berechnen
        durchschnitt = user_data["blutzuckerwert"].mean()
        st.markdown(f"**Durchschnittlicher Blutzuckerwert:** {durchschnitt:.2f} mg/dL")

        # Löschoption
        st.markdown("### Eintrag löschen")
        with st.form(key='delete_form'):
            index_to_delete = st.number_input(
                "Index des zu löschenden Eintrags", 
                min_value=1, 
                max_value=len(user_data), 
                step=1
            )
            delete_button = st.form_submit_button(label='Eintrag löschen')

        if delete_button:
            user_data = user_data.drop(user_data.index[index_to_delete - 1])
            data_manager.save_user_data("data.csv", user_data)  # 🔥 Geänderte Daten speichern
            st.success("Eintrag erfolgreich gelöscht")
            st.rerun()

# 🔄 Seite dynamisch wechseln
if "seite" not in st.session_state:
    st.session_state.seite = "Blutzucker-Tracker"

if st.session_state.seite == "Blutzucker-Tracker":
    blutzucker_tracker()
elif st.session_state.seite == "Startseite":
    from Start import startseite
    startseite()
elif st.session_state.seite == "Blutzucker-Werte":
    from pages import Blutzucker_Werte
    Blutzucker_Werte.blutzucker_werte()
elif st.session_state.seite == "Blutzucker-Grafik":
    from pages import Blutzucker_Grafik
    Blutzucker_Grafik.blutzucker_grafik()