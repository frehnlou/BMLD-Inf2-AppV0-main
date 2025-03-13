import streamlit as st
from datetime import datetime
from utils.data_manager import DataManager

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
    st.write("Hier können Sie Ihre Blutzuckerwerte verwalten und neue Werte eingeben.")
    
    if "daten" not in st.session_state:
        st.session_state.daten = []
    
    blutzuckerwert = st.number_input("Blutzuckerwert eingeben:", min_value=0.0, max_value=500.0, step=0.1)
    
    if st.button("Speichern"):
        st.session_state.daten.append({"blutzuckerwert": blutzuckerwert})
        st.success("Blutzuckerwert gespeichert!")
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    if col1.button("Blutzucker-Werte anzeigen"):
        st.session_state.seite = "Blutzucker-Werte"
    if col2.button("Blutzucker-Grafik anzeigen"):
        st.session_state.seite = "Blutzucker-Grafik"
    if col3.button("Zurück zur Startseite"):
        st.session_state.seite = "Startseite"
