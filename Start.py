import streamlit as st
import pandas as pd
import os
from utils.data_manager import DataManager
from utils.login_manager import LoginManager  # 🔐 Login-Manager hinzufügen

# ✅ `st.set_page_config` MUSS als erstes Streamlit-Kommando stehen!
st.set_page_config(page_title="Blutzucker Tracker", layout="wide")

# ====== Start Init Block (Login & Datenmanagement) ======

# Initialisierung des Data Managers
data_manager = DataManager(fs_protocol='webdav', fs_root_folder="BMLD_cblsf_App")

# Initialisierung des Login Managers
login_manager = LoginManager(data_manager)
login_manager.login_register()  # Öffnet Login-/Registrierungsseite

# ✅ Sicherstellen, dass `data.csv` existiert
data_file = os.path.join(data_manager.fs_root_folder, "data.csv")
if not os.path.exists(data_file):
    pd.DataFrame(columns=["username", "datum_zeit", "blutzuckerwert", "zeitpunkt"]).to_csv(data_file, index=False)

# 🔥 Nutzerbezogene Daten laden
data_manager.load_user_data(
    session_state_key='data_df', 
    file_name='data.csv', 
    initial_value=pd.DataFrame(), 
    parse_dates=['datum_zeit']
)

# ====== End Init Block ======

# Titel mit größerer Schrift
st.markdown("## 🩸 Blutzucker-Tracker für Diabetiker")

# Beschreibung in normalem Text
st.write("""
Willkommen zum Blutzucker-Tracker! Diese App unterstützt Sie dabei, Ihre Blutzuckerwerte einfach zu erfassen, zu speichern und zu analysieren. So behalten Sie Ihre Werte stets im Blick und können langfristige Trends erkennen.
""")

# 👤 Zeigt den eingeloggten Benutzer an (Falls Session State korrekt gesetzt ist)
if "username" in st.session_state and st.session_state["username"]:
    st.info(f"👋 Eingeloggt als: **{st.session_state.username}**")
else:
    st.warning("⚠️ Kein Benutzer eingeloggt!")

# Zusätzliche Information in einer dezenten farbigen Box
st.markdown("""
<div style="border-left: 4px solid #4CAF50; background-color: #F0FFF0; padding: 10px; border-radius: 5px;">
Nutzen Sie die App regelmäßig, um Ihre Blutzuckerwerte besser im Blick zu behalten und langfristige Muster zu erkennen.
</div>
""", unsafe_allow_html=True)

# Autoren und E-Mails in einer klaren Struktur
st.write("""
### Autoren  
Diese App wurde im Rahmen des Moduls *BMLD Informatik 2* an der ZHAW entwickelt von:

- **Cristiana Bastos** ([pereicri@students.zhaw.ch](mailto:pereicri@students.zhaw.ch))  
- **Lou-Salomé Frehner** ([frehnlou@students.zhaw.ch](mailto:frehnlou@students.zhaw.ch))
""")