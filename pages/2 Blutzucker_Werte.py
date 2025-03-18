import streamlit as st
from utils.login_manager import LoginManager
from utils.data_manager import DataManager

# ====== Login Block ======
login_manager = LoginManager()
login_manager.go_to_login('Start.py')
# ====== End Login Block ======

# ====== Funktionen ======

def blutzucker_werte():
    # Überschrift
    st.markdown("## 📋 Blutzucker-Werte")

    # Nutzername aus dem Session-State holen
    username = st.session_state.get("username")

    if not username:
        st.error("Kein Benutzer eingeloggt. Anmeldung erforderlich.")
        st.stop()

    # Datenbank für den Nutzer laden
    data_manager = DataManager(fs_protocol='webdav', fs_root_folder="BMLD_cblsf_App")
    user_data = data_manager.load_user_data(
        session_state_key="user_data",
        username=username,
        parse_dates=["datum_zeit"]
    )

    if not user_data.empty:
        st.markdown("### Gespeicherte Blutzuckerwerte")

        # Sicherstellen, dass die benötigten Spalten existieren
        if all(col in user_data.columns for col in ["datum_zeit", "blutzuckerwert", "zeitpunkt"]):
            st.table(user_data[["datum_zeit", "blutzuckerwert", "zeitpunkt"]])

            # Durchschnitt berechnen und anzeigen
            durchschnitt = user_data["blutzuckerwert"].mean()
            st.markdown(f"**Durchschnittlicher Blutzuckerwert:** {durchschnitt:.2f} mg/dL")
        else:
            st.warning("Datenformat fehlerhaft oder Spalten fehlen.")
    else:
        st.warning("Noch keine Daten vorhanden.")

# ====== Navigation ======
def navigation_buttons():
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("🏠 Startseite"):
            st.session_state.seite = "Startseite"

    with col2:
        if st.button("🩸 Blutzucker-Tracker"):
            st.session_state.seite = "Blutzucker-Tracker"

    with col3:
        if st.button("📋 Blutzucker-Werte"):
            st.session_state.seite = "Blutzucker-Werte"

    with col4:
        if st.button("📊 Blutzucker-Grafik"):
            st.session_state.seite = "Blutzucker-Grafik"

# ====== Hauptprogramm ======
if __name__ == "__main__":
    navigation_buttons()
    blutzucker_werte()