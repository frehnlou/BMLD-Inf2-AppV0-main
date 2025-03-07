import streamlit as st
import pandas as pd

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
    blutzuckerwert = st.number_input("Gib deinen Blutzuckerwert ein", min_value=0)
    zeitpunkt = st.selectbox("Zeitpunkt", ["Nüchtern", "Nach dem Essen"])
    
    if 'daten' not in st.session_state:
        st.session_state['daten'] = []

    if st.button("Eintrag hinzufügen"):
        st.session_state['daten'].append({"blutzuckerwert": blutzuckerwert, "zeitpunkt": zeitpunkt})
        st.success("Eintrag erfolgreich hinzugefügt")
        
        # Tipps basierend auf dem Blutzuckerwert
        if blutzuckerwert < 70:
            st.warning("Dein Blutzuckerwert ist niedrig. Es wird empfohlen, schnell wirkende Kohlenhydrate wie Saft oder Traubenzucker zu dir zu nehmen.")
        elif blutzuckerwert > 180:
            st.warning("Dein Blutzuckerwert ist erhöht. Es wird empfohlen, deinen Blutzucker regelmäßig zu überwachen und gegebenenfalls Insulin zu verabreichen.")
        
    if st.session_state['daten']:
        df = pd.DataFrame(st.session_state['daten'])
        st.write(df)
        
        fig, ax = plt.subplots()
        for label, df_group in df.groupby("zeitpunkt"):
            df_group.plot(x="zeitpunkt", y="blutzuckerwert", ax=ax, label=label, marker='o')
        st.pyplot(fig)
# Sidebar for navigation
st.sidebar.title("Navigation")
wahl = st.sidebar.radio("Gehe zu", ["Startseite", "Blutzucker-Tracker"])

# Display the selected page
if wahl == "Startseite":
    startseite()
elif wahl == "Blutzucker-Tracker":
    blutzucker_tracker()