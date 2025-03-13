import streamlit as st

st.set_page_config(page_title="Blutzucker Werte", layout="wide")

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

st.markdown("## 📋 Blutzucker-Werte")

if 'daten' in st.session_state and st.session_state['daten']:
    st.markdown("### Gespeicherte Blutzuckerwerte")
    st.table(st.session_state['daten'])
    
    # Durchschnitt berechnen
    durchschnitt = sum(d['blutzuckerwert'] for d in st.session_state['daten']) / len(st.session_state['daten'])
    
    # Durchschnittswert anzeigen
    st.markdown(f"*Durchschnittlicher Blutzuckerwert:* {durchschnitt:.2f} mg/dL")
else:
    st.warning("Noch keine Daten vorhanden.")
