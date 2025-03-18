import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd
from utils.data_manager import DataManager
from utils.login_manager import LoginManager

# Seitenkonfiguration
st.set_page_config(page_title="Blutzucker Tracker", layout="wide")

# ====== Login-Check ======
data_manager = DataManager(fs_protocol='webdav', fs_root_folder="BMLD_cblsf_App")
login_manager = LoginManager(data_manager)
login_manager.go_to_login('Start.py')

# Nutzername aus dem Session-State holen
username = st.session_state.get("username")

if not username:
    st.error("Kein Benutzer eingeloggt. Anmeldung erforderlich.")
    st.stop()

# Benutzerspezifische Daten laden
if "user_data" not in st.session_state:
    st.session_state.user_data = data_manager.load_user_data(
        session_state_key="user_data",
        username=username,
        initial_value=pd.DataFrame(columns=["datum_zeit", "blutzuckerwert", "zeitpunkt"]),
        parse_dates=["datum_zeit"]
    )

user_data = st.session_state.user_data

# ====== Navigation ======
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

# ====== Funktionen ======

def startseite():
    st.markdown("## 🏠 Willkommen auf der Startseite!")
    st.write("""
    Liebe Diabetikerinnen und Diabetiker 🩸,

    Mit unserem Blutzucker-Tracker kannst du deine Werte einfach eingeben, speichern und analysieren – alles an einem Ort!

    **Funktionen der App:**
    - Schnelle Eingabe deines Blutzuckers (mg/dL)
    - Messzeitpunkt wählen (Nüchtern, Nach dem Essen)
    - Automatische Übersicht in einer Tabelle
    - Anschauliche Diagramme zur Analyse deiner Werte

    Verfolge deine Werte langfristig und behalte die Kontrolle für ein gesünderes Leben mit Diabetes!
    """)

def blutzucker_tracker():
    st.markdown("## 🩸 Blutzucker-Tracker")

    with st.form(key='blutzucker_form'):
        blutzuckerwert = st.number_input("Blutzuckerwert (mg/dL)", min_value=0, step=1)
        zeitpunkt = st.selectbox("Zeitpunkt", ["Nüchtern", "Nach dem Essen"])
        submit_button = st.form_submit_button(label='Eintrag hinzufügen')

    if submit_button:
        datum_zeit = datetime.now(ZoneInfo("Europe/Zurich")).strftime("%Y-%m-%d %H:%M:%S")
        new_entry = pd.DataFrame([{
            "datum_zeit": datum_zeit,
            "blutzuckerwert": blutzuckerwert,
            "zeitpunkt": zeitpunkt
        }])
        st.session_state.user_data = pd.concat([st.session_state.user_data, new_entry], ignore_index=True)

        # Speichert die Werte nur für den aktuellen Benutzer
        data_manager.save_user_data("user_data", username)

        st.success("Eintrag hinzugefügt!")
        st.rerun()

    if not user_data.empty:
        st.markdown("### Gespeicherte Blutzuckerwerte")
        st.table(user_data.reset_index(drop=True))
        durchschnitt = user_data["blutzuckerwert"].mean()
        st.markdown(f"**Durchschnittlicher Blutzuckerwert:** {durchschnitt:.2f} mg/dL")
    else:
        st.warning("Noch keine Daten vorhanden.")

def blutzucker_werte():
    st.markdown("## 📋 Blutzucker-Werte")

    if not user_data.empty:
        st.markdown("### Gespeicherte Blutzuckerwerte")
        st.table(user_data.reset_index(drop=True))
    else:
        st.warning("Noch keine Werte gespeichert.")

def blutzucker_grafik():
    st.markdown("## 📊 Blutzucker-Grafik")

    if not user_data.empty:
        st.markdown("### Verlauf der Blutzuckerwerte")
        chart_data = user_data.set_index("datum_zeit")[["blutzuckerwert"]]
        st.line_chart(chart_data)
    else:
        st.warning("Noch keine Werte vorhanden.")

# ====== Seitenwechsel ======
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