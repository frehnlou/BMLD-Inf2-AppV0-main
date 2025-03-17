import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo
from utils.data_manager import DataManager
from utils.login_manager import LoginManager
import pandas as pd

# ✅ Muss als erstes Streamlit-Kommando stehen!
st.set_page_config(page_title="Blutzucker Tracker", layout="wide")

# ====== Login-Check ======
login_manager = LoginManager()
login_manager.go_to_login('Start.py')

# Abstand für bessere Optik
st.markdown("<br>", unsafe_allow_html=True)

# Navigation mit vier Spalten
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
    Liebe Diabetikerinnen und Diabetiker! 🩸

    Kennst du das Problem, den Überblick über deine Blutzuckerwerte zu behalten? Mit unserem Blutzucker-Tracker kannst du deine Werte einfach eingeben, speichern und analysieren – alles an einem Ort!

    - Schnelle Eingabe deines Blutzuckers (mg/dL)
    - Messzeitpunkt wählen (Nüchtern, Nach dem Essen)
    - Automatische Übersicht in einer Tabelle, damit du deine Werte immer im Blick hast
    - Anschauliche Diagramme, die deine Blutzuckerwerte visuell auswerten

    **Warum diese App?**
    ✔ Kein lästiges Papier-Tagebuch mehr  
    ✔ Verfolge deine Werte langfristig & erkenne Muster  
    ✔ Bessere Kontrolle für ein gesünderes Leben mit Diabetes  

    **Einfach testen & deine Blutzuckerwerte im Blick behalten! 🏅**
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
        datum_zeit = datetime.now(ZoneInfo("Europe/Zurich")).strftime("%d.%m.%Y %H:%M:%S")
        result = {
            "blutzuckerwert": blutzuckerwert,
            "zeitpunkt": zeitpunkt,
            "datum_zeit": datum_zeit
        }
        st.session_state['daten'].append(result)
        st.success("✅ Eintrag erfolgreich hinzugefügt!")

        # Speichern der Daten
        dm = DataManager()
        if 'data_df' not in st.session_state:
            st.session_state['data_df'] = pd.DataFrame()
        st.session_state['data_df'] = pd.concat([st.session_state['data_df'], pd.DataFrame([result])], ignore_index=True)

        st.rerun()

    if st.session_state['daten']:
        st.markdown("### Gespeicherte Blutzuckerwerte")
        
        # Durchschnitt berechnen
        durchschnitt = sum(d['blutzuckerwert'] for d in st.session_state['daten']) / len(st.session_state['daten'])
        
        # Daten als Tabelle anzeigen
        daten_df = pd.DataFrame(st.session_state['daten']).drop(columns=['zeitpunkt'], errors='ignore')
        st.table(daten_df)

        # Durchschnittswert anzeigen
        st.markdown(f"**Durchschnittlicher Blutzuckerwert:** {durchschnitt:.2f} mg/dL")

def blutzucker_werte():
    st.markdown("## 📋 Blutzucker-Werte")
    if 'daten' in st.session_state and st.session_state['daten']:
        st.markdown("### Gespeicherte Blutzuckerwerte")
        st.table(pd.DataFrame(st.session_state['daten']).drop(columns=['zeitpunkt'], errors='ignore'))
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

# 🔄 Seitenwechsel-Logik
if "seite" not in st.session_state:
    st.session_state.seite = "Startseite"

if st.session_state.seite == "Startseite":
    startseite()
elif st.session_state.seite == "Blutzucker-Tracker":
    blutzucker_tracker()
elif st.session_state.seite == "Blutzucker-Werte":
    blutzucker_werte()
elif st.session_state.seite == "Blutzucker-Grafik":
    blutzucker_grafik()
