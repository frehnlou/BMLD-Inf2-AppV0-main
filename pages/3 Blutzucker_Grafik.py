import streamlit as st

def set_page_config():
    st.set_page_config(page_title="Blutzucker Grafik", layout="wide")

set_page_config()

# Abstand nach oben für bessere Platzierung
st.markdown("<br>", unsafe_allow_html=True)

st.markdown("## 📊 Blutzucker-Grafik")

if 'daten' in st.session_state and st.session_state['daten']:
    st.markdown("### Verlauf der Blutzuckerwerte")
    blutzuckerwerte = [d['blutzuckerwert'] for d in st.session_state['daten']]
    st.line_chart({"Blutzuckerwert": blutzuckerwerte})
else:
    st.warning("Noch keine Daten vorhanden.")