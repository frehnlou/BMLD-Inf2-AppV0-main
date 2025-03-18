import secrets
import streamlit as st
import streamlit_authenticator as stauth
from utils.data_manager import DataManager


class LoginManager:
    """
    Singleton-Klasse, die den Anwendungszustand, die Speicherung und die Benutzer-Authentifizierung verwaltet.
    
    Verwaltet den Zugriff auf das Dateisystem, Benutzeranmeldedaten und den Authentifizierungsstatus
    mithilfe des Streamlit-Session-States für Konsistenz zwischen Reruns.
    """
    def __new__(cls, *args, **kwargs):
        """
        Implementiert das Singleton-Pattern, indem die bestehende Instanz aus dem Session-State zurückgegeben wird, falls verfügbar.

        Returns:
            LoginManager: Die Singleton-Instanz, entweder bestehend oder neu erstellt.
        """
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
        Initialisiert die Komponenten für das Dateisystem und die Authentifizierung, falls noch nicht initialisiert.

        Args:
            data_manager: Die DataManager-Instanz für die Datenspeicherung.
            auth_credentials_file (str): Der Dateiname für die Speicherung der Benutzeranmeldedaten.
            auth_cookie_name (str): Der Name des Cookies für die Sitzungsverwaltung.
        """
        if hasattr(self, 'authenticator'):  # Überprüfen, ob die Instanz bereits initialisiert ist
            return
        
        if data_manager is None:
            return

        # Initialisiere die Authentifizierungskomponenten
        self.data_manager = data_manager
        self.auth_credentials_file = auth_credentials_file
        self.auth_cookie_name = auth_cookie_name
        self.auth_cookie_key = secrets.token_urlsafe(32)
        self.auth_credentials = self._load_auth_credentials()
        self.authenticator = stauth.Authenticate(
            self.auth_credentials,
            self.auth_cookie_name,
            self.auth_cookie_key
        )

    def _load_auth_credentials(self):
        """
        Lädt die Benutzeranmeldedaten aus der konfigurierten Anmeldedatei.

        Returns:
            dict: Benutzeranmeldedaten, standardmäßig ein leeres `usernames`-Dictionary, falls die Datei nicht gefunden wird.
        """
        dh = self.data_manager._get_data_handler()
        return dh.load(self.auth_credentials_file, initial_value={"usernames": {}})

    def _save_auth_credentials(self):
        """
        Speichert die aktuellen Benutzeranmeldedaten in der Anmeldedatei.
        """
        dh = self.data_manager._get_data_handler()
        dh.save(self.auth_credentials_file, self.auth_credentials)

    def login_register(self, login_title='Login', register_title='Registrieren'):
        """
        Rendert die Authentifizierungsoberfläche.
        
        Zeigt das Login-Formular und optional das Registrierungsformular an. Verarbeitet die Benutzeranmeldung
        und den Registrierungsablauf. Stoppt die weitere Ausführung nach dem Rendern.
        """
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

        Args:
            stop (bool): Stoppt die Ausführung nach dem Rendern.
        """
        if st.session_state.get("authentication_status") is True:
            self.authenticator.logout("Logout", "sidebar")
        else:
            self.authenticator.login("Login", "sidebar")
            if st.session_state["authentication_status"] is False:
                st.error("Benutzername/Passwort ist falsch.")
            else:
                st.warning("Bitte geben Sie Ihren Benutzernamen und Ihr Passwort ein.")
            if stop:
                st.stop()

    def register(self, stop=True):
        """
        Rendert das Registrierungsformular und verarbeitet den Benutzerregistrierungsablauf.
        Zeigt Passwortanforderungen an, verarbeitet Registrierungsversuche und speichert Anmeldedaten
        bei erfolgreicher Registrierung.

        Args:
            stop (bool): Stoppt die Ausführung nach dem Rendern.
        """
        if st.session_state.get("authentication_status") is True:
            self.authenticator.logout("Logout", "sidebar")
        else:
            st.info("""
            Das Passwort muss 8-20 Zeichen lang sein und mindestens einen Grossbuchstaben, 
            einen Kleinbuchstaben, eine Ziffer und ein Sonderzeichen aus @$!%*?& enthalten.
            """)
            res = self.authenticator.register_user("Registrieren", preauthorization=False)
            if res[1] is not None:
                st.success(f"Benutzer {res[1]} erfolgreich registriert.")
                try:
                    self._save_auth_credentials()
                    st.success("Anmeldedaten erfolgreich gespeichert.")
                except Exception as e:
                    st.error(f"Fehler beim Speichern der Anmeldedaten: {e}")
            if stop:
                st.stop()

    def go_to_login(self, login_page_py_file):
        """
        Erstellt eine Logout-Schaltfläche, die den Benutzer abmeldet und zur Login-Seite weiterleitet.
        Wenn der Benutzer nicht eingeloggt ist, wird die Login-Seite angezeigt.

        Args:
            login_page_py_file (str): Der Pfad zur Python-Datei, die die Login-Seite enthält.
        """
        if st.session_state.get("authentication_status") is not True:
            st.switch_page(login_page_py_file)
        else:
            self.authenticator.logout("Logout", "sidebar")