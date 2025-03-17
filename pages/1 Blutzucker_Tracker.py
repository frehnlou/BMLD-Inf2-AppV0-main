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

# 🔹 Navigation (GENAU SO GELASSEN WIE GEWÜNSCHT)
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

# 📌 Nutzername holen (GENAU SO GELASSEN WIE GEWÜNSCHT)
username = st.session_state.get("username", "Gast")

# 📌 Daten laden
user_data = data_manager.load_user_data(
    session_state_key="user_data",
    file_name="data.csv",
    initial_value=pd.DataFrame(columns=["datum_zeit", "blutzuckerwert", "zeitpunkt"]),
    parse_dates=["datum_zeit"]
)

# 🔥 Startseite (Aktualisiert)
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

# 🔥 Blutzucker-Tracker (GENAU SO GELASSEN, aber Tabelle verbessert)
def blutzucker_tracker():
    st.markdown("## 🩸 Blutzucker-Tracker")

    with st.form(key='blutzucker_form'):
        blutzuckerwert = st.number_input("Blutzuckerwert (mg/dL)", min_value=0, step=1)
        zeitpunkt = st.selectbox("Zeitpunkt", ["Nüchtern", "Nach dem Essen"])
        submit_button = st.form_submit_button(label='Eintrag hinzufügen')

    if submit_button:
        datum_zeit = datetime.now(ZoneInfo("Europe/Zurich")).strftime("%Y-%m-%d %H:%M:%S")
        result = {
            "blutzuckerwert": blutzuckerwert,
            "zeitpunkt": zeitpunkt,
            "datum_zeit": datum_zeit
        }
        data_manager.append_record("data.csv", result)
        st.success("✅ Eintrag wurde gespeichert.")
        st.rerun()

    # 📌 Daten filtern NUR für den aktuellen Benutzer
    if not user_data.empty:
        st.markdown("### Gespeicherte Blutzuckerwerte")
        st.dataframe(user_data.style.set_properties(**{'text-align': 'left'}))

        durchschnitt = user_data["blutzuckerwert"].mean()
        st.markdown(f"<span style='background-color:#d4edda; color:#155724; padding:5px; border-radius:5px;'>Durchschnittlicher Wert: {durchschnitt:.2f} mg/dL</span>", unsafe_allow_html=True)
    else:
        st.warning("Noch keine Daten vorhanden.")

# 🔥 Blutzucker-Werte (Tabelle verbessert)
def blutzucker_werte():
    st.markdown("## Blutzucker-Werte")

    if not user_data.empty:
        st.markdown("### Gespeicherte Blutzuckerwerte")
        st.dataframe(user_data.style.set_properties(**{'text-align': 'left'}))
    else:
        st.warning("Noch keine Werte gespeichert.")

# 🔥 Blutzucker-Grafik (Keine Änderung nötig)
def blutzucker_grafik():
    st.markdown("## Blutzucker-Grafik")

    if not user_data.empty:
        st.markdown("### Verlauf der Blutzuckerwerte")
        chart_data = user_data.set_index("datum_zeit")[["blutzuckerwert"]]
        st.line_chart(chart_data)
    else:
        st.warning("Noch keine Werte vorhanden.")

# 🔄 Seitenwechsel OHNE `st.switch_page()` (GENAU SO GELASSEN)
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
