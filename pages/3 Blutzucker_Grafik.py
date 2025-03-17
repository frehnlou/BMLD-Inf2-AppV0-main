import streamlit as st
from utils.login_manager import LoginManager  # 🔐 Login-Manager hinzufügen
from utils.data_manager import DataManager  # 📊 Data Manager für nutzerspezifische Daten

# ====== Start Login Block ======
login_manager = LoginManager()
login_manager.go_to_login('Start.py') 
# ====== End Login Block ======

# Abstand nach oben für bessere Platzierung
st.markdown("<br>", unsafe_allow_html=True)

st.markdown("## 📊 Blutzucker-Grafik")

# Nutzername aus Session holen
username = st.session_state.get("username", "Gast")

# Datenbank für den Nutzer laden
data_manager = DataManager()
user_data = data_manager.load_user_data(
    session_state_key="user_data",
    file_name="data.csv",
    parse_dates=["datum_zeit"]
)

if not user_data.empty:
    st.markdown("### Verlauf der Blutzuckerwerte")
    
    # Werte extrahieren
    blutzuckerwerte = user_data[["datum_zeit", "blutzuckerwert"]].set_index("datum_zeit")
    
    # 🔥 Grafische Darstellung
    st.line_chart(blutzuckerwerte)
else:
    st.warning("Noch keine Daten vorhanden.")