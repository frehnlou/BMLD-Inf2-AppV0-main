import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd
from utils.data_manager import DataManager
from utils.login_manager import LoginManager

# Seitenkonfiguration
st.set_page_config(page_title="Blutzucker Tracker", layout="wide")

# ====== Login-Check ======
data_manager = DataManager(fs_protocol='webdav', fs_root_folder="BMLD_cblsf_App")
login_manager = LoginManager(data_manager)
login_manager.go_to_login('Start.py')

# Nutzername aus dem Session-State holen
username = st.session_state.get("username")

if not username:
    st.error("Kein Benutzer eingeloggt. Anmeldung erforderlich.")
    st.stop()

# Benutzerspezifische Daten initialisieren
if f"user_data_{username}" not in st.session_state:
    # Lade die Daten des aktuellen Benutzers oder initialisiere sie, falls keine vorhanden sind
    st.session_state[f"user_data_{username}"] = data_manager.load_user_data(
        session_state_key=f"user_data_{username}",
        username=username,
        initial_value=pd.DataFrame(columns=["datum_zeit", "blutzuckerwert", "zeitpunkt"]),
        parse_dates=["datum_zeit"]
    )

# Zugriff auf die Benutzerdaten
user_data = st.session_state[f"user_data_{username}"]

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
    Liebe Diabetikerinnen und Diabetiker 🩸,

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
        new_entry = pd.DataFrame([{
            "datum_zeit": datum_zeit,
            "blutzuckerwert": blutzuckerwert,
            "zeitpunkt": zeitpunkt
        }])

        # Aktualisiere die Daten im Session-State
        st.session_state[f"user_data_{username}"] = pd.concat([st.session_state[f"user_data_{username}"], new_entry], ignore_index=True)

        # Speichere die Daten für den aktuellen Benutzer
        try:
            data_manager.save_user_data(
                session_state_key=f"user_data_{username}",
                username=username
            )
            st.success("Eintrag erfolgreich hinzugefügt!")
        except Exception as e:
            st.error(f"Fehler beim Speichern der Daten: {e}")

    # Zeige die gespeicherten Werte an (ohne Spaltenüberschriften)
    if not user_data.empty:
        st.markdown("### Gespeicherte Blutzuckerwerte")
        # Entferne die Spaltenüberschriften
        table_data = user_data.reset_index(drop=True).to_numpy().tolist()
        st.table(table_data)

        durchschnitt = user_data["blutzuckerwert"].mean()
        st.markdown(f"**Durchschnittlicher Blutzuckerwert:** {durchschnitt:.2f} mg/dL")
    else:
        st.warning("Noch keine Daten vorhanden.")

# ====== Blutzucker-Werte ======
def blutzucker_werte():
    st.markdown("## 📋 Blutzucker-Werte")

    # Zugriff auf die Benutzerdaten
    user_data = st.session_state[f"user_data_{username}"]

    if not user_data.empty:
        st.markdown("### Gespeicherte Blutzuckerwerte")
        # Benutzerdefinierte Spaltenüberschriften
        renamed_data = user_data.rename(columns={
            "blutzuckerwert": "1: Blutzuckerwerte",
            "zeitpunkt": "2: Nüchtern"
        })
        # Zeige die Tabelle mit den neuen Spaltenüberschriften
        st.table(renamed_data[["1: Blutzuckerwerte", "2: Nüchtern"]])
    else:
        st.warning("Noch keine Werte gespeichert.")

# ====== Blutzucker-Grafik ======
def blutzucker_grafik():
    st.markdown("## 📊 Blutzucker-Grafik")

    # Zugriff auf die Benutzerdaten
    user_data = st.session_state[f"user_data_{username}"]

    if not user_data.empty:
        st.markdown("### Verlauf der Blutzuckerwerte")
        chart_data = user_data.set_index("datum_zeit")[["blutzuckerwert"]]
        st.line_chart(chart_data)
    else:
        st.warning("Noch keine Werte vorhanden.")

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