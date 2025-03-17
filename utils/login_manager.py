import secrets
import streamlit as st
import streamlit_authenticator as stauth
from utils.data_manager import DataManager


class LoginManager:
    """
    Singleton-Klasse für die Verwaltung von Anwendungszustand, Speicherung und Benutzer-Authentifizierung.
    """
    def __new__(cls, *args, **kwargs):
        """ Singleton-Pattern: Gibt die bestehende Instanz zurück, falls vorhanden. """
        if 'login_manager' in st.session_state:
            return st.session_state.login_manager
        else:
            instance = super(LoginManager, cls).__new__(cls)
            st.session_state.login_manager = instance
            return instance
    
    def __init__(self, data_manager: DataManager = None,
                 auth_credentials_file: str = 'credentials.yaml',
                 auth_cookie_name: str = 'bmld_inf2_streamlit_app'):
        """ Initialisiert die Authentifizierung und das Dateisystem. """
        if hasattr(self, 'authenticator'):  # Falls schon initialisiert, abbrechen
            return
        
        if data_manager is None:
            return

        self.data_manager = data_manager
        self.auth_credentials_file = auth_credentials_file
        self.auth_cookie_name = auth_cookie_name
        self.auth_cookie_key = secrets.token_urlsafe(32)
        self.auth_credentials = self._load_auth_credentials()
        self.authenticator = stauth.Authenticate(self.auth_credentials, self.auth_cookie_name, self.auth_cookie_key)

    def _load_auth_credentials(self):
        """ Lädt Benutzeranmeldeinformationen aus der Konfigurationsdatei. """
        dh = self.data_manager._get_data_handler()
        return dh.load(self.auth_credentials_file, initial_value={"usernames": {}})

    def _save_auth_credentials(self):
        """ Speichert die aktuellen Benutzeranmeldeinformationen in die Datei. """
        dh = self.data_manager._get_data_handler()
        dh.save(self.auth_credentials_file, self.auth_credentials)

    def login_register(self, login_title="Login", register_title="Neuen Benutzer registrieren"):
        """
        Zeigt das Anmelde- und Registrierungsformular in Tabs an.

        Args:
            login_title (str): Titel für den Login-Tab.
            register_title (str): Titel für den Registrierungs-Tab.
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
        """ Zeigt das Anmeldeformular an und verarbeitet die Authentifizierung. """
        if st.session_state.get("authentication_status") is True:
            self.authenticator.logout()
        else:
            self.authenticator.login()
            if st.session_state["authentication_status"] is False:
                st.error("❌ Benutzername oder Passwort ist falsch!")
            else:
                st.warning("Bitte geben Sie Ihren Benutzernamen und Ihr Passwort ein.")
            if stop:
                st.stop()

    def register(self, stop=True):
        """
        Zeigt das Registrierungsformular an und setzt neue Benutzer in die Datenbank.
        """
        if st.session_state.get("authentication_status") is True:
            self.authenticator.logout()
        else:
            st.info("""
            🔒 **Passwortanforderungen:**  
            - **8-15 Zeichen lang**  
            - Mindestens **1 Grossbuchstabe**  
            - Mindestens **1 Kleinbuchstabe**  
            - Mindestens **1 Zahl**  
            - Mindestens **1 Sonderzeichen** (@$!%*?&)  
            """)

            # ✅ Registrierungsformular
            res = self.authenticator.register_user()

            if res and res[1] is not None:
                st.success(f"✅ Benutzer {res[1]} wurde erfolgreich registriert!")
                try:
                    self._save_auth_credentials()
                    st.success("✅ Zugangsdaten wurden gespeichert.")
                except Exception as e:
                    st.error(f"⚠️ Fehler beim Speichern der Zugangsdaten: {e}")

            if stop:
                st.stop()

    def go_to_login(self, login_page_py_file):
        """
        Erstellt einen Logout-Button, der den Benutzer abmeldet und zur Login-Seite umleitet.

        Args:
            login_page_py_file (str): Der Name der Python-Datei mit der Login-Seite.
        """
        if st.session_state.get("authentication_status") is not True:
            st.switch_page(login_page_py_file)
        else:
            self.authenticator.logout()  # Logout-Button anzeigen
