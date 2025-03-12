import streamlit as st

# Abstand nach oben für bessere Platzierung
st.markdown("<br>", unsafe_allow_html=True)

# Vier Spalten für die Buttons
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🏠 Startseite"):
        st.session_state.seite = "Startseite"

with col2:
    if st.button("📊 Blutzucker-Tracker"):
        st.session_state.seite = "Blutzucker-Tracker"

with col3:
    if st.button("📈 Blutzucker-Werte"):
        st.session_state.seite = "Blutzucker-Werte"

with col4:
    if st.button("📉 Blutzucker-Grafik"):
        st.session_state.seite = "Blutzucker-Grafik"

st.title('Blutzucker Verlauf')

# Prüfen, ob Blutzucker-Daten vorhanden sind
if 'blutzucker_df' not in st.session_state or st.session_state['blutzucker_df'].empty:
    st.info('Keine Blutzucker-Daten vorhanden. Bitte geben Sie neue Werte ein.')
    st.stop()

# Blutzucker-Daten abrufen und nach Zeitstempel sortieren
blutzucker_df = st.session_state['blutzucker_df'].sort_values('timestamp', ascending=True)

# Blutzucker über die Zeit als Liniendiagramm
st.line_chart(data=blutzucker_df.set_index('timestamp')['blood_sugar'], 
              use_container_width=True)
st.caption('Blutzuckerwerte über Zeit (mg/dL oder mmol/L)')

# Falls weitere Werte (z. B. Insulin oder Kohlenhydrate) gespeichert werden:
if 'insulin' in blutzucker_df.columns:
    st.line_chart(data=blutzucker_df.set_index('timestamp')['insulin'], 
                  use_container_width=True)
    st.caption('Insulin-Dosis über Zeit (Einheiten)')

if 'carbs' in blutzucker_df.columns:
    st.line_chart(data=blutzucker_df.set_index('timestamp')['carbs'], 
                  use_container_width=True)
    st.caption('Kohlenhydrate über Zeit (g)')
st.title('Blutzucker Verlauf')

# Prüfen, ob Blutzucker-Daten vorhanden sind
if 'blutzucker_df' not in st.session_state or st.session_state['blutzucker_df'].empty:
    st.info('Keine Blutzucker-Daten vorhanden. Bitte geben Sie neue Werte ein.')
    st.stop()

# Blutzucker-Daten abrufen und nach Zeitstempel sortieren
blutzucker_df = st.session_state['blutzucker_df'].sort_values('timestamp', ascending=True)

# Blutzucker über die Zeit als Liniendiagramm
st.line_chart(data=blutzucker_df.set_index('timestamp')['blood_sugar'], 
              use_container_width=True)
st.caption('Blutzuckerwerte über Zeit (mg/dL oder mmol/L)')

# Falls weitere Werte (z. B. Insulin oder Kohlenhydrate) gespeichert werden:
if 'insulin' in blutzucker_df.columns:
    st.line_chart(data=blutzucker_df.set_index('timestamp')['insulin'], 
                  use_container_width=True)
    st.caption('Insulin-Dosis über Zeit (Einheiten)')

if 'carbs' in blutzucker_df.columns:
    st.line_chart(data=blutzucker_df.set_index('timestamp')['carbs'], 
                  use_container_width=True)
    st.caption('Kohlenhydrate über Zeit (g)')