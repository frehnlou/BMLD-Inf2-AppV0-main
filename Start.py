import streamlit as st
import pandas as pd
from utils.data_manager import DataManager
from utils.login_manager import LoginManager

# Seitenkonfiguration
st.set_page_config(page_title="Blutzucker Tracker", layout="wide")

# Daten laden mit Fehlerbehandlung
try:
    data_manager.load_user_data(
        session_state_key='data_df', 
        file_name='data.csv', 
        initial_value=pd.DataFrame(columns=["datum_zeit", "blutzuckerwert", "zeitpunkt"]), 
        parse_dates=['datum_zeit']
    )
except FileNotFoundError:
    st.warning("Die Datei 'data.csv' wurde nicht gefunden. Ein neues leeres DataFrame wird erstellt.")
    st.session_state['data_df'] = pd.DataFrame(columns=["timesdatum_zeit", "blutzuckerwert", "zeitpunkt"])
except ValueError as e:
    st.error(f"Fehler beim Laden der Daten: {e}")
    st.stop()

# Falls der Benutzer nicht eingeloggt ist, stoppe den weiteren Code
if "authentication_status" not in st.session_state or not st.session_state["authentication_status"]:
    st.error("⚠️ Sie sind nicht eingeloggt. Bitte melden Sie sich an.")
    st.stop()

# Überprüfen, ob der Benutzername im Session-State vorhanden ist
if "username" not in st.session_state:
    st.error("⚠️ Benutzername fehlt im Session-State. Bitte melden Sie sich erneut an.")
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