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
data_manager = DataManager(fs_protocol='webdav', fs_root_folder="BMLD_cblsf_App")
if f"user_data_{username}" not in st.session_state:
    st.session_state[f"user_data_{username}"] = data_manager.load_user_data(
        session_state_key=f"user_data_{username}",
        username=username,
        parse_dates=["datum_zeit"]
    )

user_data = st.session_state[f"user_data_{username}"]

st.markdown("## 📊 Blutzucker-Grafik")

if not user_data.empty:
    st.markdown("### Verlauf der Blutzuckerwerte")
    chart_data = user_data.set_index("datum_zeit")[["blutzuckerwert"]]
    st.line_chart(chart_data)
else:
    st.warning("Noch keine Daten vorhanden.")