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
        Initialisiert die LoginManager-Klasse.
        """
        if data_manager is None:
            raise ValueError("Ein gültiger DataManager muss übergeben werden.")

        self.data_manager = data_manager
        self.auth_credentials_file = auth_credentials_file
        self.auth_cookie_name = auth_cookie_name
        self.auth_cookie_key = secrets.token_urlsafe(32)
        self.auth_credentials = self._load_auth_credentials()

        # Initialisiere den Authenticator
        self.authenticator = stauth.Authenticate(
            self.auth_credentials,
            self.auth_cookie_name,
            self.auth_cookie_key,
            cookie_expiry_days=30
        )

    def _load_auth_credentials(self):
        """
        Lädt die Benutzeranmeldedaten aus der Datei `credentials.yaml`.
        Erstellt eine neue Datei mit Standardwerten, falls sie nicht existiert.

        Returns:
            dict: Benutzeranmeldedaten.
        """
        dh = self.data_manager._get_data_handler()
        try:
            creds = dh.load(self.auth_credentials_file, initial_value={"usernames": {}})
            if not creds or "usernames" not in creds:
                raise ValueError("credentials.yaml wurde nicht gefunden oder ist leer. Eine neue Datei wird erstellt...")
            return creds
        except Exception as e:
            st.warning(f"{e}")
            creds = {"usernames": {}}
            dh.save(self.auth_credentials_file, creds)
            return creds

    def _save_auth_credentials(self):
        """
        Speichert die Benutzeranmeldedaten in der Datei `credentials.yaml`.
        """
        dh = self.data_manager._get_data_handler()
        try:
            dh.save(self.auth_credentials_file, self.auth_credentials)
        except Exception as e:
            st.error(f"Fehler beim Speichern der Anmeldedaten: {e}")

    def login_register(self, login_title='Login', register_title='Register new user'):
        if st.session_state.get("authentication_status") is True:
            self.authenticator.logout("Logout", "sidebar")
        else:
            login_tab, register_tab = st.tabs((login_title, register_title))
            with login_tab:
                self.login(stop=False)
            with register_tab:
                self.register()

    def login(self, stop=True):
        """
        Rendert das Login-Formular und verarbeitet Authentifizierungsstatusmeldungen.
        """
        if st.session_state.get("authentication_status") is True:
            self.authenticator.logout("Logout", "sidebar")
        else:
            try:
                name, authentication_status, username = self.authenticator.login("Login", "sidebar")
                if authentication_status:
                    st.success(f"Willkommen {name}!")
                elif authentication_status is False:
                    st.error("Benutzername/Passwort ist falsch.")
                elif authentication_status is None:
                    st.warning("Bitte geben Sie Ihren Benutzernamen und Ihr Passwort ein.")
            except Exception as e:
                st.error(f"Fehler bei der Anmeldung: {e}")
            if stop:
                st.stop()

    def register(self, stop=True):
        """
        Rendert das Registrierungsformular und verarbeitet den Benutzerregistrierungsablauf.
        Erstellt die Datei `credentials.yaml`, falls sie nicht existiert.
        """
        if st.session_state.get("authentication_status") is True:
            self.authenticator.logout("Logout", "sidebar")
        else:
            st.info("""
            Das Passwort muss 8-20 Zeichen lang sein und mindestens einen Großbuchstaben, 
            einen Kleinbuchstaben, eine Ziffer und ein Sonderzeichen aus @$!%*?& enthalten.
            """)
            try:
                res = self.authenticator.register_user("Registrieren", preauthorization=False)
                if res[1] is not None:
                    st.success(f"Benutzer {res[1]} erfolgreich registriert.")
                    try:
                        self._save_auth_credentials()
                        st.success("Anmeldedaten erfolgreich gespeichert.")
                    except Exception as e:
                        st.error(f"Fehler beim Speichern der Anmeldedaten: {e}")
            except Exception as e:
                st.error(f"Fehler bei der Registrierung: {e}")
            if stop:
                st.stop()

    def go_to_login(self, login_page_py_file):
        if st.session_state.get("authentication_status") is not True:
            st.switch_page(login_page_py_file)
        else:
            self.authenticator.logout("Logout", "sidebar")