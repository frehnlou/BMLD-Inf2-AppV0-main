import secrets
import streamlit as st
import streamlit_authenticator as stauth
from utils.data_manager import DataManager


class LoginManager:
    """
    Singleton-Klasse, die den Anwendungszustand, die Speicherung und die Benutzer-Authentifizierung verwaltet.
    """
    def __new__(cls, *args, **kwargs):
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
        Initialisiert die Komponenten für das Dateisystem und die Authentifizierung.
        """
        if hasattr(self, 'authenticator'):
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
        """
        Lädt die Benutzeranmeldedaten aus der konfigurierten Datei.
        """
        dh = self.data_manager._get_data_handler()
        st.write(f"Lade Anmeldedaten aus: {self.auth_credentials_file}")  # Debugging-Ausgabe
        return dh.load(self.auth_credentials_file, initial_value={"usernames": {}})

    def _save_auth_credentials(self):
        """
        Speichert die aktuellen Benutzeranmeldedaten in der Datei.
        """
        dh = self.data_manager._get_data_handler()
        try:
            st.write(f"Speichere Anmeldedaten in: {self.auth_credentials_file}")  # Debugging-Ausgabe
            dh.save(self.auth_credentials_file, self.auth_credentials)
        except Exception as e:
            st.error(f"Fehler beim Speichern der Datei: {e}")

    def login_register(self, login_title='Login', register_title='Register new user'):
        """
        Zeigt die Authentifizierungsoberfläche an.
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
        Zeigt das Anmeldeformular an und verarbeitet den Authentifizierungsstatus.
        """
        if st.session_state.get("authentication_status") is True:
            self.authenticator.logout()
        else:
            self.authenticator.login()
            if st.session_state["authentication_status"] is False:
                st.error("Benutzername oder Passwort ist falsch.")
            else:
                st.warning("Bitte geben Sie Ihren Benutzernamen und Ihr Passwort ein.")
            if stop:
                st.stop()

    def register(self, stop=True):
        """
        Zeigt das Registrierungsformular an und verarbeitet den Registrierungsablauf.
        """
        if st.session_state.get("authentication_status") is True:
            self.authenticator.logout()
        else:
            st.info("""
            Das Passwort muss 8-20 Zeichen lang sein und mindestens einen Großbuchstaben, 
            einen Kleinbuchstaben, eine Ziffer und ein Sonderzeichen aus @$!%*?& enthalten.
            """)
            res = self.authenticator.register_user()
            if res[1] is not None:
                st.success(f"Benutzer {res[1]} erfolgreich registriert.")
                try:
                    # Debugging: Überprüfe, ob die Methode aufgerufen wird
                    st.write("Speichere Anmeldedaten...")
                    self._save_auth_credentials()
                    st.success("Anmeldedaten erfolgreich gespeichert.")
                except Exception as e:
                    st.error(f"Fehler beim Speichern der Anmeldedaten: {e}")
            if stop:
                st.stop()

    def go_to_login(self, login_page_py_file):
        """
        Leitet den Benutzer zur Anmeldeseite weiter, wenn er nicht eingeloggt ist.
        """
        if st.session_state.get("authentication_status") is not True:
            st.switch_page(login_page_py_file)
        else:
            self.authenticator.logout()