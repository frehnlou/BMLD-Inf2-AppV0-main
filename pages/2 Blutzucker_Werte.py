import streamlit as st
from utils.data_manager import DataManager

# 📌 Nutzername holen
username = st.session_state.get("username", "Gast")

# 📌 Daten laden
def lade_daten():
    """ Lädt die Blutzucker-Daten von WebDAV """
    data_manager = DataManager(fs_protocol='webdav', fs_root_folder="BMLD_cblsf_App")
    return data_manager.load_user_data(
        session_state_key="user_data",
        username=username,
        initial_value=pd.DataFrame(columns=["datum_zeit", "blutzuckerwert", "zeitpunkt"]),
        parse_dates=["datum_zeit"]
    )

def blutzucker_werte():
    st.markdown("## 📋 Blutzucker-Werte")

    # Daten laden
    user_data = lade_daten()

    if not user_data.empty:
        st.markdown("### Gespeicherte Blutzuckerwerte")
        st.table(user_data.drop(columns=["username"], errors="ignore").reset_index(drop=True))
    else:
        st.warning("⚠️ Noch keine Werte gespeichert.")