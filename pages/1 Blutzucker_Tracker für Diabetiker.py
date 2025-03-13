import streamlit as st
from datetime import datetime
from utils.data_manager import DataManager
import pandas as pd

# Set page configuration
st.set_page_config(page_title="Blutzucker Tracker", layout="wide")

# Abstand nach oben für bessere Platzierung
st.markdown("<br>", unsafe_allow_html=True)

# Navigation über vier Spalten
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🏠 Startseite"):
        st.session_state.seite = "Startseite"

with col2:
    if st.button("🩸 Blutzucker-Tracker"):
        st.session_state.seite = "Blutzucker-Tracker"

with col3:
    if st.button("📋 Blutzucker-Werte"):
        st.session_state.seite = "Blutzucker-Werte"

with col4:
    if st.button("📊 Blutzucker-Grafik"):
        st.session_state.seite = "Blutzucker-Grafik"

def startseite():
    st.markdown("## 🏠 Willkommen auf der Startseite!")
    st.write("""
    Liebe Diabetikerinnen und Diabetiker!🩸

    Kennst du das Problem, den Überblick über deine Blutzuckerwerte zu behalten? Mit unserem Blutzucker-Tracker kannst du deine Werte einfach eingeben, speichern und analysieren – alles an einem Ort!

    - Was bringt dir die App?
    - Schnelle Eingabe deines Blutzuckers (mg/dL)
    - Messzeitpunkt wählen (Nüchtern, Nach dem Essen)
    - Automatische Übersicht in einer Tabelle, damit du deine Werte immer im Blick hast
    - Anschauliche Diagramme, die deine Blutzuckerwerte visuell auswerten

    Warum diese App?
             
    ✔ Kein lästiges Papier-Tagebuch mehr

    ✔ Verfolge deine Werte langfristig & erkenne Muster

    ✔ Bessere Kontrolle für ein gesünderes Leben mit Diabetes

    Einfach testen & deine Blutzuckerwerte im Blick behalten! 🏅
    """)

def blutzucker_tracker():
    st.markdown("## 🩸 Blutzucker-Tracker")
    
    with st.form(key='blutzucker_form'):
        blutzuckerwert = st.number_input("Gib deinen Blutzuckerwert ein", min_value=0, step=1)
        zeitpunkt = st.selectbox("Zeitpunkt", ["Nüchtern", "Nach dem Essen"])
        submit_button = st.form_submit_button(label='Eintrag hinzufügen')
    
    if 'daten' not in st.session_state:
        st.session_state['daten'] = []

    if submit_button:
        datum_zeit = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        result = {
            "blutzuckerwert": blutzuckerwert,
            "zeitpunkt": zeitpunkt,
            "datum_zeit": datum_zeit
        }
        st.session_state['daten'].append(result)
        st.success("Eintrag erfolgreich hinzugefügt")
        
        dm = DataManager()
        if 'data_df' not in st.session_state:
            st.session_state['data_df'] = pd.DataFrame()
        st.session_state['data_df'] = pd.concat([st.session_state['data_df'], pd.DataFrame([result])], ignore_index=True)
    
    if st.session_state['daten']:
        st.markdown("### Gespeicherte Blutzuckerwerte")
        
        # Durchschnitt berechnen
        durchschnitt = sum(d['blutzuckerwert'] for d in st.session_state['daten']) / len(st.session_state['daten'])
        
        # Daten als Tabelle anzeigen
        daten_anzeige = st.session_state['daten'][:]
        st.table(daten_anzeige)
        
        # Durchschnittswert anzeigen
        st.markdown(f"Durchschnittlicher Blutzuckerwert: {durchschnitt:.2f} mg/dL")

        # Löschoption
        st.markdown("### Eintrag löschen")
        with st.form(key='delete_form'):
            index_to_delete = st.number_input("Index des zu löschenden Eintrags", min_value=1, max_value=len(st.session_state['daten']), step=1)
            delete_button = st.form_submit_button(label='Eintrag löschen')
        
        if delete_button:
            if 0 <= index_to_delete - 1 < len(st.session_state['daten']):
                del st.session_state['daten'][index_to_delete - 1]
                st.success("Eintrag erfolgreich gelöscht")
                st.rerun()

def blutzucker_werte():
    st.markdown("## 📋 Blutzucker-Werte")
    if 'daten' in st.session_state and st.session_state['daten']:
        st.markdown("### Gespeicherte Blutzuckerwerte")
        st.table(st.session_state['daten'])
    else:
        st.warning("Noch keine Daten vorhanden.")

def blutzucker_grafik():
    st.markdown("## 📊 Blutzucker-Grafik")
    if 'daten' in st.session_state and st.session_state['daten']:
        st.markdown("### Verlauf der Blutzuckerwerte")
        blutzuckerwerte = [d['blutzuckerwert'] for d in st.session_state['daten']]
        st.line_chart({"Blutzuckerwert": blutzuckerwerte})
    else:
        st.warning("Noch keine Daten vorhanden.")

if "seite" not in st.session_state:
    st.session_state.seite = "Startseite"

if st.session_state.seite == "Startseite":
    startseite()
elif st.session_state.seite == "Blutzucker-Tracker":
    blutzucker_tracker()
elif st.session_state.seite == "Blutzucker-Werte":
    try:
        from pages import Blutzucker_Werte
        Blutzucker_Werte.blutzucker_werte()
    except ImportError as e:
        st.error(f"Fehler beim Importieren von Blutzucker_Werte: {e}")
elif st.session_state.seite == "Blutzucker-Grafik":
    try:
        from pages import Blutzucker_Grafik
        Blutzucker_Grafik.blutzucker_grafik()
    except ImportError as e:
        st.error(f"Fehler beim Importieren von Blutzucker_Grafik: {e}")