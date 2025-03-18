import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd
from utils.data_manager import DataManager
from utils.login_manager import LoginManager

# Seitenkonfiguration
st.set_page_config(page_title="Blutzucker Werte", layout="wide")

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

# ====== Blutzucker-Werte ======
st.markdown("## 📋 Blutzucker-Werte")

# ====== Gespeicherte Werte anzeigen ======
if not user_data.empty:
    st.markdown("### Gespeicherte Blutzuckerwerte")
    st.table(user_data.reset_index(drop=True))
else:
    st.warning("Noch keine Daten vorhanden.")