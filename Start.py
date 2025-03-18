import streamlit as st
import sys
import os

# Sicherstellen, dass das Verzeichnis "utils" im Python-Pfad enthalten ist
utils_path = os.path.abspath("utils")
if utils_path not in sys.path:
    sys.path.append(utils_path)

from data_manager import DataManager  # Import aus utils
from login_manager import LoginManager  # Import aus utils

# Seitenkonfiguration
st.set_page_config(page_title="Blutzucker Tracker", layout="wide")

# Initialisiere DataManager
data_manager = DataManager(fs_protocol='webdav', fs_root_folder="BMLD_cblsf_App")

# Initialisiere LoginManager
login_manager = LoginManager(data_manager)
login_manager.login_register()

# Falls der Benutzer nicht eingeloggt ist, stoppe den weiteren Code
if "authentication_status" not in st.session_state or not st.session_state["authentication_status"]:
    st.stop()

# Startseite
st.markdown("## Blutzucker-Tracker für Diabetiker")

st.write("""
Willkommen zum Blutzucker-Tracker! Diese App unterstützt Sie dabei, Ihre Blutzuckerwerte einfach zu erfassen, zu speichern und zu analysieren. So behalten Sie Ihre Werte stets im Blick und können langfristige Trends erkennen.
""")

# Benutzerinfo
st.info(f" 👋 Eingeloggt als: {st.session_state.username}")

# Autoreninfo
st.write("""
### Autoren  
Diese App wurde im Rahmen des Moduls BMLD Informatik 2 an der ZHAW entwickelt von:

- Cristiana Pereira Bastos (pereicri@students.zhaw.ch)  
- Lou-Salomé Frehner (frehnlou@students.zhaw.ch)
""")