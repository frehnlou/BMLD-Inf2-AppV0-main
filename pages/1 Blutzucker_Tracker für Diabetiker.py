import streamlit as st
from datetime import datetime
from utils.data_manager import DataManager
import pandas as pd

st.set_page_config(page_title="Blutzucker Tracker", layout="wide")

# Abstand nach oben für bessere Platzierung
st.markdown("<br>", unsafe_allow_html=True)

# Navigation
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🏠 Startseite"):
        st.switch_page("app")

with col2:
    if st.button("🩸 Blutzucker-Tracker"):
        st.switch_page("pages/Blutzucker_Tracker")

with col3:
    if st.button("📋 Blutzucker-Werte"):
        st.switch_page("pages/Blutzucker_Werte")

with col4:
    if st.button("📊 Blutzucker-Grafik"):
        st.switch_page("pages/Blutzucker_Grafik")

st.markdown("## 🩸 Blutzucker-Tracker")

with st.form(key='blutzucker_form'):
    blutzuckerwert = st.number_input("Gib deinen Blutzuckerwert ein", min_value=0, step=1)
    zeitpunkt = st.selectbox("Zeitpunkt", ["Nüchtern", "Nach dem Essen"])
    submit_button = st.form_submit_button(label='Eintrag hinzufügen')

if 'daten' not in st.session_state:
    st.session_state['daten'] = []

if submit_button:
    datum_zeit = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    result = {"blutzuckerwert": blutzuckerwert, "zeitpunkt": zeitpunkt, "datum_zeit": datum_zeit}
    st.session_state['daten'].append(result)
    st.success("Eintrag erfolgreich hinzugefügt")

    dm = DataManager()
    if 'data_df' not in st.session_state:
        st.session_state['data_df'] = pd.DataFrame()
    st.session_state['data_df'] = pd.concat([st.session_state['data_df'], pd.DataFrame([result])], ignore_index=True)

if st.session_state['daten']:
    st.markdown("### Gespeicherte Blutzuckerwerte")
    st.table(st.session_state['daten'])
