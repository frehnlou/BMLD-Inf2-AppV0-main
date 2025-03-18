import streamlit as st
import pandas as pd
from utils.login_manager import LoginManager
from utils.data_manager import DataManager

# ====== Start Login Block ======
login_manager = LoginManager()
login_manager.go_to_login('Start.py') 
# ====== End Login Block ======

def blutzucker_werte():
    # Abstand nach oben für bessere Platzierung
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("## 📋 Blutzucker-Werte")

    # Nutzername holen
    username = st.session_state.get("username")

    if not username:
        st.error("⚠️ Kein Benutzer eingeloggt! Anmeldung erforderlich.")
        st.stop()

    # Datenbank für den Nutzer laden
    data_manager = DataManager(fs_protocol='webdav', fs_root_folder="BMLD_cblsf_App")
    user_data = data_manager.load_user_data(
        session_state_key="user_data",
        username=username,  
        parse_dates=["datum_zeit"]
    )

    # DEBUGGING: Überprüfen, ob Daten geladen wurden
    st.write(f"🔍 **Debug: Geladene Daten für Benutzer `{username}`**")
    st.write(user_data)

    if user_data.empty:
        st.warning("⚠️ Noch keine Blutzuckerwerte vorhanden. Bitte neuen Wert eingeben.")
    else:
        st.markdown("###  Gespeicherte Blutzuckerwerte")

        # Sicherstellen, dass Spalten existieren
        required_columns = {"datum_zeit", "blutzuckerwert", "zeitpunkt"}
        if required_columns.issubset(user_data.columns):
            # Tabelle anzeigen
            st.table(user_data[["datum_zeit", "blutzuckerwert", "zeitpunkt"]])

            # ✅ Durchschnitt berechnen
            durchschnitt = user_data["blutzuckerwert"].mean()
            st.markdown(f" **Durchschnittlicher Blutzuckerwert:** {durchschnitt:.2f} mg/dL")
        else:
            st.warning("⚠️ Datenformat fehlerhaft oder Spalten fehlen!")

if __name__ == "__main__":
    blutzucker_werte()
