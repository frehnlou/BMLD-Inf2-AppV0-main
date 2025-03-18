import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd
from utils.data_manager import DataManager
from utils.login_manager import LoginManager

# ✅ MUSS erstes Kommando bleiben!
st.set_page_config(page_title="Blutzucker Tracker", layout="wide")

# ====== Login-Check ======
data_manager = DataManager(fs_protocol='webdav', fs_root_folder="BMLD_cblsf_App")
login_manager = LoginManager(data_manager)
login_manager.go_to_login('Start.py')

# 📌 Nutzername holen
username = st.session_state.get("username")
if not username:
    st.error("⚠️ Kein Benutzer eingeloggt! Anmeldung erforderlich.")
    st.stop()

# 📌 Benutzerspezifische Daten laden (stellen sicher, dass nach Logout die Daten noch da sind)
if "user_data" not in st.session_state:
    st.session_state.user_data = data_manager.load_user_data(
        session_state_key="user_data",
        username=username,
        initial_value=pd.DataFrame(columns=["datum_zeit", "blutzuckerwert", "zeitpunkt"]),
        parse_dates=["datum_zeit"]
    )

user_data = st.session_state.user_data

# ====== Navigation ======
col1, col2, col3, col4 = st.columns(4)

def save_and_switch_page(page):
    """ Speichert die Daten und wechselt zur anderen Seite """
    if "user_data" in st.session_state:
        data_manager.save_user_data("user_data", username)  # 🔥 Speichert vor Seitenwechsel
    st.session_state.seite = page
    st.rerun()  # 🔄 Aktualisiert die Seite nach dem Speichern

with col1:
    if st.button("🏠 Startseite"):
        save_and_switch_page("Startseite")

with col2:
    if st.button("🩸 Blutzucker-Tracker"):
        save_and_switch_page("Blutzucker-Tracker")

with col3:
    if st.button("📋 Blutzucker-Werte"):
        save_and_switch_page("Blutzucker-Werte")

with col4:
    if st.button("📊 Blutzucker-Grafik"):
        save_and_switch_page("Blutzucker-Grafik")

# 🔥 Blutzucker-Tracker
def blutzucker_tracker():
    st.markdown("## 🩸 Blutzucker-Tracker")

    with st.form(key='blutzucker_form'):
        blutzuckerwert = st.number_input("Blutzuckerwert (mg/dL)", min_value=0, step=1)
        zeitpunkt = st.selectbox("Zeitpunkt", ["Nüchtern", "Nach dem Essen"])
        submit_button = st.form_submit_button(label=' Eintrag hinzufügen')

    if submit_button:
        datum_zeit = datetime.now(ZoneInfo("Europe/Zurich")).strftime("%Y-%m-%d %H:%M:%S")
        new_entry = pd.DataFrame([{ "datum_zeit": datum_zeit, "blutzuckerwert": blutzuckerwert, "zeitpunkt": zeitpunkt }])
        st.session_state.user_data = pd.concat([st.session_state.user_data, new_entry], ignore_index=True)

        # ✅ Speichert die Werte nur für den aktuellen Benutzer
        data_manager.save_user_data("user_data", username)

        st.success("✅ Eintrag hinzugefügt!")
        st.rerun()

    if not user_data.empty:
        st.markdown("###  Gespeicherte Blutzuckerwerte")
        st.table(user_data)

        durchschnitt = user_data["blutzuckerwert"].mean()
        st.markdown(f" **Durchschnittlicher Blutzuckerwert:** {durchschnitt:.2f} mg/dL")
    else:
        st.warning("Noch keine Werte vorhanden.")

# 🔥 Blutzucker-Werte
def blutzucker_werte():
    st.markdown("## 📋 Blutzucker-Werte")

    if not user_data.empty:
        st.markdown("###  Gespeicherte Blutzuckerwerte")
        st.table(user_data)
    else:
        st.warning("Noch keine Werte gespeichert.")

# 🔥 Blutzucker-Grafik
def blutzucker_grafik():
    st.markdown("## 📊 Blutzucker-Grafik")

    if not user_data.empty:
        st.markdown("###  Verlauf der Blutzuckerwerte")
        user_data["datum_zeit"] = pd.to_datetime(user_data["datum_zeit"], errors='coerce')
        chart_data = user_data.set_index("datum_zeit")[["blutzuckerwert"]]
        if len(chart_data) > 1:
            st.line_chart(chart_data)
        else:
            st.warning("⚠️ Mindestens zwei Werte erforderlich, um eine Grafik darzustellen.")
    else:
        st.warning("Noch keine Werte vorhanden.")

# 🔄 Seitenwechsel
if "seite" not in st.session_state:
    st.session_state.seite = "Startseite"

if st.session_state.seite == "Blutzucker-Tracker":
    blutzucker_tracker()
elif st.session_state.seite == "Startseite":
    st.markdown("## 🏠 Willkommen auf der Startseite!")
elif st.session_state.seite == "Blutzucker-Werte":
    blutzucker_werte()
elif st.session_state.seite == "Blutzucker-Grafik":
    blutzucker_grafik()
