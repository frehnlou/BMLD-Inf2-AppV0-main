import secrets
import streamlit as st
import streamlit_authenticator as stauth
from utils.data_manager import DataManager

class LoginManager:
    """
    Verwaltet den Login- und Registrierungsprozess mit Multi-User-Unterstützung.
    Jeder Benutzer erhält eigene, separate Daten.
    """
    def __init__(self, data_manager: DataManager = None,
                 auth_credentials_file: str = 'credentials.yaml',
                 auth_cookie_name: str = 'bmld_inf2_streamlit_app'):
        """
        Initialisiert das Login-System mit Benutzerverwaltung.

        Args:
            data_manager (DataManager): Instanz von DataManager zur Speicherung von Benutzerdaten.
            auth_credentials_file (str): Datei für die Benutzerdatenbank.
            auth_cookie_name (str): Name des Authentifizierungs-Cookies.
        """
        if hasattr(self, 'authenticator'):
            return  # Falls bereits initialisiert, abbrechen

        if data_manager is None:
            raise ValueError("DataManager-Instanz erforderlich für LoginManager!")

        # Speichere Datenmanager und Login-Parameter
        self.data_manager = data_manager
        self.auth_credentials_file = auth_credentials_file
        self.auth_cookie_name = auth_cookie_name
        self.auth_cookie_key = secrets.token_urlsafe(32)

        # Lade Benutzeranmeldedaten
        self.auth_credentials = self._load_auth_credentials()

        # Authentifizierung mit Streamlit-Authenticator
        self.authenticator = stauth.Authenticate(
            credentials=self.auth_credentials,
            cookie_name=self.auth_cookie_name,
            key=self.auth_cookie_key,
            cookie_expiry_days=30
        )

    def _load_auth_credentials(self):
        """
        Lädt Benutzeranmeldedaten aus der Datenbank.

        Returns:
            dict: Anmeldedaten der Benutzer.
        """
        dh = self.data_manager._get_data_handler()
        return dh.load(self.auth_credentials_file, initial_value={"usernames": {}})

    def _save_auth_credentials(self):
        """
        Speichert aktualisierte Benutzeranmeldedaten.
        """
        dh = self.data_manager._get_data_handler()
        dh.save(self.auth_credentials_file, self.auth_credentials)

    def login_register(self):
        """
        Zeigt die Login- und Registrierungsseite an.
        Falls der Benutzer bereits eingeloggt ist, wird ein Logout-Button angezeigt.
        """
        if st.session_state.get("authentication_status") is True:
            self.authenticator.logout("Logout", "sidebar")
            st.sidebar.success(f"👤 Eingeloggt als **{st.session_state.username}**")
        else:
            login_tab, register_tab = st.tabs(["🔐 Login", "📝 Registrieren"])
            with login_tab:
                self.login()
            with register_tab:
                self.register()

    def login(self):
        """
        Zeigt das Login-Formular an und verwaltet die Anmeldung.
        """
        name, authentication_status, username = self.authenticator.login("Login", "main")

        if authentication_status is False:
            st.error("❌ Falsche Login-Daten!")
        elif authentication_status is None:
            st.warning("Bitte Benutzername und Passwort eingeben.")

    def register(self):
        """
        Zeigt das Registrierungsformular und verwaltet die Benutzerregistrierung.
        """
        st.info("""
        Das Passwort muss mindestens 8 Zeichen lang sein und
        eine Kombination aus Großbuchstaben, Kleinbuchstaben, Zahlen und Sonderzeichen enthalten.
        """)

        try:
            new_user_registered = self.authenticator.register_user(
                pre_authorization=False
            )

            if new_user_registered[1]:
                st.success(f"✅ Benutzer {new_user_registered[1]} erfolgreich registriert!")

                # Speichere die neuen Anmeldedaten
                self._save_auth_credentials()
                st.success("Anmeldedaten gespeichert!")
        except Exception as e:
            st.error(f"⚠️ Fehler bei der Registrierung: {e}")

    def go_to_login(self, login_page_py_file="Start.py"):
        """
        Falls der Benutzer nicht eingeloggt ist, zur Login-Seite umleiten.
        Falls eingeloggt, Logout-Button anzeigen.

        Args:
            login_page_py_file (str): Name der Login-Seite.
        """
        if st.session_state.get("authentication_status") is not True:
            st.switch_page(login_page_py_file)
        else:
            self.authenticator.logout("Logout", "sidebar")
            st.sidebar.success(f"👤 Eingeloggt als **{st.session_state.username}**")
