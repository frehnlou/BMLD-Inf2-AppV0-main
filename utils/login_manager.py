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
        if hasattr(self, 'authenticator'):
            return

        if data_manager is None:
            return

        self.data_manager = data_manager
        self.auth_credentials_file = auth_credentials_file
        self.auth_cookie_name = auth_cookie_name
        self.auth_cookie_key = secrets.token_urlsafe(32)
        self.auth_credentials = self._load_auth_credentials()
        self.authenticator = stauth.Authenticate(
            self.auth_credentials,
            self.auth_cookie_name,
            self.auth_cookie_key,
            cookie_expiry_days=30
        )

    def _load_auth_credentials(self):
        dh = self.data_manager._get_data_handler()
        return dh.load(self.auth_credentials_file, initial_value={"usernames": {}})

    def _save_auth_credentials(self):
        dh = self.data_manager._get_data_handler()
        dh.save(self.auth_credentials_file, self.auth_credentials)

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
        if st.session_state.get("authentication_status") is True:
            self.authenticator.logout("Logout", "sidebar")
        else:
            try:
                name, authentication_status, username = self.authenticator.login("Login", location="sidebar")
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
                # Verwende die Methode register_user(), um die Datei automatisch zu erstellen
                res = self.authenticator.register_user("Registrieren", preauthorization=False)
                if res[1] is not None:
                    st.success(f"Benutzer {res[1]} erfolgreich registriert.")
                    try:
                        # Speichere die Anmeldedaten in der Datei `credentials.yaml`
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