import secrets
import streamlit as st
import streamlit_authenticator as stauth
from utils.data_manager import DataManager

class LoginManager:
    """
    Singleton-Klasse, die das Anwendungs-Login verwaltet.
    
    - Unterstützt Benutzerregistrierung, Anmeldung und Sitzungsverwaltung.
    - Speichert Benutzerdaten in einer YAML-Datei für Authentifizierung.
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
        """
        Initialisiert den Login-Manager.

        Args:
            data_manager: Das DataManager-Objekt zur Speicherung von Benutzeranmeldungen.
            auth_credentials_file (str): YAML-Datei zur Speicherung von Benutzerdaten.
            auth_cookie_name (str): Name des Authentifizierungs-Cookies.
        """
        if hasattr(self, 'authenticator'):  # Falls bereits initialisiert, nichts tun
            return
        
        if data_manager is None:
            return

        # Initialisiere Authentifizierungsvariablen
        self.data_manager = data_manager
        self.auth_credentials_file = auth_credentials_file
        self.auth_cookie_name = auth_cookie_name
        self.auth_cookie_key = secrets.token_urlsafe(32)
        self.auth_credentials = self._load_auth_credentials()
        self.authenticator = stauth.Authenticate(self.auth_credentials, self.auth_cookie_name, self.auth_cookie_key)


    def _load_auth_credentials(self):
        """
        Lädt die Benutzerdaten aus der YAML-Datei.

        Returns:
            dict: Benutzerinformationen, falls vorhanden.
        """
        dh = self.data_manager._get_data_handler()
        return dh.load(self.auth_credentials_file, initial_value= {"usernames": {}})

    def _save_auth_credentials(self):
        """
        Speichert aktuelle Benutzeranmeldungen in die YAML-Datei.
        """
        dh = self.data_manager._get_data_handler()
        dh.save(self.auth_credentials_file, self.auth_credentials)

    def login_register(self, login_title='Login', register_title='Neuen Benutzer registrieren'):
        """
        Zeigt das Login- und Registrierungsformular an.
        
        Falls der Benutzer nicht eingeloggt ist, wird entweder das Login- oder Registrierungsformular angezeigt.
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
        Zeigt das Login-Formular an und verarbeitet den Anmeldevorgang.
        """
        if st.session_state.get("authentication_status") is True:
            self.authenticator.logout()
        else:
            self.authenticator.login()
            if st.session_state["authentication_status"] is False:
                st.error("⚠️ Benutzername oder Passwort ist falsch!")
            else:
                st.warning("Bitte Benutzername und Passwort eingeben.")
            if stop:
                st.stop()

    def register(self, stop=True):
        """
        Zeigt das Registrierungsformular an und speichert neue Benutzer.
        """
        if st.session_state.get("authentication_status") is True:
            self.authenticator.logout()
        else:
            st.info("""
            🔑Das Passwort muss zwischen 8-15 Zeichen lang sein und mindestens enthalten:
            - Einen Großbuchstaben
            - Einen Kleinbuchstaben
            - Eine Zahl
            - Ein Sonderzeichen (@$!%*?&)
            """)

            res = self.authenticator.register_user()
            if res[1] is not None:
                st.success(f"✅ Benutzer *{res[1]}* wurde erfolgreich registriert!")
                try:
                    self._save_auth_credentials()
                    st.success("🔒 Anmeldedaten wurden gespeichert!")
                except Exception as e:
                    st.error(f"⚠️ Fehler beim Speichern der Anmeldedaten: {e}")
            if stop:
                st.stop()

    def go_to_login(self, login_page_py_file):
        """
        Erstellt eine Logout-Schaltfläche und leitet nicht angemeldete Benutzer zur Login-Seite um.
        """
        if st.session_state.get("authentication_status") is not True:
            st.switch_page(login_page_py_file)
        else:
            self.authenticator.logout()  # 🔑 Zeigt Logout-Button an
