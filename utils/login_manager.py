import secrets
import streamlit as st
import streamlit_authenticator as stauth
from utils.data_manager import DataManager


class LoginManager:
    """
    Singleton-Klasse für die Verwaltung von Anwendungszustand, Speicherung und Benutzer-Authentifizierung.
    
    Verwaltet Dateisystemzugriff, Benutzeranmeldeinformationen und Authentifizierungsstatus mit Streamlit's
    Sitzungszustand für die Persistenz zwischen Neuladen der Seite.
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
        Initialisiert Dateisystem- und Authentifizierungskomponenten, falls noch nicht geschehen.

        Args:
            data_manager: Die DataManager-Instanz für die Datenspeicherung.
            auth_credentials_file (str): Die Datei für die Speicherung der Benutzerdaten.
            auth_cookie_name (str): Name des Cookies für die Sitzungsverwaltung.
        """
        if hasattr(self, 'authenticator'):  # Falls bereits initialisiert, nicht erneut ausführen
            return
        
        if data_manager is None:
            return

        # Initialisierung der Authentifizierung
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
        dh = self.data_manager.__get_data__handler()
        dh.save(self.auth_credentials_file, self.auth_credentials)

    def login_register(self, login_title="Anmeldung", register_title="Neuen Benutzer registrieren"):
        """
        Zeigt das Anmelde- und Registrierungsformular an.

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
        Zeigt das Registrierungsformular an und ersetzt englische Labels in Deutsch.
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

            # ✅ Fehlerhafte Parameter entfernt!
            res = self.authenticator.register_user()

            if res and res[1] is not None:
                st.success(f"✅ Benutzer {res[1]} wurde erfolgreich registriert!")
                try:
                    self._save_auth_credentials()
                    st.success("✅ Zugangsdaten wurden gespeichert.")
                except Exception as e:
                    st.error(f"⚠️ Fehler beim Speichern der Zugangsdaten: {e}")

            # 🔥 Workaround: Labels mit JavaScript ins Deutsche übersetzen
            st.markdown(
                """
                <script>
                setTimeout(() => {
                    let labels = {
                        "Register user": "Benutzer registrieren",
                        "First name": "Vorname",
                        "Last name": "Nachname",
                        "Email": "E-Mail",
                        "Username": "Benutzername",
                        "Password": "Passwort",
                        "Repeat password": "Passwort wiederholen",
                        "Password hint": "Passworthinweis",
                        "Captcha": "Sicherheitscode"
                    };
                    
                    document.querySelectorAll("label").forEach(label => {
                        let text = label.innerText.trim();
                        if (labels[text]) {
                            label.innerText = labels[text];
                        }
                    });
                    console.log("Labels wurden übersetzt.");
                }, 2000);  // Erhöhte Verzögerung auf 2000ms
                </script>
                """,
                unsafe_allow_html=True
            )

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