import streamlit as st
from utils.login_manager import LoginManager
from utils.data_manager import DataManager

# ====== Login Block ======
login_manager = LoginManager()
login_manager.go_to_login('Start.py')
# ====== End Login Block ======

# Überschrift
st.markdown("## 📊 Blutzucker-Grafik")

# Nutzername aus dem Session-State holen
username = st.session_state.get("username")

if not username:
    st.error("Kein Benutzer eingeloggt. Anmeldung erforderlich.")
    st.stop()

# Datenbank für den Nutzer laden
data_manager = DataManager(fs_protocol='webdav', fs_root_folder="BMLD_cblsf_App")

try:
    user_data = data_manager.load_user_data(
        session_state_key="user_data",
        username=username,
        parse_dates=["datum_zeit"]
    )
except Exception as e:
    st.error(f"Fehler beim Laden der Daten: {e}")
    st.stop()

if not user_data.empty:
    st.markdown("### Verlauf der Blutzuckerwerte")

    # Sicherstellen, dass die benötigten Spalten existieren
    if all(col in user_data.columns for col in ["datum_zeit", "blutzuckerwert"]):
        try:
            # Werte extrahieren
            blutzuckerwerte = user_data[["datum_zeit", "blutzuckerwert"]].set_index("datum_zeit")

            # Überprüfung: Mindestens zwei Datenpunkte nötig für eine Linie
            if len(blutzuckerwerte) > 1:
                st.line_chart(blutzuckerwerte)
            else:
                st.warning("Mindestens zwei Werte erforderlich, um eine Grafik darzustellen.")
        except Exception as e:
            st.error(f"Fehler bei der Grafikerstellung: {e}")
    else:
        st.warning("Datenformat fehlerhaft oder Spalten fehlen.")
else:
    st.warning("Noch keine Daten vorhanden. Bitte fügen Sie Blutzuckerwerte hinzu.")

# Hinweis für Benutzer
st.info("Sie können Blutzuckerwerte im 'Blutzucker-Tracker' hinzufügen.")