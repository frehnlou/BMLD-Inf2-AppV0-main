import streamlit as st
from utils.data_manager import DataManager
from utils.login_manager import LoginManager

# ✅ Direkt zur Login-Seite
st.set_page_config(page_title="Blutzucker Tracker", layout="wide")

# ✅ Initialisiere DataManager
data_manager = DataManager(fs_protocol='webdav', fs_root_folder="BMLD_cblsf_App")

# ✅ Initialisiere LoginManager
login_manager = LoginManager(data_manager)
login_manager.login_register()

# Falls der Benutzer nicht eingeloggt ist, stoppe den weiteren Code
if "authentication_status" not in st.session_state or not st.session_state["authentication_status"]:
    st.stop()

# 📌 Nutzername holen
username = st.session_state.get("username")

# ✅ Daten des Nutzers laden
if "user_data" not in st.session_state:
    st.session_state.user_data = data_manager.load_user_data(
        session_state_key="user_data",
        username=username,
        initial_value=pd.DataFrame(columns=["datum_zeit", "blutzuckerwert", "zeitpunkt"]),
        parse_dates=["datum_zeit"]
    )

# ====== Startseite nach erfolgreicher Anmeldung ======
st.markdown("## 🩸 Blutzucker-Tracker für Diabetiker")

st.write("""
Willkommen zum Blutzucker-Tracker! Diese App unterstützt Sie dabei, Ihre Blutzuckerwerte einfach zu erfassen, zu speichern und zu analysieren. So behalten Sie Ihre Werte stets im Blick und können langfristige Trends erkennen.
""")

# 👤 Benutzerinfo
st.info(f"👋 Eingeloggt als: {st.session_state.username}")

# Infobox
st.markdown("""
<div style="border-left: 4px solid #4CAF50; background-color: #F0FFF0; padding: 10px; border-radius: 5px;">
Nutzen Sie die App regelmässig, um Ihre Blutzuckerwerte besser im Blick zu behalten und langfristige Muster zu erkennen.
</div>
""", unsafe_allow_html=True)

# Autoreninfo
st.write("""
### Autoren  
Diese App wurde im Rahmen des Moduls BMLD Informatik 2 an der ZHAW entwickelt von:

- Cristiana Bastos (pereicri@students.zhaw.ch)  
- Lou-Salomé Frehner (frehnlou@students.zhaw.ch)
""")
