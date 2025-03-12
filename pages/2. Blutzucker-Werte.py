import streamlit as st

st.title('Blutzucker-Werte')

# Prüfen, ob Daten im Session State vorhanden sind
if 'blutzucker_df' not in st.session_state or st.session_state['blutzucker_df'].empty:
    st.info('Keine Blutzucker-Daten vorhanden. Bitte geben Sie neue Werte ein.')
    st.stop()

# Blutzucker-Daten abrufen und nach Zeitstempel sortieren
blutzucker_df = st.session_state['blutzucker_df'].sort_values('timestamp', ascending=False)

# Tabelle anzeigen
st.dataframe(blutzucker_df)