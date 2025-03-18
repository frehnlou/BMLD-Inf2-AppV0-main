import streamlit as st
import json
from utils.data_manager import DataManager

class LoginManager:
    def __init__(self, data_manager):
        self.data_manager = data_manager
        if not self.data_manager:
            raise ValueError("❌ data_manager wurde nicht korrekt übergeben!")

        self.auth_credentials = self._load_auth_credentials()

    def _load_auth_credentials(self):
        """ Lädt die Authentifizierungsdaten. """
        dh = self.data_manager._get_data_handler()
        try:
            return dh.load("auth_credentials.json", initial_value={})
        except Exception:
            st.error("⚠️ Fehler beim Laden der Authentifizierungsdaten!")
            return {}

    def login_register(self):
        """ Zeigt Login- oder Registrierungsformular an. """
        st.markdown("## 🔐 Login / Registrierung")
        username = st.text_input("Benutzername")
        password = st.text_input("Passwort", type="password")

        if st.button("Login"):
            if username in self.auth_credentials and self.auth_credentials[username] == password:
                st.session_state["authentication_status"] = True
                st.session_state["username"] = username
                st.success(f"✅ Erfolgreich eingeloggt als {username}")
                st.experimental_rerun()
            else:
                st.error("❌ Falsche Login-Daten!")

    def logout(self):
        """ Loggt den Benutzer aus. """
        st.session_state.clear()
        st.success("🚪 Erfolgreich ausgeloggt!")
        st.experimental_rerun()
