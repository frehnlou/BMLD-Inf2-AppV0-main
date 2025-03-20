import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd
from utils.data_manager import DataManager
from utils.login_manager import LoginManager
import os

# Seitenkonfiguration
st.set_page_config(page_title="Blutzucker Tracker", layout="wide")

# ====== Login-Check ======
LoginManager().go_to_login('Start.py')

# Nutzername aus dem Session-State holen
username = st.session_state.get("username")

if not username:
    st.error("⚠️ Kein Benutzer eingeloggt! Anmeldung erforderlich.")
    st.stop()

# ====== Navigation ======
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

# ====== Startseite ======
def startseite():
    st.markdown("## 🏠 Willkommen auf der Startseite!")
    st.write("""
    Liebe Diabetikerinnen und Diabetiker 🩸

    Mit dieser App können Sie:
    - Ihre Blutzuckerwerte einfach eingeben und speichern.
    - Den Messzeitpunkt auswählen (z. B. Nüchtern oder nach dem Essen).
    - Ihre Werte in einer übersichtlichen Tabelle anzeigen lassen.
    - Den Durchschnitt Ihrer Blutzuckerwerte berechnen.
    - Ihre Werte in einer anschaulichen Grafik analysieren.

    Behalten Sie Ihre Gesundheit im Blick und erkennen Sie langfristige Muster!
    """)

# ====== Blutzucker-Tracker ======
def blutzucker_tracker():
    st.markdown("## 🩸 Blutzucker-Tracker")

    # Eingabemaske für Blutzuckerwerte
    with st.form(key='blutzucker_form'):
        blutzuckerwert = st.number_input("Blutzuckerwert (mg/dL)", min_value=0, step=1)
        zeitpunkt = st.selectbox("Zeitpunkt", ["Nüchtern", "Nach dem Essen"])
        submit_button = st.form_submit_button(label='Eintrag hinzufügen')

    if submit_button:
        datum_zeit = datetime.now(ZoneInfo("Europe/Zurich")).strftime("%Y-%m-%d %H:%M:%S")
        new_entry = {
            "datum_zeit": datum_zeit,
            "blutzuckerwert": blutzuckerwert,
            "zeitpunkt": zeitpunkt
        }

        st.success("Eintrag erfolgreich hinzugefügt!")

        # Aktualisiere den DataFrame und speichere die Daten

        #st.write(st.session_state)
        #st.write(new_entry)
        DataManager().append_record(session_state_key='data_df', record_dict=new_entry)
        #st.write(st.session_state)


# ====== Blutzucker-Werte ======
def blutzucker_werte():
    st.markdown("## 📋 Blutzucker-Werte")

    if "data_df" not in st.session_state:
        st.warning("Noch keine Werte gespeichert.")
    else:
        st.markdown("### Gespeicherte Blutzuckerwerte")
        renamed_data = st.session_state["data_df"].rename(columns={
            "datum_zeit": "Datum & Uhrzeit",
            "blutzuckerwert": "Blutzuckerwert (mg/dL)",
            "zeitpunkt": "Zeitpunkt"
        })
        st.table(renamed_data[["Datum & Uhrzeit", "Blutzuckerwert (mg/dL)", "Zeitpunkt"]])

        durchschnitt = st.session_state["data_df"]["blutzuckerwert"].mean()
        st.markdown(f"**Durchschnittlicher Blutzuckerwert:** {durchschnitt:.2f} mg/dL")

# ====== Blutzucker-Grafik ======
def blutzucker_grafik():
    st.markdown("## 📊 Blutzucker-Grafik")

    if st.session_state["data_df"]:
        st.warning("Noch keine Werte vorhanden.")
    else:
        st.markdown("### Verlauf der Blutzuckerwerte")
        chart_data = st.session_state["data_df"].set_index("datum_zeit")[["blutzuckerwert"]]
        st.line_chart(chart_data)

# ====== Seitenwechsel ======
if "seite" not in st.session_state:
    st.session_state.seite = "Startseite"  # Standardseite ist die Startseite

# Seitenlogik
if st.session_state.seite == "Startseite":
    startseite()
elif st.session_state.seite == "Blutzucker-Tracker":
    blutzucker_tracker()
elif st.session_state.seite == "Blutzucker-Werte":
    blutzucker_werte()
elif st.session_state.seite == "Blutzucker-Grafik":
    blutzucker_grafik()