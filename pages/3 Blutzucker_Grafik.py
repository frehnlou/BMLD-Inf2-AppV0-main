import streamlit as st
import pandas as pd
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

def blutzucker_grafik():
    st.markdown("## 📊 Blutzucker-Grafik")

    # Daten laden
    user_data = lade_daten()

    if not user_data.empty:
        st.markdown("### Verlauf der Blutzuckerwerte")
        blutzuckerwerte = user_data[["datum_zeit", "blutzuckerwert"]].set_index("datum_zeit")
        st.line_chart(blutzuckerwerte)
    else:
        st.warning("⚠️ Noch keine Daten vorhanden.")