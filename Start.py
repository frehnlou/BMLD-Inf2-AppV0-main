import streamlit as st
import pandas as pd
from utils.data_manager import DataManager
from utils.login_manager import LoginManager  # 🔐 Login-Manager hinzufügen

# ✅ MUSS als erstes Streamlit-Kommando stehen
st.set_page_config(page_title="Blutzucker Tracker", layout="wide")

# ====== Start Login Block ======
data_manager = DataManager(fs_protocol='webdav', fs_root_folder="BMLD_cblsf_App")
login_manager = LoginManager(data_manager)
login_manager.login_register()  # Login-/Registrierungsseite anzeigen

# ✅ Prüfe, ob ein Benutzer eingeloggt ist, bevor Daten geladen werden
if "username" in st.session_state and st.session_state["username"]:
    data_manager.load_user_data(
        session_state_key='data_df',
        file_name='data.csv',
        initial_value=pd.DataFrame(columns=["username", "datum_zeit", "blutzuckerwert", "zeitpunkt"]),
        parse_dates=['datum_zeit']
    )
else:
    st.warning("⚠️ Kein Benutzer eingeloggt! Daten können nicht geladen werden.")

# ====== Ende Login & Daten Block ======

# Titel und Begrüßung
st.markdown("## 🩸 Blutzucker-Tracker für Diabetiker")

# Beschreibung
st.write("""
Willkommen zum Blutzucker-Tracker! Diese App unterstützt Sie dabei, Ihre Blutzuckerwerte einfach zu erfassen, zu speichern und zu analysieren. So behalten Sie Ihre Werte stets im Blick und können langfristige Trends erkennen.
""")

# 👤 Benutzerinfo
if "username" in st.session_state:
    st.info(f"👋 Eingeloggt als: **{st.session_state.username}**")
else:
    st.warning("⚠️ Kein Benutzer eingeloggt!")

# Infobox
st.markdown("""
<div style="border-left: 4px solid #4CAF50; background-color: #F0FFF0; padding: 10px; border-radius: 5px;">
Nutzen Sie die App regelmäßig, um Ihre Blutzuckerwerte besser im Blick zu behalten und langfristige Muster zu erkennen.
</div>
""", unsafe_allow_html=True)

# Autoreninfo
st.write("""
### Autoren  
Diese App wurde im Rahmen des Moduls *BMLD Informatik 2* an der ZHAW entwickelt von:

- **Cristiana Bastos** ([pereicri@students.zhaw.ch](mailto:pereicri@students.zhaw.ch))  
- **Lou-Salomé Frehner** ([frehnlou@students.zhaw.ch](mailto:frehnlou@students.zhaw.ch))
""")
