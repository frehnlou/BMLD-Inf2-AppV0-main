import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title('Blutzucker Verlauf')

# Prüfen, ob Blutzucker-Daten vorhanden sind
if 'blutzucker_df' not in st.session_state or st.session_state['blutzucker_df'].empty:
    st.info('Keine Blutzucker-Daten vorhanden. Bitte geben Sie neue Werte ein.')
    st.stop()

# Blutzucker-Daten abrufen und nach Zeitstempel sortieren
blutzucker_df = st.session_state['blutzucker_df'].sort_values('timestamp', ascending=True)

# Blutzucker über die Zeit als Liniendiagramm mit roter Linie
fig, ax = plt.subplots()
ax.plot(blutzucker_df['timestamp'], blutzucker_df['blood_sugar'], color='red')
ax.set_xlabel('Zeit')
ax.set_ylabel('Blutzucker (mg/dL oder mmol/L)')
ax.set_title('Blutzuckerwerte über Zeit')
st.pyplot(fig)
st.caption('Blutzuckerwerte über Zeit (mg/dL oder mmol/L)')

# Falls weitere Werte (z. B. Insulin oder Kohlenhydrate) gespeichert werden:
if 'insulin' in blutzucker_df.columns:
    fig, ax = plt.subplots()
    ax.plot(blutzucker_df['timestamp'], blutzucker_df['insulin'], color='red')
    ax.set_xlabel('Zeit')
    ax.set_ylabel('Insulin (Einheiten)')
    ax.set_title('Insulin-Dosis über Zeit')
    st.pyplot(fig)
    st.caption('Insulin-Dosis über Zeit (Einheiten)')

if 'carbs' in blutzucker_df.columns:
    fig, ax = plt.subplots()
    ax.plot(blutzucker_df['timestamp'], blutzucker_df['carbs'], color='red')
    ax.set_xlabel('Zeit')
    ax.set_ylabel('Kohlenhydrate (g)')
    ax.set_title('Kohlenhydrate über Zeit')
    st.pyplot(fig)
    st.caption('Kohlenhydrate über Zeit (g)')