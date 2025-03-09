import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Datei zum Speichern der Daten
DATA_FILE = "blutzucker_daten.csv"

def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE).to_dict('records')
    return []

def save_data(data):
    df = pd.DataFrame(data)
    df.to_csv(DATA_FILE, index=False)

def startseite():
    st.markdown("## 🏠 Willkommen auf der Startseite!")
    st.write("""
    Liebe Diabetikerinnen und Diabetiker!🩸

    Kennst du das Problem, den Überblick über deine Blutzuckerwerte zu behalten? Mit unserem Blutzucker-Tracker kannst du deine Werte einfach eingeben, speichern und analysieren – alles an einem Ort!

    - Was bringt dir die App?
    - Schnelle Eingabe deines Blutzuckers (mg/dL)
    - Messzeitpunkt wählen (Nüchtern oder nach dem Essen)
    - Alle Werte speichern & jederzeit abrufen
    - Tabelle & Diagramm, um deine Trends zu erkennen
    - Automatische Warnhinweise, wenn dein Blutzucker zu hoch oder zu niedrig ist

    Warum diese App?
             
    ✔ Kein lästiges Papier-Tagebuch mehr

    ✔ Verfolge deine Werte langfristig & erkenne Muster

    ✔ Bessere Kontrolle für ein gesünderes Leben mit Diabetes

    Einfach testen & deine Blutzuckerwerte im Blick behalten! 🏅
    """)

def blutzucker_tracker():
    st.markdown("## 📈 Blutzucker-Tracker")
    st.subheader("Blutzucker-Tracker")
    
    # Blutzucker-Tracker 
    with st.form(key='blutzucker_form'):
        blutzuckerwert = st.number_input("Gib deinen Blutzuckerwert ein", min_value=0)
        zeitpunkt = st.selectbox("Zeitpunkt", ["Nüchtern", "Nach dem Essen"])
        submit_button = st.form_submit_button(label='Eintrag hinzufügen')
    
    if 'daten' not in st.session_state:
        st.session_state['daten'] = load_data()

    if submit_button:
        datum_zeit = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state['daten'].append({"blutzuckerwert": blutzuckerwert, "zeitpunkt": zeitpunkt, "datum_zeit": datum_zeit})
        save_data(st.session_state['daten'])
        st.success("Eintrag erfolgreich hinzugefügt")
        
    if st.session_state['daten']:
        df = pd.DataFrame(st.session_state['daten'])
        st.write(df)
        
        # Anzeige des letzten Eintrags
        letzter_eintrag = df.iloc[-1]
        st.write("Letzter Eintrag:")
        st.write(f"Blutzuckerwert = {letzter_eintrag['blutzuckerwert']}")
        st.write(f"Zeitpunkt = {letzter_eintrag['zeitpunkt']}")
        st.write(f"Datum & Zeit = {letzter_eintrag['datum_zeit']}")
        
        # Berechnung des Durchschnitts
        durchschnitt = df['blutzuckerwert'].mean()
        st.write(f"Durchschnittlicher Blutzuckerwert: {durchschnitt:.2f} mg/dL")
        
        # Anzeige des letzten Eintrags mit Datum und Uhrzeit
        st.write(f"Blutzucker: {letzter_eintrag['blutzuckerwert']} mg/dL")

# Session-State zur Steuerung der Ansicht
if "seite" not in st.session_state:
    st.session_state.seite = "Startseite"

# Navigation über Buttons
col1, col2 = st.columns(2)
with col1:
    if st.button("🏠 Startseite"):
        st.session_state.seite = "Startseite"
with col2:
    if st.button("📈 Blutzucker-Tracker"):
        st.session_state.seite = "Blutzucker-Tracker"

# Anzeige der gewählten Seite
if st.session_state.seite == "Startseite":
    startseite()
elif st.session_state.seite == "Blutzucker-Tracker":
    blutzucker_tracker()