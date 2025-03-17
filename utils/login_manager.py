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
            raise ValueError("❌ DataManager darf nicht None sein! Stelle sicher, dass er richtig initialisiert wurde.")
        
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
        dh = self.data_manager._get_data_handler()  # 🔥 Fix: Richtige Methode aufrufen
        dh.save(self.auth_credentials_file, self.auth_credentials)
