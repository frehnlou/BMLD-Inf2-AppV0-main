import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd
from utils.data_manager import DataManager
from utils.login_manager import LoginManager

# ✅ MUSS erstes Kommando sein!
st.set_page_config(page_title="Blutzucker Tracker", layout="wide")

# ====== Login-Check ======
data_manager = DataManager(fs_protocol='webdav', fs_root_folder="BMLD_cblsf_App")
login_manager = LoginManager(data_manager)
login_manager.go_to_login('Start.py')

# Navigation
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

# 📌 Daten laden (damit beide Seiten dieselben Daten haben)
def lade_daten():
    """ Lädt die Blutzucker-Daten von WebDAV oder erstellt eine neue Datei """
    if "user_data" not in st.session_state:
        st.session_state.user_data = data_manager.load_user_data(
            session_state_key="user_data",
            username=username,  # 🔥 Benutzername als Schlüssel
            initial_value=pd.DataFrame(columns=["datum_zeit", "blutzuckerwert", "zeitpunkt"]),
            parse_dates=["datum_zeit"]
        )
    return st.session_state.user_data

# 🔥 Blutzucker-Tracker
def blutzucker_tracker():
    st.markdown("## 🩸 Blutzucker-Tracker")

    # Daten immer von WebDAV laden
    user_data = lade_daten()

    with st.form(key='blutzucker_form'):
        blutzuckerwert = st.number_input("Blutzuckerwert (mg/dL)", min_value=0, step=1)
        zeitpunkt = st.selectbox("Zeitpunkt", ["Nüchtern", "Nach dem Essen"])
        submit_button = st.form_submit_button(label='Eintrag hinzufügen')

    if submit_button:
        datum_zeit = datetime.now(ZoneInfo("Europe/Zurich")).strftime("%d.%m.%Y %H:%M:%S")
        neuer_eintrag = pd.DataFrame([{ 
            "datum_zeit": datum_zeit, 
            "blutzuckerwert": blutzuckerwert, 
            "zeitpunkt": zeitpunkt 
        }])

        # Daten aktualisieren und speichern
        st.session_state.user_data = pd.concat([user_data, neuer_eintrag], ignore_index=True)
        data_manager.save_user_data(username, st.session_state.user_data)  # ✅ Korrigiert
        st.success("✅ Eintrag hinzugefügt!")
        st.rerun()

    # Daten anzeigen
    if not user_data.empty:
        st.markdown("### Gespeicherte Blutzuckerwerte")
        st.table(user_data.drop(columns=["username"], errors="ignore").reset_index(drop=True))

        durchschnitt = user_data["blutzuckerwert"].mean()
        st.markdown(f"**Durchschnittlicher Blutzuckerwert:** {durchschnitt:.2f} mg/dL")
    else:
        st.warning("⚠️ Noch keine Daten vorhanden.")

# 🔥 Blutzucker-Werte
def blutzucker_werte():
    st.markdown("## 📋 Blutzucker-Werte")

    # Daten immer von WebDAV laden
    user_data = lade_daten()

    if not user_data.empty:
        st.markdown("### Gespeicherte Blutzuckerwerte")
        st.table(user_data.drop(columns=["username"], errors="ignore").reset_index(drop=True))
    else:
        st.warning("⚠️ Noch keine Werte gespeichert.")

# 🔥 Startseite
def startseite():
    st.markdown("## 🏠 Willkommen auf der Startseite!")
    st.write("""
    Willkommen zum Blutzucker-Tracker! Diese App unterstützt Sie dabei, Ihre Blutzuckerwerte einfach zu erfassen, zu speichern und zu analysieren. So behalten Sie Ihre Werte stets im Blick und können langfristige Trends erkennen.
    """)

# 🔄 Seitenwechsel
def seitenwechsel():
    if "seite" not in st.session_state:
        st.session_state.seite = "Startseite"
    
    if st.session_state.seite == "Blutzucker-Tracker":
        blutzucker_tracker()
    elif st.session_state.seite == "Blutzucker-Werte":
        blutzucker_werte()
    elif st.session_state.seite == "Startseite":
        startseite()

# 🔄 Starte die App
seitenwechsel()