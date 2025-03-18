import secrets
import streamlit as st
import streamlit_authenticator as stauth
from utils.data_manager import DataManager


class LoginManager:
    """
    Verwaltet die Benutzeranmeldung und -registrierung mit Cookie-gestützter Authentifizierung.
    """

    def __new__(cls, *args, **kwargs):
        """ Singleton-Pattern: Verhindert mehrfaches Initialisieren. """
        if 'login_manager' in st.session_state:
            return st.session_state.login_manager
        else:
            instance = super(LoginManager, cls).__new__(cls)
            st.session_state.login_manager = instance
            return instance

    def __init__(self, data_manager: DataManager = None,
                 auth_credentials_file: str = 'credentials.yaml',
                 auth_cookie_name: str = 'bmld_inf2_streamlit_app'):
        """
        Initialisiert Authentifizierung mit Cookie-gestütztem Login.
        """

        if hasattr(self, 'authenticator'):
            return  # Bereits initialisiert

        if data_manager is None:
            return

        self.data_manager = data_manager
        self.auth_credentials_file = auth_credentials_file
        self.auth_cookie_name = auth_cookie_name
        self.auth_cookie_key = secrets.token_urlsafe(32)
        self.auth_credentials = self._load_auth_credentials()

        # ✅ Streamlit-Authenticator initialisieren
        self.authenticator = stauth.Authenticate(
            credentials=self.auth_credentials,
            cookie_name=self.auth_cookie_name,
            key=self.auth_cookie_key
        )

    def _load_auth_credentials(self):
        """
        Lädt die gespeicherten Anmeldeinformationen.
        """
        dh = self.data_manager._get_data_handler()
        return dh.load(self.auth_credentials_file, initial_value={"usernames": {}})

    def _save_auth_credentials(self):
        """
        Speichert die Anmeldeinformationen dauerhaft.
        """
        dh = self.data_manager._get_data_handler()
        dh.save(self.auth_credentials_file, self.auth_credentials)

    def login_register(self, login_title='Login', register_title='Registrieren'):
        """
        Stellt die Benutzeranmeldung und -registrierung bereit.
        """
        if st.session_state.get("authentication_status") is True:
            self.authenticator.logout()
        else:
            login_tab, register_tab = st.tabs((login_title, register_title))
            with login_tab:
                self.login(stop=False)
            with register_tab:
                self.register()

    def login(self, stop=True):
        """
        Führt die Anmeldung durch.
        """
        if st.session_state.get("authentication_status") is True:
            self.authenticator.logout()
        else:
            self.authenticator.login()
            if st.session_state["authentication_status"] is False:
                st.error("⚠️ Benutzername oder Passwort falsch!")
            if stop:
                st.stop()

    def register(self, stop=True):
        """
        Stellt die Benutzerregistrierung bereit.
        """
        if st.session_state.get("authentication_status") is True:
            self.authenticator.logout()
        else:
            st.info("Das Passwort muss 8-20 Zeichen lang sein und mindestens eine Zahl enthalten.")
            res = self.authenticator.register_user()
            if res[1] is not None:
                st.success(f"✅ Benutzer {res[1]} erfolgreich registriert!")
                try:
                    self._save_auth_credentials()
                    st.success("✅ Zugangsdaten gespeichert!")
                except Exception as e:
                    st.error(f"❌ Fehler beim Speichern: {e}")
            if stop:
                st.stop()
