import secrets
import streamlit as st
import streamlit_authenticator as stauth
from utils.data_manager import DataManager


class LoginManager:
    """
    Singleton-Klasse, die den Anwendungszustand, die Speicherung und die Benutzer-Authentifizierung verwaltet.
    
    Verwaltet den Zugriff auf das Dateisystem, Benutzeranmeldedaten und den Authentifizierungsstatus mithilfe von
    Streamlits Session-State für Persistenz zwischen Ausführungen. Bietet Schnittstellen für benutzerspezifische
    und anwendungsweite Datenspeicherung.
    """
    def __new__(cls, *args, **kwargs):
        """
        Implementiert das Singleton-Muster, indem die vorhandene Instanz aus dem Session-State zurückgegeben wird, falls verfügbar.

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
        Initialisiert die Komponenten für Dateisystem und Authentifizierung, falls noch nicht initialisiert.

        Konfiguriert den Zugriff auf das Dateisystem mit dem angegebenen Protokoll und richtet die Authentifizierung
        mit Cookie-basierter Sitzungsverwaltung ein.

        Args:
            data_manager: Die DataManager-Instanz für die Datenspeicherung.
            auth_credentials_file (str): Der Dateiname für die Speicherung der Benutzeranmeldedaten.
            auth_cookie_name (str): Der Name des Cookies für die Sitzungsverwaltung.
        """
        if hasattr(self, 'authenticator'):  # Überprüfen, ob die Instanz bereits initialisiert ist
            return
        
        if data_manager is None:
            return

        # Initialisiere Streamlit-Authentifizierungs-Komponenten
        self.data_manager = data_manager
        self.auth_credentials_file = auth_credentials_file
        self.auth_cookie_name = auth_cookie_name
        self.auth_cookie_key = secrets.token_urlsafe(32)
        self.auth_credentials = self._load_auth_credentials()
        self.authenticator = stauth.Authenticate(self.auth_credentials, self.auth_cookie_name, self.auth_cookie_key)

    def _load_auth_credentials(self):
        """
        Lädt Benutzeranmeldedaten aus der konfigurierten Anmeldedatei.

        Returns:
            dict: Benutzeranmeldedaten, standardmäßig ein leeres `usernames`-Dict, falls die Datei nicht gefunden wird.
        """
        dh = self.data_manager._get_data_handler()
        return dh.load(self.auth_credentials_file, initial_value={"usernames": {}})

    def _save_auth_credentials(self):
        """
        Speichert die aktuellen Benutzeranmeldedaten in der Anmeldedatei.
        """
        dh = self.data_manager._get_data_handler()
        dh.save(self.auth_credentials_file, self.auth_credentials)

    def login_register(self, login_title='Login', register_title='Register new user'):
        """
        Rendert die Authentifizierungsoberfläche.
        
        Zeigt das Login-Formular und optional das Registrierungsformular an. Verarbeitet die
        Authentifizierungs- und Registrierungsabläufe. Stoppt die weitere Ausführung nach dem Rendern.
        
        Args:
            login_title (str): Titel des Login-Tabs.
            register_title (str): Titel des Registrierungs-Tabs.
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
        Rendert das Login-Formular und verarbeitet Authentifizierungsstatus-Meldungen.
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
        Rendert das Registrierungsformular und verarbeitet den Registrierungsablauf.
        
        Zeigt Passwortanforderungen an, verarbeitet Registrierungsversuche und speichert
        Anmeldedaten bei erfolgreicher Registrierung.
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
            self.authenticator.logout()  # Erstellt die Logout-Schaltfläche