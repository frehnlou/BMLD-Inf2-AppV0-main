import streamlit as st
from utils.login_manager import LoginManager  # 🔐 Login-Manager hinzufügen
from utils.data_manager import DataManager  # 📊 Data Manager für nutzerspezifische Daten

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
        username=username,  # ✅ Benutzer bekommt seine eigene Datei
        parse_dates=["datum_zeit"]
    )

    if user_data is not None and not user_data.empty:
        st.markdown("### 📋 Gespeicherte Blutzuckerwerte")

        # 🔥 Sicherstellen, dass die Spalten existieren
        required_columns = {"datum_zeit", "blutzuckerwert", "zeitpunkt"}
        if required_columns.issubset(user_data.columns):
            # 🔥 Falls `datum_zeit` nicht als `Datetime` erkannt wird, umwandeln
            if not pd.api.types.is_datetime64_any_dtype(user_data["datum_zeit"]):
                user_data["datum_zeit"] = pd.to_datetime(user_data["datum_zeit"], errors='coerce')

            st.table(user_data[["datum_zeit", "blutzuckerwert", "zeitpunkt"]])

            # ✅ Durchschnitt berechnen
            durchschnitt = user_data["blutzuckerwert"].mean()
            st.markdown(f"**📊 Durchschnittlicher Blutzuckerwert:** {durchschnitt:.2f} mg/dL")
        else:
            st.warning("⚠️ Datenformat fehlerhaft oder Spalten fehlen!")
    else:
        st.warning("⚠️ Noch keine Blutzuckerwerte vorhanden. Bitte geben Sie einen neuen Wert ein.")

if __name__ == "__main__":
    blutzucker_werte()
