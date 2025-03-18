import streamlit as st
from utils.data_manager import DataManager
from utils.login_manager import LoginManager

# Seitenkonfiguration
st.set_page_config(page_title="Blutzucker Tracker", layout="wide")

# Initialisiere DataManager
data_manager = DataManager(fs_protocol='file', fs_root_folder="BMLD_CPBLSF_App")

# Initialisiere LoginManager
login_manager = LoginManager(data_manager)

# Login- oder Registrierungsseite anzeigen
login_manager.login_register()

# Falls der Benutzer nicht eingeloggt ist, stoppe den weiteren Code
if "authentication_status" not in st.session_state or not st.session_state["authentication_status"]:
    st.stop()

# Startseite nach erfolgreicher Anmeldung
st.markdown("## 🩸 Blutzucker-Tracker für Diabetiker")
st.info(f"👋 Eingeloggt als: {st.session_state.username}")