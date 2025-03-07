import streamlit as st
import pandas as pd
import datetime

def startseite():
    st.title("Blutzucker-Tracker für Diabetiker")
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
    st.subheader("Blutzucker-Tracker")
    
    # Blutzucker-Tracker 
    with st.form(key='blutzucker_form'):
        blutzuckerwert = st.number_input("Gib deinen Blutzuckerwert ein", min_value=0)
        zeitpunkt = st.selectbox("Zeitpunkt", ["Nüchtern", "Nach dem Essen"])
        submit_button = st.form_submit_button(label='Eintrag hinzufügen')
    
    if 'daten' not in st.session_state:
        st.session_state['daten'] = []

    if submit_button:
        datum_zeit = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state['daten'].append({"blutzuckerwert": blutzuckerwert, "zeitpunkt": zeitpunkt, "datum_zeit": datum_zeit})
        st.success("Eintrag erfolgreich hinzugefügt")
        
    if st.session_state['daten']:
        df = pd.DataFrame(st.session_state['daten'])
        st.write(df)
        
        # Anzeige des letzten Eintrags
        letzter_eintrag = df.iloc[-1]
        st.write(f"Letzter Eintrag: Blutzuckerwert = {letzter_eintrag['blutzuckerwert']}, Zeitpunkt = {letzter_eintrag['zeitpunkt']}, Datum & Zeit = {letzter_eintrag['datum_zeit']}")
        
        # Berechnung des Durchschnitts
        durchschnitt = df['blutzuckerwert'].mean()
        st.write(f"Durchschnittlicher Blutzuckerwert: {durchschnitt:.2f} mg/dL")
        
# Sidebar for navigation
st.sidebar.title("Navigation")
wahl = st.sidebar.radio("Gehe zu", ["Startseite", "Blutzucker-Tracker"])

# Display the selected page
if wahl == "Startseite":
    startseite()
elif wahl == "Blutzucker-Tracker":
    blutzucker_tracker()