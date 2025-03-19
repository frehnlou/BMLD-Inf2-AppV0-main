import streamlit as st
import pandas as pd
from utils.data_manager import DataManager
from utils.login_manager import LoginManager

# Seitenkonfiguration
st.set_page_config(page_title="Blutzucker Tracker", layout="wide")

# Initialisiere DataManager
data_manager = DataManager(fs_protocol='webdav', fs_root_folder="BMLD_CPBLSF_App")
login_manager = LoginManager(data_manager)
login_manager.login_register()

# load the data from the persistent storage into the session state
data_manager.load_user_data(
    session_state_key='data_df', 
    file_name='data.csv', 
    initial_value = pd.DataFrame(), 
    parse_dates = ['timestamp']
    )

# Falls der Benutzer nicht eingeloggt ist, stoppe den weiteren Code
if "authentication_status" not in st.session_state or not st.session_state["authentication_status"]:
    st.stop()

# Startseite nach erfolgreicher Anmeldung
st.markdown("## 🩸 Blutzucker-Tracker für Diabetiker")

st.write("""
Willkommen zum Blutzucker-Tracker! Diese App unterstützt Sie dabei, Ihre Blutzuckerwerte einfach zu erfassen, zu speichern und zu analysieren. So behalten Sie Ihre Werte stets im Blick und können langfristige Trends erkennen.
""")

# 👤 Benutzerinfo
st.info(f"👋 Eingeloggt als: {st.session_state.username}")

# Infobox
st.markdown("""
<div style="border-left: 4px solid #4CAF50; background-color: #F0FFF0; padding: 10px; border-radius: 5px;">
Nutzen Sie die App regelmässig, um Ihre Blutzuckerwerte besser im Blick zu behalten und langfristige Muster zu erkennen.
</div>
""", unsafe_allow_html=True)

# Autoreninfo
st.write("""
### Autoren  
Diese App wurde im Rahmen des Moduls BMLD Informatik 2 an der ZHAW entwickelt von:

- Cristiana Bastos (pereicri@students.zhaw.ch)  
- Lou-Salomé Frehner (frehnlou@students.zhaw.ch)
""")