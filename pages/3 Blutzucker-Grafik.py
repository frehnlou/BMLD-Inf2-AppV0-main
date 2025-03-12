import streamlit as st
import altair as alt

st.title('Blutzucker Verlauf')

# Prüfen, ob Blutzucker-Daten vorhanden sind
if 'blutzucker_df' not in st.session_state or st.session_state['blutzucker_df'].empty:
    st.info('Keine Blutzucker-Daten vorhanden. Bitte geben Sie neue Werte ein.')
    st.stop()

# Blutzucker-Daten abrufen und nach Zeitstempel sortieren
blutzucker_df = st.session_state['blutzucker_df'].sort_values('timestamp', ascending=True)

# Blutzucker-Grafik mit roter Linie und Diagrammbeschriftung
chart = alt.Chart(blutzucker_df).mark_line(color='red').encode(
    x=alt.X('timestamp:T', title='Zeitstempel'),
    y=alt.Y('blood_sugar:Q', title='Blutzuckerwert (mg/dL oder mmol/L)'),
    tooltip=['timestamp:T', 'blood_sugar:Q']
).properties(
    title="Blutzuckerwerte über Zeit"
)

# Diagramm in Streamlit anzeigen
st.altair_chart(chart, use_container_width=True)

st.caption('Blutzuckerwerte über Zeit (mg/dL oder mmol/L)')
