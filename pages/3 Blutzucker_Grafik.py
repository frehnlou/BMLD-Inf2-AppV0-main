import streamlit as st
from utils.login_manager import LoginManager  # 🔐 Login-Manager hinzufügen

# ====== Start Login Block ======
login_manager = LoginManager()
login_manager.go_to_login('Start.py') 
# ====== End Login Block ======

# Abstand nach oben für bessere Platzierung
st.markdown("<br>", unsafe_allow_html=True)

st.markdown("## 📊 Blutzucker-Grafik")

if 'daten' in st.session_state and st.session_state['daten']:
    st.markdown("### Verlauf der Blutzuckerwerte")
    blutzuckerwerte = [d['blutzuckerwert'] for d in st.session_state['daten']]
    st.line_chart({"Blutzuckerwert": blutzuckerwerte})
else:
    st.warning("Noch keine Daten vorhanden.")