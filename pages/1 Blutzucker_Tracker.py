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
user_data = data_manager.load_user_data(
    session_state_key=f"user_data_{username}",
    username=username,
    initial_value=pd.DataFrame(columns=["datum_zeit", "blutzuckerwert", "zeitpunkt"]),
    parse_dates=["datum_zeit"]
)

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

# ====== Blutzucker-Tracker ======
st.markdown("## 🩸 Blutzucker-Tracker")

st.write("""
Mit dem Blutzucker-Tracker können Sie Ihre Blutzuckerwerte einfach eingeben und speichern. 
Verfolgen Sie Ihre Werte langfristig und behalten Sie die Kontrolle über Ihre Gesundheit.
""")

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
    st.session_state[f"user_data_{username}"] = pd.concat([user_data, new_entry], ignore_index=True)

    # Speichert die Werte nur für den aktuellen Benutzer
    data_manager.save_user_data(
        session_state_key=f"user_data_{username}",
        username=username
    )

    st.success("Eintrag hinzugefügt!")
    st.rerun()

# ====== Gespeicherte Werte anzeigen ======
if not user_data.empty:
    st.markdown("### Gespeicherte Blutzuckerwerte")
    st.table(user_data.reset_index(drop=True))
else:
    st.warning("Noch keine Daten vorhanden.")