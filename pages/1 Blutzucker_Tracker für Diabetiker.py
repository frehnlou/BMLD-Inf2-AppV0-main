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
    st.markdown("## 🩸 Blutzucker-Tracker")
    
    # Eingabeformular für Blutzuckerwerte
    with st.form(key='blutzucker_form'):
        blutzuckerwert = st.number_input("Gib deinen Blutzuckerwert ein", min_value=0, step=1)
        zeitpunkt = st.selectbox("Zeitpunkt", ["Nüchtern", "Nach dem Essen"])
        submit_button = st.form_submit_button(label='Eintrag hinzufügen')
    
    # Session-State für die Speicherung von Daten
    if 'daten' not in st.session_state:
        st.session_state['daten'] = []

    if submit_button:
        datum_zeit = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state['daten'].append({
            "blutzuckerwert": blutzuckerwert,
            "zeitpunkt": zeitpunkt,
            "datum_zeit": datum_zeit
        })
        st.success("Eintrag erfolgreich hinzugefügt")

    if st.session_state['daten']:
        st.markdown("### Letzter Eintrag")
        
        # Anzeige des letzten Eintrags
        letzter_eintrag = st.session_state['daten'][-1]
        st.write(f"Ihr Blutzuckerwert ist: {letzter_eintrag['blutzuckerwert']} mg/dL")
        st.write(f"Messzeitpunkt: {letzter_eintrag['zeitpunkt']}")
        st.write(f"Berechnet am: {letzter_eintrag['datum_zeit']}")

        # Durchschnitt berechnen
        durchschnitt = sum(d['blutzuckerwert'] for d in st.session_state['daten']) / len(st.session_state['daten'])
        st.markdown(f"**Durchschnittlicher Blutzuckerwert:** {durchschnitt:.2f} mg/dL")

        # Löschfunktion für Einträge
        st.markdown("### Eintrag löschen")
        index_to_delete = st.number_input("Index des zu löschenden Eintrags", min_value=1, max_value=len(st.session_state['daten']), step=1) - 1
        if st.button("Eintrag löschen"):
            if 0 <= index_to_delete < len(st.session_state['daten']):
                del st.session_state['daten'][index_to_delete]
                st.success("Eintrag erfolgreich gelöscht")
                st.experimental_rerun()

def blutzucker_werte():
    st.markdown("## 📋 Blutzucker-Werte")
    
    if 'daten' in st.session_state and st.session_state['daten']:
        st.markdown("### Alle gespeicherten Werte")
        
        # Tabelle der Daten
        daten = st.session_state['daten']
        st.table(daten)
    else:
        st.warning("Noch keine Daten vorhanden.")

# Session-State zur Steuerung der Navigation
if "seite" not in st.session_state:
    st.session_state.seite = "Startseite"

# Auswahl der aktuellen Seite
if st.session_state.seite == "Startseite":
    startseite()
elif st.session_state.seite == "Blutzucker-Tracker":
    blutzucker_tracker()
elif st.session_state.seite == "Blutzucker-Werte":
    blutzucker_werte()