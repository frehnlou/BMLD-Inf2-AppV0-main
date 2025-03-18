import os
import pandas as pd
import streamlit as st
import streamlit_authenticator as stauth
import secrets

class LoginManager:
    """
    Verwaltet die Benutzer-Authentifizierung und den Zugriff auf Anmeldedaten.
    """

    def __init__(self, data_manager, auth_credentials_file='credentials.yaml', auth_cookie_name='auth_cookie'):
        """
        Initialisiert den LoginManager.

        Args:
            data_manager (DataManager): Instanz des DataManager zum Laden/Speichern von Daten.
            auth_credentials_file (str): Pfad zur Datei mit den Anmeldedaten.
            auth_cookie_name (str): Name des Cookies für die Sitzungsverwaltung.
        """
        self.data_manager = data_manager
        self.auth_credentials_file = auth_credentials_file
        self.auth_cookie_name = auth_cookie_name
        self.auth_cookie_key = secrets.token_urlsafe(32)  # Generiere einen zufälligen Schlüssel
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
        Lädt die Benutzeranmeldedaten aus der Datei.

        Returns:
            dict: Benutzeranmeldedaten.
        """
        try:
            return self.data_manager.load(self.auth_credentials_file, initial_value={"usernames": {}})
        except Exception as e:
            st.error(f"Fehler beim Laden der Anmeldedaten: {e}")
            return {"usernames": {}}

    def _save_auth_credentials(self):
        """
        Speichert die Benutzeranmeldedaten in der Datei.
        """
        try:
            self.data_manager.save(self.auth_credentials_file, self.auth_credentials)
        except Exception as e:
            st.error(f"Fehler beim Speichern der Anmeldedaten: {e}")

    def login_register(self):
        """
        Zeigt die Login- und Registrierungsoberfläche an.
        """
        if st.session_state.get("authentication_status") is True:
            self.authenticator.logout("Logout", "sidebar")
        else:
            login_tab, register_tab = st.tabs(["Login", "Registrieren"])
            with login_tab:
                self.login()
            with register_tab:
                self.register()

    def login(self):
        """
        Zeigt das Login-Formular an und verarbeitet die Anmeldung.
        """
        # Debugging-Ausgabe
        st.write("Debug: Login wird aufgerufen mit location='sidebar'")
        try:
            # Stelle sicher, dass der Parameter "location" korrekt ist
            name, authentication_status, username = self.authenticator.login("Login", location="sidebar")
            if authentication_status:
                st.success(f"Willkommen {name}!")
            elif authentication_status is False:
                st.error("Benutzername oder Passwort ist falsch.")
            elif authentication_status is None:
                st.warning("Bitte geben Sie Ihre Anmeldedaten ein.")
        except ValueError as e:
            st.error(f"Fehler: {e}")

    def register(self):
        """
        Zeigt das Registrierungsformular an und verarbeitet die Registrierung.
        """
        st.markdown("""
        **Passwortanforderungen:**
        - Mindestens 8 Zeichen
        - Mindestens ein Großbuchstabe
        - Mindestens ein Kleinbuchstabe
        - Mindestens eine Zahl
        - Mindestens ein Sonderzeichen (@$!%*?&)
        """)

        try:
            if self.authenticator.register_user("Registrieren", preauthorization=False):
                st.success("Benutzer erfolgreich registriert!")
                self._save_auth_credentials()
        except Exception as e:
            st.error(f"Fehler bei der Registrierung: {e}")

    def go_to_login(self, login_page_py_file):
        """
        Leitet den Benutzer zur Login-Seite weiter, falls nicht eingeloggt.

        Args:
            login_page_py_file (str): Name der Login-Seite.
        """
        if st.session_state.get("authentication_status") is not True:
            st.warning("Bitte melden Sie sich an.")
            st.stop()