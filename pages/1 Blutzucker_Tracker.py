import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo
from utils.data_manager import DataManager
from utils.login_manager import LoginManager
import pandas as pd

# ✅ MUSS erstes Streamlit-Kommando bleiben!
st.set_page_config(page_title="Blutzucker Tracker", layout="wide")

# ====== Start Login Block ======
login_manager = LoginManager()
login_manager.go_to_login('Start.py') 
# ====== End Login Block ======

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

# Nutzername holen
username = st.session_state.get("username", "Gast")

# DataManager initialisieren
data_manager = DataManager(fs_protocol='webdav', fs_root_folder="BMLD_cblsf_App")

# Seiten-Funktionen definieren
def startseite():
    st.markdown("## 🏠 Willkommen auf der Startseite!")
    st.write("""
    Liebe Diabetikerinnen und Diabetiker!🩸

    Kennst du das Problem, den Überblick über deine Blutzuckerwerte zu behalten? Mit unserem Blutzucker-Tracker kannst du deine Werte einfach eingeben, speichern und analysieren – alles an einem Ort!

    ✔ Kein lästiges Papier-Tagebuch mehr

    ✔ Verfolge deine Werte langfristig & erkenne Muster

    ✔ Bessere Kontrolle für ein gesünderes Leben mit Diabetes

    Einfach testen & deine Blutzuckerwerte im Blick behalten! 🏅
    """)

def blutzucker_tracker():
    st.markdown("## 🩸 Blutzucker-Tracker")

    with st.form(key='blutzucker_form'):
        blutzuckerwert = st.number_input("Blutzuckerwert (mg/dL)", min_value=0, step=1)
        zeitpunkt = st.selectbox("Zeitpunkt", ["Nüchtern", "Nach dem Essen"])
        submit_button = st.form_submit_button(label='Eintrag hinzufügen')

    user_data = data_manager.load_user_data(
        session_state_key="user_data",
        file_name="data.csv",
        initial_value=pd.DataFrame(columns=["username", "datum_zeit", "blutzuckerwert", "zeitpunkt"]),
        parse_dates=["datum_zeit"]
    )

    if submit_button:
        datum_zeit = datetime.now(ZoneInfo("Europe/Zurich")).strftime("%d.%m.%Y %H:%M:%S")
        result = {
            "username": username,
            "blutzuckerwert": blutzuckerwert,
            "zeitpunkt": zeitpunkt,
            "datum_zeit": datum_zeit
        }
        data_manager.append_record("data.csv", result)
        st.success("Eintrag hinzugefügt!")
        st.rerun()

    if not user_data.empty:
        st.table(user_data[["datum_zeit", "blutzuckerwert", "zeitpunkt"]])
        durchschnitt = user_data["blutzuckerwert"].mean()
        st.write(f"Durchschnittlicher Wert: {durchschnitt:.2f} mg/dL")
    else:
        st.warning("Keine Daten vorhanden.")

def blutzucker_werte():
    st.markdown("## 📋 Blutzucker-Werte")
    user_data = data_manager.load_user_data(
        session_state_key="user_data",
        file_name="data.csv",
        initial_value=pd.DataFrame(),
        parse_dates=["datum_zeit"]
    )
    if not user_data.empty:
        st.table(user_data[["datum_zeit", "blutzuckerwert", "zeitpunkt"]])
    else:
        st.warning("Keine Daten vorhanden.")

def blutzucker_grafik():
    st.markdown("## 📊 Blutzucker-Grafik")
    user_data = data_manager.load_user_data(
        session_state_key="user_data",
        file_name="data.csv",
        parse_dates=["datum_zeit"]
    )

    if not user_data.empty:
        chart_data = user_data[["datum_zeit", "blutzuckerwert"]].set_index("datum_zeit")
        st.line_chart(blutzuckerwerte)
    else:
        st.warning("Keine Daten vorhanden.")

# Seiten dynamisch verwalten
if "seite" not in st.session_state:
    st.session_state.seite = "Startseite"

if st.session_state.seite == "Startseite":
    startseite()
elif st.session_state.seite == "Blutzucker-Tracker":
    blutzucker_tracker()
elif st.session_state.seite == "Blutzucker-Werte":
    blutzucker_werte()
elif st.session_state.seite == "Blutzucker-Grafik":
    blutzucker_grafik()
