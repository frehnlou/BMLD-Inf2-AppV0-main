import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd
from utils.data_manager import DataManager
from utils.login_manager import LoginManager

# ✅ MUSS als erstes stehen
st.set_page_config(page_title="Blutzucker Tracker", layout="wide")

# ====== Login-Check ======
data_manager = DataManager(fs_protocol='webdav', fs_root_folder="BMLD_cblsf_App")
login_manager = LoginManager(data_manager)
login_manager.go_to_login('Start.py')

# 🔹 Navigation
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

#Nutzername holen
username = st.session_state.get("username", "Gast")

#Daten laden
user_data = data_manager.load_user_data(
    session_state_key="user_data",
    file_name="data.csv",
    initial_value=pd.DataFrame(columns=["datum_zeit", "blutzuckerwert", "zeitpunkt"]),
    parse_dates=["datum_zeit"]
)

#Startseite
def startseite():
    st.markdown("## 🏠 Willkommen auf der Startseite!")
    st.write("""
    Liebe Diabetikerinnen und Diabetiker! 🩸

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

# Blutzucker-Tracker
def blutzucker_tracker():
    global user_data

    st.markdown("## 🩸 Blutzucker-Tracker")

    with st.form(key='blutzucker_form'):
        blutzuckerwert = st.number_input("Blutzuckerwert (mg/dL)", min_value=0, step=1)
        zeitpunkt = st.selectbox("Zeitpunkt", ["Nüchtern", "Nach dem Essen"])
        submit_button = st.form_submit_button(label='Eintrag hinzufügen')

    if submit_button:
        datum_zeit = datetime.now(ZoneInfo("Europe/Zurich")).strftime("%Y-%m-%d %H:%M:%S")
        result = {
            "datum_zeit": datum_zeit,
            "blutzuckerwert": blutzuckerwert,
            "zeitpunkt": zeitpunkt
        }
        data_manager.append_record("user_data", result)
        st.success("✅ Eintrag wurde gespeichert.")
        st.rerun()

    #  Daten filtern & anzeigen
    if not user_data.empty:
        st.markdown("### Gespeicherte Blutzuckerwerte")
        st.dataframe(user_data[["datum_zeit", "blutzuckerwert", "zeitpunkt"]])

        durchschnitt = user_data["blutzuckerwert"].mean()
        st.markdown(f"**Durchschnittlicher Blutzuckerwert:** {durchschnitt:.2f} mg/dL")
    else:
        st.warning("Noch keine Daten vorhanden.")
    
    # Löschoption für Einträge
    st.markdown("### Eintrag löschen")
    with st.form(key='delete_form'):
        index_to_delete = st.number_input("Index des zu löschenden Eintrags", min_value=0, max_value=len(user_data)-1 if not user_data.empty else 0, step=1)
        delete_button = st.form_submit_button(label='Eintrag löschen')
    
    if delete_button and not user_data.empty:
        user_data = user_data.drop(index=index_to_delete).reset_index(drop=True)
        data_manager.save_data("user_data")
        st.success("🗑️ Eintrag erfolgreich gelöscht.")
        st.rerun()

# Seitenwechsel OHNE `st.switch_page()`
if "seite" not in st.session_state:
    st.session_state.seite = "Startseite"

if st.session_state.seite == "Blutzucker-Tracker":
    blutzucker_tracker()
elif st.session_state.seite == "Startseite":
    startseite()
