import streamlit as st
import pandas as pd
from utils.login_manager import LoginManager
from utils.data_manager import DataManager

# ====== Start Login Block ======
login_manager = LoginManager()
login_manager.go_to_login('Start.py') 
# ====== End Login Block ======

st.markdown("## 📊 Blutzucker-Grafik")

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
    st.markdown("###  Verlauf der Blutzuckerwerte")

    if "datum_zeit" in user_data.columns and "blutzuckerwert" in user_data.columns:
        try:
            user_data["datum_zeit"] = pd.to_datetime(user_data["datum_zeit"], errors='coerce')
            blutzuckerwerte = user_data.set_index("datum_zeit")[["blutzuckerwert"]]

            if len(blutzuckerwerte) > 1:
                st.line_chart(blutzuckerwerte)
            else:
                st.warning("⚠️ Mindestens zwei Werte erforderlich, um eine Grafik darzustellen.")
        except Exception as e:
            st.error(f"⚠️ Fehler bei der Grafikerstellung: {e}")
    else:
        st.warning("⚠️ Datenformat fehlerhaft oder Spalten fehlen!")
else:
    st.warning("⚠️ Noch keine Blutzuckerwerte vorhanden. Bitte neuen Wert eingeben.")
