import secrets
import streamlit as st
import streamlit_authenticator as stauth
from utils.data_manager import DataManager


class LoginManager:
    """
    Singleton-Klasse, die den Anwendungszustand, die Speicherung und die Benutzer-Authentifizierung verwaltet.
    
    Verwaltet den Zugriff auf das Dateisystem, Benutzeranmeldedaten und den Authentifizierungsstatus
    mithilfe des Streamlit-Session-States für die Persistenz zwischen App-Neustarts.
    Bietet Schnittstellen für den Zugriff auf benutzerspezifische und anwendungsweite Datenspeicherung.
    """
    def __new__(cls, *args, **kwargs):
        """
        Implementiert das Singleton-Muster, indem die vorhandene Instanz aus dem Session-State zurückgegeben wird.

        Rückgabe:
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

        Konfiguriert den Zugriff auf das Dateisystem mit dem angegebenen Protokoll und richtet die Authentifizierung
        mit Cookie-basierter Sitzungsverwaltung ein.

        Argumente:
            data_manager: Die DataManager-Instanz für die Datenspeicherung.
            auth_credentials_file (str): Der Dateiname für die Speicherung der Benutzeranmeldedaten.
            auth_cookie_name (str): Der Name des Cookies für die Sitzungsverwaltung.
        """
        if hasattr(self, 'authenticator'):  # Überprüfen, ob die Instanz bereits initialisiert ist
            return
        
        if data_manager is None:
            return

        # Initialisiere die Authentifizierung
        self.data_manager = data_manager
        self.auth_credentials_file = auth_credentials_file
        self.auth_cookie_name = auth_cookie_name
        self.auth_cookie_key = secrets.token_urlsafe(32)
        self.auth_credentials = self._load_auth_credentials()
        self.authenticator = stauth.Authenticate(self.auth_credentials, self.auth_cookie_name, self.auth_cookie_key)

    def _load_auth_credentials(self):
        """
        Lädt die Benutzeranmeldedaten aus der konfigurierten Datei.

        Rückgabe:
            dict: Benutzeranmeldedaten, standardmäßig ein leeres Wörterbuch, falls die Datei nicht gefunden wird.
        """
        dh = self.data_manager._get_data_handler()
        return dh.load(self.auth_credentials_file, initial_value={"usernames": {}})

    def _save_auth_credentials(self):
        """
        Speichert die aktuellen Benutzeranmeldedaten in der Datei.
        """
        dh = self.data_manager._get_data_handler()
        dh.save(self.auth_credentials_file, self.auth_credentials)

    def login_register(self, login_title='Anmelden', register_title='Registrieren'):
        """
        Zeigt die Authentifizierungsoberfläche an.
        
        Zeigt das Anmeldeformular und optional das Registrierungsformular an. Verarbeitet die
        Authentifizierungs- und Registrierungsabläufe. Stoppt die weitere Ausführung nach der Anzeige.

        Argumente:
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
        Zeigt das Anmeldeformular an und verarbeitet den Authentifizierungsstatus.
        """
        if st.session_state.get("authentication_status") is True:
            self.authenticator.logout()
        else:
            username = st.text_input("Benutzername", key="login_username")
            password = st.text_input("Passwort", type="password", key="login_password")
            login_button = st.button("Anmelden", key="login_button")

            if login_button:
                user_data = self.auth_credentials["usernames"].get(username)
                if user_data and user_data["password"] == password:
                    st.session_state["username"] = username
                    st.session_state["authentication_status"] = True
                    st.success(f"Willkommen, {username}!")
                else:
                    st.error("Benutzername oder Passwort ist falsch.")
            if stop:
                st.stop()

    def register(self, stop=True):
        """
        Zeigt das Registrierungsformular an und verarbeitet den Registrierungsablauf.
        
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
            username = st.text_input("Benutzername", key="register_username")
            email = st.text_input("E-Mail", key="register_email")
            password = st.text_input("Passwort", type="password", key="register_password")
            register_button = st.button("Registrieren", key="register_button")

            if register_button:
                # Überprüfen, ob der Benutzername bereits existiert
                if username in self.auth_credentials["usernames"]:
                    st.error("Benutzername existiert bereits. Bitte wählen Sie einen anderen.")
                    return

                # Benutzer hinzufügen
                self.auth_credentials["usernames"][username] = {
                    "email": email,
                    "password": password  # Optional: Passwort-Hashing hinzufügen
                }

                try:
                    self._save_auth_credentials()
                    st.success(f"Benutzer {username} erfolgreich registriert.")
                except Exception as e:
                    st.error(f"Fehler beim Speichern der Anmeldedaten: {e}")

                if stop:
                    st.stop()

    def go_to_login(self, login_page_py_file):
        """
        Erstellt eine Logout-Schaltfläche, die den Benutzer abmeldet und zur Anmeldeseite weiterleitet.
        Wenn der Benutzer nicht eingeloggt ist, wird die Anmeldeseite angezeigt.

        Argumente:
            login_page_py_file (str): Der Pfad zur Python-Datei, die die Anmeldeseite enthält.
        """
        if st.session_state.get("authentication_status") is not True:
            st.switch_page(login_page_py_file)
        else:
            self.authenticator.logout()