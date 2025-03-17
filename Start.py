import streamlit as st
import pandas as pd
from utils.data_manager import DataManager
from utils.login_manager import LoginManager  # 🔐 Login-Manager hinzufügen

# ✅ MUSS als erstes Streamlit-Kommando stehen
st.set_page_config(page_title="Blutzucker Tracker", layout="wide")

# ====== Start Login Block ======
st.write("🚀 **App wird gestartet...**")

# ✅ Prüfe, ob `DataManager` richtig initialisiert wird
try:
    data_manager = DataManager(fs_protocol='webdav', fs_root_folder="BMLD_cblsf_App")
    st.write("✅ **DataManager erfolgreich initialisiert!**")
except Exception as e:
    st.error(f"❌ Fehler beim Initialisieren von DataManager: {e}")
    data_manager = None  # Falls Fehler, setze auf None

# Falls `DataManager` nicht existiert, stoppe die App
if data_manager is None:
    st.error("❌ **Fehler: DataManager konnte nicht erstellt werden.**")
    st.stop()

# ✅ Prüfe `LoginManager`
try:
    login_manager = LoginManager(data_manager)
    st.write("✅ **LoginManager erfolgreich erstellt!**")
except Exception as e:
    st.error(f"❌ Fehler bei der Erstellung von LoginManager: {e}")
    st.stop()  # Falls LoginManager nicht funktioniert, App stoppen

# ✅ Prüfe `login_register()`
try:
    login_manager.login_register()  # Login-/Registrierungsseite anzeigen
    st.write("✅ **login_register() erfolgreich ausgeführt!**")
except Exception as e:
    st.error(f"❌ Fehler in login_register(): {e}")
    st.stop()  # Falls login_register() fehlschlägt, App stoppen

# ✅ Prüfe, ob `username` im `session_state` existiert
if "username" not in st.session_state:
    st.session_state["username"] = None

# ✅ Prüfe, ob ein Benutzer eingeloggt ist, bevor Daten geladen werden
if st.session_state["username"]:
    try:
        data_manager.load_user_data(
            session_state_key='data_df',
            file_name='data.csv',
            initial_value=pd.DataFrame(columns=["username", "datum_zeit", "blutzuckerwert", "zeitpunkt"]),
            parse_dates=['datum_zeit']
        )
        st.write("✅ **Benutzerdaten erfolgreich geladen!**")
    except Exception as e:
        st.error(f"❌ Fehler beim Laden der Benutzerdaten: {e}")
else:
    st.warning("⚠️ Kein Benutzer eingeloggt! Daten können nicht geladen werden.")

# ====== Ende Login & Daten Block ======

# Titel und Begrüßung
st.markdown("## 🩸 Blutzucker-Tracker für Diabetiker")

# Beschreibung
st.write("""
Willkommen zum Blutzucker-Tracker! Diese App unterstützt Sie dabei, Ihre Blutzuckerwerte einfach zu erfassen, zu speichern und zu analysieren. So behalten Sie Ihre Werte stets im Blick und können langfristige Trends erkennen.
""")

# 👤 Benutzerinfo
if st.session_state["username"]:
    st.info(f"👋 Eingeloggt als: *{st.session_state.username}*")
else:
    st.warning("⚠️ Kein Benutzer eingeloggt!")

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

- *Cristiana Bastos* (pereicri@students.zhaw.ch)  
- *Lou-Salomé Frehner* (frehnlou@students.zhaw.ch)
""")
