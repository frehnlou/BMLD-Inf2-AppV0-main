import streamlit as st

st.title('Blutzucker Verlauf')

# Sicherstellen, dass die Session-State-Daten existieren
if 'blutzucker_df' not in st.session_state or st.session_state['blutzucker_df'].empty:
    st.info('Keine Blutzucker-Daten vorhanden. Bitte geben Sie neue Werte ein.')
    st.stop()

# Blutzucker-Daten abrufen
blutzucker_df = st.session_state['blutzucker_df']

# Sicherstellen, dass die notwendigen Spalten vorhanden sind
if 'timestamp' not in blutzucker_df.columns or 'blood_sugar' not in blutzucker_df.columns:
    st.error('Die Daten enthalten nicht die erforderlichen Spalten: "timestamp" und "blood_sugar".')
    st.stop()

# Daten nach Zeitstempel sortieren
blutzucker_df = blutzucker_df.sort_values('timestamp', ascending=True)

# Blutzucker über Zeit anzeigen
st.line_chart(data=blutzucker_df.set_index('timestamp')['blood_sugar'], use_container_width=True)
st.caption('Blutzuckerwerte über Zeit (mg/dL oder mmol/L)')