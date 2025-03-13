import streamlit as st
import pandas as pd
from utils.data_manager import DataManager

# Initialisierung des Data Managers
data_manager = DataManager(fs_protocol='webdav', fs_root_folder="BMLD_cblsf_App")

# Laden der Daten aus dem persistenten Speicher in den Session State
data_manager.load_app_data(
    session_state_key='data_df', 
    file_name='data.csv', 
    initial_value=pd.DataFrame(), 
    parse_dates=['timestamp']
)

# Titel mit grösserer Schrift
st.markdown("## 🩸 Blutzucker-Tracker für Diabetiker")

# Beschreibung in normalem Text
st.write("""
Willkommen zum Blutzucker-Tracker! Diese App unterstützt Sie dabei, Ihre Blutzuckerwerte einfach zu erfassen, zu speichern und zu analysieren. So behalten Sie Ihre Werte stets im Blick und können langfristige Trends erkennen.
""")

# Zusätzliche Information in einer dezenten farbigen Box
st.markdown("""
<div style="border-left: 4px solid #4CAF50; background-color: #F0FFF0; padding: 10px; border-radius: 5px;">
Nutzen Sie die App regelmässig, um Ihre Blutzuckerwerte besser im Blick zu behalten und langfristige Muster zu erkennen.
</div>
""", unsafe_allow_html=True)

# Autoren und E-Mails in einer klaren Struktur
st.write("""
### Autoren  
Diese App wurde im Rahmen des Moduls *BMLD Informatik 2* an der ZHAW entwickelt von:

- **Cristiana Bastos** ([pereicri@students.zhaw.ch](mailto:pereicri@students.zhaw.ch))  
- **Lou-Salomé Frehner** ([frehnlou@students.zhaw.ch](mailto:frehnlou@students.zhaw.ch))
""")