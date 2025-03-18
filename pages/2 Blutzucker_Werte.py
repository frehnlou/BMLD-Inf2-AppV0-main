import streamlit as st
import pandas as pd
from utils.login_manager import LoginManager
from utils.data_manager import DataManager

# ====== Start Login Block ======
login_manager = LoginManager()
login_manager.go_to_login('Start.py') 
# ====== End Login Block ======

st.markdown("## 📋 Blutzucker-Werte")

# Nutzername holen
username = st.session_state.get("username")

if not username:
    st.error("⚠️ Kein Benutzer eingeloggt! Anmeldung erforderlich.")
    st.stop()

# Datenbank für den Nutzer laden
data_manager = DataManager(fs_protocol='webdav', fs_root_folder="BMLD_cblsf_App")
user_data = data_manager.load_user_data(
    session_state_key="user_data",
    username=username,  
    parse_dates=["datum_zeit"]
)

if not user_data.empty:
    st.markdown("### Gespeicherte Blutzuckerwerte")
    st.table(user_data[["datum_zeit", "blutzuckerwert", "zeitpunkt"]])
else:
    st.warning("⚠️ Noch keine Blutzuckerwerte vorhanden. Bitte neuen Wert eingeben.")
if __name__ == "__main__":
    blutzucker_werte()