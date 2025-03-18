import streamlit as st
from utils.data_manager import DataManager

# ====== Login Block ======
from utils.login_manager import LoginManager
login_manager = LoginManager()
login_manager.go_to_login('Start.py')
# ====== End Login Block ======

# Nutzername aus dem Session-State holen
username = st.session_state.get("username")

if not username:
    st.error("Kein Benutzer eingeloggt. Anmeldung erforderlich.")
    st.stop()

# Datenbank für den Nutzer laden
data_manager = DataManager(fs_protocol='webdav', fs_root_folder="BMLD_cpblsf_App")
if f"user_data_{username}" not in st.session_state:
    st.session_state[f"user_data_{username}"] = data_manager.load_user_data(
        session_state_key=f"user_data_{username}",
        username=username,
        parse_dates=["datum_zeit"]
    )

user_data = st.session_state[f"user_data_{username}"]

st.markdown("## 📋 Blutzucker-Werte")

if not user_data.empty:
    st.markdown("### Gespeicherte Blutzuckerwerte")
    renamed_data = user_data.rename(columns={
        "datum_zeit": "Datum & Zeit",
        "blutzuckerwert": "Blutzuckerwert (mg/dL)",
        "zeitpunkt": "Zeitpunkt"
    })
    st.table(renamed_data[["Datum & Zeit", "Blutzuckerwert (mg/dL)", "Zeitpunkt"]])

    durchschnitt = user_data["blutzuckerwert"].mean()
    st.markdown(f"**Durchschnittlicher Blutzuckerwert:** {durchschnitt:.2f} mg/dL")
else:
    st.warning("Noch keine Daten vorhanden.")