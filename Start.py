import streamlit as st
import sys
import os

# Füge das Hauptverzeichnis zum Modulpfad hinzu, falls erforderlich
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.data_manager import DataManager
from utils.login_manager import LoginManager

# Seitenkonfiguration
st.set_page_config(page_title="Blutzucker Tracker", layout="wide")

# Initialisiere DataManager
data_manager = DataManager(fs_protocol='local', fs_root_folder="shared_folder")

# Initialisiere LoginManager
login_manager = LoginManager(data_manager)
login_manager.login_register()

# Benutzerinfo
if st.session_state.get("authentication_status"):
    st.info(f" 👋 Eingeloggt als: {st.session_state.username}")

# Autoreninfo
st.write("""
### Autoren  
Diese App wurde im Rahmen des Moduls BMLD Informatik 2 an der ZHAW entwickelt von:

- Cristiana Pereira Bastos (pereicri@students.zhaw.ch)  
- Lou-Salomé Frehner (frehnlou@students.zhaw.ch)
""")