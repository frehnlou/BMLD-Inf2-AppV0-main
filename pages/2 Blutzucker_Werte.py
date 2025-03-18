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
        session_state_key=f"user_data_{username}",  # Konsistenter Key wie in 3 Blutzucker_Grafik.py
        username=username,  # ✅ Benutzer bekommt seine eigene Datei
        parse_dates=["datum_zeit"]
    )

    if not user_data.empty:
        st.markdown("###  Gespeicherte Blutzuckerwerte")

        # 🔥 Sicherstellen, dass die Spalten existieren
        if all(col in user_data.columns for col in ["datum_zeit", "blutzuckerwert", "zeitpunkt"]):
            # Benutzerdefinierte Spaltenüberschriften
            renamed_data = user_data.rename(columns={
                "datum_zeit": "Datum & Zeit",
                "blutzuckerwert": "1: Blutzuckerwerte",
                "zeitpunkt": "2: Nüchtern"
            })
            st.table(renamed_data[["Datum & Zeit", "1: Blutzuckerwerte", "2: Nüchtern"]])
            
            # ✅ Durchschnitt berechnen
            durchschnitt = user_data["blutzuckerwert"].mean()
            st.markdown(f"* Durchschnittlicher Blutzuckerwert:* {durchschnitt:.2f} mg/dL")
        else:
            st.warning("⚠️ Datenformat fehlerhaft oder Spalten fehlen!")
    else:
        st.warning("Noch keine Daten vorhanden.")

# Hauptfunktion ausführen
if __name__ == "__main__":
    blutzucker_werte()