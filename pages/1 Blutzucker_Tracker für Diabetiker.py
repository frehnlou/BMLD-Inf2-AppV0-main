import streamlit as st
from datetime import datetime

# Abstand nach oben für bessere Platzierung
st.markdown("<br>", unsafe_allow_html=True)

# Vier Spalten für die Buttons
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🏠 Startseite"):
        st.session_state.seite = "Startseite"

with col2:
    if st.button(" 🩸 Blutzucker-Tracker"):
        st.session_state.seite = "Blutzucker-Tracker"

with col3:
    if st.button(" 📋 Blutzucker-Werte"):
        st.session_state.seite = "Blutzucker-Werte"

with col4:
    if st.button(" 📊 Blutzucker-Grafik"):
        st.session_state.seite = "Blutzucker-Grafik"

def startseite():
    st.markdown("## 🏠 Willkommen auf der Startseite!")
    st.write("""
    Liebe Diabetikerinnen und Diabetiker!🩸

    Kennst du das Problem, den Überblick über deine Blutzuckerwerte zu behalten? Mit unserem Blutzucker-Tracker kannst du deine Werte einfach eingeben, speichern und analysieren – alles an einem Ort!

    - Was bringt dir die App?
    - Schnelle Eingabe deines Blutzuckers (mg/dL)
    - Messzeitpunkt wählen (Nüchtern oder nach dem Essen)
    - Automatische Übersicht in einer Tabelle, damit du deine Werte immer im Blick hast
    - Anschauliche Diagramme, die deine Blutzuckerwerte visuell auswerten

    Warum diese App?
             
    ✔ Kein lästiges Papier-Tagebuch mehr

    ✔ Verfolge deine Werte langfristig & erkenne Muster

    ✔ Bessere Kontrolle für ein gesünderes Leben mit Diabetes

    Einfach testen & deine Blutzuckerwerte im Blick behalten! 🏅
    """)

def blutzucker_tracker():
    st.markdown("## 🩸Blutzucker-Tracker")
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
        st.write(st.session_state['daten'])
        
        # Anzeige des letzten Eintrags
        letzter_eintrag = st.session_state['daten'][-1]
        st.write("Letzter Eintrag:")
        st.write(f"Blutzuckerwert = {letzter_eintrag['blutzuckerwert']}")
        st.write(f"Zeitpunkt = {letzter_eintrag['zeitpunkt']}")
        st.write(f"Datum & Zeit = {letzter_eintrag['datum_zeit']}")
        
        # Berechnung des Durchschnitts
        durchschnitt = sum(d['blutzuckerwert'] for d in st.session_state['daten']) / len(st.session_state['daten'])
        st.write(f"Durchschnittlicher Blutzuckerwert: {durchschnitt:.2f} mg/dL")
        
        # Löschfunktion
        st.write("### Eintrag löschen")
        index_to_delete = st.number_input("Index des zu löschenden Eintrags", min_value=0, max_value=len(st.session_state['daten'])-1, step=1)
        if st.button("Eintrag löschen"):
            del st.session_state['daten'][index_to_delete]
            st.success("Eintrag erfolgreich gelöscht")
            st.experimental_rerun()

def blutzucker_werte():
    st.markdown("## 📋 Blutzucker-Werte")
    if 'daten' in st.session_state and st.session_state['daten']:
        st.write(st.session_state['daten'])
    else:
        st.write("Keine Daten vorhanden.")

def blutzucker_grafik():
    st.markdown("## 📊 Blutzucker-Grafik")
    if 'daten' in st.session_state and st.session_state['daten']:
        daten = st.session_state['daten']
        daten.sort(key=lambda x: x['datum_zeit'])
        blutzuckerwerte = [d['blutzuckerwert'] for d in daten]
        datum_zeiten = [d['datum_zeit'] for d in daten]
        st.line_chart({"Datum & Zeit": datum_zeiten, "Blutzuckerwert": blutzuckerwerte})
    else:
        st.write("Keine Daten vorhanden.")

# Session-State zur Steuerung der Ansicht
if "seite" not in st.session_state:
    st.session_state.seite = "Startseite"

# Anzeige der gewählten Seite
if st.session_state.seite == "Startseite":
    startseite()
elif st.session_state.seite == "Blutzucker-Tracker":
    blutzucker_tracker()
elif st.session_state.seite == "Blutzucker-Werte":
    blutzucker_werte()
elif st.session_state.seite == "Blutzucker-Grafik":
    blutzucker_grafik()