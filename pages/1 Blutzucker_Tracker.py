import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd
from utils.data_manager import DataManager
from utils.login_manager import LoginManager

# ✅ MUSS erstes Kommando bleiben!
st.set_page_config(page_title="🩸 Blutzucker Tracker", layout="wide")

# ====== Login-Check ======
data_manager = DataManager(fs_protocol='webdav', fs_root_folder="BMLD_cblsf_App")
login_manager = LoginManager(data_manager)
login_manager.go_to_login('Start.py')

# 📌 Nutzername holen
username = st.session_state.get("username")

if not username:
    st.error("⚠️ Kein Benutzer eingeloggt! Anmeldung erforderlich.")
    st.stop()

# 📌 Benutzerspezifische Daten laden
if "user_data" not in st.session_state:
    st.session_state.user_data = data_manager.load_user_data(
        session_state_key="user_data",
        username=username,  # 🔥 Jeder Benutzer bekommt seine eigene Datei
        initial_value=pd.DataFrame(columns=["datum_zeit", "blutzuckerwert", "zeitpunkt"]),
        parse_dates=["datum_zeit"]
    )

user_data = st.session_state.user_data

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

# 🔥 Blutzucker-Tracker
st.markdown("## 🩸 Blutzucker-Tracker")

with st.form(key='blutzucker_form'):
    blutzuckerwert = st.number_input("📌 Blutzuckerwert (mg/dL)", min_value=1, step=1)  # 🔥 Keine 0-Werte!
    zeitpunkt = st.selectbox(" Zeitpunkt", ["Nüchtern", "Nach dem Essen"])
    submit_button = st.form_submit_button(label="✅ Eintrag hinzufügen")

if submit_button:
    datum_zeit = datetime.now(ZoneInfo("Europe/Zurich")).strftime("%Y-%m-%d %H:%M:%S")  # Einheitliches Datum-Format
    new_entry = pd.DataFrame([{ "datum_zeit": datum_zeit, "blutzuckerwert": blutzuckerwert, "zeitpunkt": zeitpunkt }])
    
    st.session_state.user_data = pd.concat([st.session_state.user_data, new_entry], ignore_index=True)

    # ✅ Nur speichern, wenn gültige Daten vorhanden sind
    if not st.session_state.user_data.empty:
        data_manager.save_user_data("user_data", username)
        st.success(f"✅ Eintrag gespeichert für {username}!")
    else:
        st.warning("⚠️ Keine gültigen Daten zum Speichern!")

    st.rerun()

# 📌 Gespeicherte Werte anzeigen
if not user_data.empty:
    st.markdown("###  Gespeicherte Blutzuckerwerte")
    user_data["datum_zeit"] = pd.to_datetime(user_data["datum_zeit"], errors='coerce')  # Falls nötig, konvertieren
    st.table(user_data.drop(columns=["username"], errors="ignore").reset_index(drop=True))

    durchschnitt = user_data["blutzuckerwert"].mean()
    st.markdown(f"** Durchschnittlicher Blutzuckerwert:** {durchschnitt:.2f} mg/dL")
else:
    st.warning("⚠️ Noch keine Werte gespeichert. Bitte einen neuen Wert eingeben.")

# 🔥 Blutzucker-Grafik
def blutzucker_grafik():
    st.markdown("## 📊 Blutzucker-Grafik")

    if not user_data.empty:
        st.markdown("###  Verlauf der Blutzuckerwerte")

        # 🔥 Falls `datum_zeit` nicht als `Datetime` erkannt wird, umwandeln
        if not pd.api.types.is_datetime64_any_dtype(user_data["datum_zeit"]):
            user_data["datum_zeit"] = pd.to_datetime(user_data["datum_zeit"], errors='coerce')

        # 🔥 Setze `datum_zeit` als Index für das Diagramm
        chart_data = user_data.set_index("datum_zeit")[["blutzuckerwert"]]

        if len(chart_data) > 1:
            st.line_chart(chart_data)
        else:
            st.warning("⚠️ Mindestens zwei Werte erforderlich, um eine Grafik darzustellen.")
    else:
        st.warning("⚠️ Noch keine Werte vorhanden. Bitte geben Sie einen neuen Wert ein.")


# 🔄 Seitenwechsel
if "seite" not in st.session_state:
    st.session_state.seite = "Startseite"

if st.session_state.seite == "Blutzucker-Tracker":
    blutzucker_tracker()
elif st.session_state.seite == "Startseite":
    startseite()
elif st.session_state.seite == "Blutzucker-Werte":
    blutzucker_werte()
elif st.session_state.seite == "Blutzucker-Grafik":
    blutzucker_grafik()

