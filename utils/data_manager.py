import secrets
import yaml
import streamlit as st
import streamlit_authenticator as stauth
from utils.data_manager import DataManager

class LoginManager:
    def __init__(self, data_manager: DataManager = None, auth_credentials_file: str = "credentials.yaml"):
        if data_manager is None:
            raise ValueError("❌ DataManager darf nicht None sein!")

        self.data_manager = data_manager
        self.auth_credentials_file = auth_credentials_file
        self.auth_cookie_name = "bmld_inf2_streamlit_app"
        self.auth_cookie_key = secrets.token_urlsafe(32)

        self.auth_credentials = self._load_auth_credentials()

        # Falls die Datei leer oder fehlerhaft ist, abbrechen!
        if not self.auth_credentials or "usernames" not in self.auth_credentials:
            st.error("⚠️ Fehler beim Laden der Benutzerdaten. Bitte sicherstellen, dass `credentials.yaml` existiert!")
            st.stop()

        self.authenticator = stauth.Authenticate(
            self.auth_credentials,
            self.auth_cookie_name,
            self.auth_cookie_key,
            cookie_expiry_days=30
        )

    def _load_auth_credentials(self):
        """Lädt die Anmeldeinformationen aus `credentials.yaml`"""
        try:
            with open(self.auth_credentials_file, "r") as file:
                credentials = yaml.safe_load(file)
            return credentials
        except Exception as e:
            st.error(f"⚠️ Fehler beim Laden der Anmeldeinformationen: {e}")
            return {"usernames": {}}

    def _save_auth_credentials(self):
        """Speichert die aktualisierten Benutzeranmeldedaten in `credentials.yaml`"""
        try:
            with open(self.auth_credentials_file, "w") as file:
                yaml.dump(self.auth_credentials, file)
        except Exception as e:
            st.error(f"❌ Fehler beim Speichern der Benutzeranmeldedaten: {e}")

    def login_register(self):
        """Stellt Login und Registrierung bereit"""
        if "authentication_status" not in st.session_state:
            st.session_state["authentication_status"] = None

        login_tab, register_tab = st.tabs([" Login", " Registrierung"])
        with login_tab:
            self.login()
        with register_tab:
            self.register()

    def login(self):
        """Benutzer-Login mit `streamlit_authenticator`"""
        try:
            name, authentication_status, username = self.authenticator.login("Login", "main")
            st.session_state["authentication_status"] = authentication_status

            if authentication_status:
                st.session_state["username"] = username
                st.success(f"✅ Erfolgreich eingeloggt als {username}")
            elif authentication_status is False:
                st.error("❌ Falsche Login-Daten!")
            else:
                st.warning(" Bitte Benutzername und Passwort eingeben.")
        except Exception as e:
            st.error(f"⚠️ Fehler beim Login: {e}")

    def register(self):
        """Benutzerregistrierung"""
        st.info("📌 Passwort muss mind. 8 Zeichen, eine Zahl, ein Sonderzeichen enthalten.")
        try:
            res = self.authenticator.register_user()
            if res[1]:
                st.success(f"✅ Benutzer `{res[1]}` erfolgreich registriert!")
                self._save_auth_credentials()
        except Exception as e:
            st.error(f"❌ Fehler bei der Registrierung: {e}")

    def go_to_login(self, login_page_py_file):
        """Leitet zur Login-Seite um, wenn der Benutzer nicht angemeldet ist"""
        if st.session_state.get("authentication_status") is not True:
            st.switch_page(login_page_py_file)
        else:
            self.authenticator.logout()
            st.success("✅ Erfolgreich ausgeloggt!")