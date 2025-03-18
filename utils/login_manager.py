import yaml
import os
import streamlit as st
from utils.data_manager import DataManager

class LoginManager:
    def __init__(self, data_manager, auth_credentials_file='credentials.yaml'):
        """
        Initialisiert den LoginManager mit dem DataManager und stellt sicher, dass credentials.yaml existiert.
        """
        self.data_manager = data_manager
        self.auth_credentials_file = auth_credentials_file

        # Falls die Datei nicht existiert, wird sie automatisch erstellt
        if not os.path.exists(self.auth_credentials_file):
            st.warning("⚠️ `credentials.yaml` nicht gefunden. Neue Datei wird erstellt.")
            self.auth_credentials = {"usernames": {}}  # Leere Struktur
            self._save_auth_credentials()  # Datei speichern
        else:
            self.auth_credentials = self._load_auth_credentials()

    def _load_auth_credentials(self):
        """
        Lädt die Anmeldedaten aus der Datei.
        """
        try:
            with open(self.auth_credentials_file, 'r') as file:
                data = yaml.safe_load(file) or {"usernames": {}}
                st.write(f"📂 Geladene Anmeldedaten: {data}")  # Debugging
                return data
        except FileNotFoundError:
            st.warning("⚠️ Datei nicht gefunden. Erstelle neue Datei.")
            return {"usernames": {}}
        except Exception as e:
            st.error(f"❌ Fehler beim Laden von `credentials.yaml`: {e}")
            return {"usernames": {}}

    def _save_auth_credentials(self):
        """
        Speichert die Anmeldedaten in der Datei.
        """
        try:
            with open(self.auth_credentials_file, 'w') as file:
                yaml.safe_dump(self.auth_credentials, file)
            st.write("✅ Anmeldedaten erfolgreich gespeichert.")  # Debugging
        except Exception as e:
            st.error(f"❌ Fehler beim Speichern von `credentials.yaml`: {e}")

    def register_user(self, username, password, email):
        """
        Registriert einen neuen Benutzer und speichert die Anmeldedaten.
        """
        if username in self.auth_credentials["usernames"]:
            st.error("❌ Benutzername existiert bereits.")
            return False

        # Passwort-Hashing kann hier hinzugefügt werden
        hashed_password = password  

        self.auth_credentials["usernames"][username] = {
            "email": email,
            "password": hashed_password
        }
        self._save_auth_credentials()
        st.success(f"✅ Benutzer {username} erfolgreich registriert.")
        return True

    def login(self):
        """
        Authentifiziert den Benutzer basierend auf den gespeicherten Anmeldedaten.
        """
        username = st.text_input("Benutzername")
        password = st.text_input("Passwort", type="password")
        login_button = st.button("Anmelden")

        if login_button:
            user_data = self.auth_credentials["usernames"].get(username)
            if user_data and user_data["password"] == password:  
                st.session_state["username"] = username
                st.session_state["authentication_status"] = True
                st.success(f"🎉 Willkommen, {username}!")
            else:
                st.error("❌ Benutzername oder Passwort ist falsch.")

    def login_register(self):
        """
        Zeigt die Login- und Registrierungsoberfläche an.
        """
        login_tab, register_tab = st.tabs(["Login", "Registrieren"])
        with login_tab:
            self.login()
        with register_tab:
            self.register()

    def register(self):
        """
        Registriert einen neuen Benutzer.
        """
        username = st.text_input("Benutzername")
        email = st.text_input("E-Mail")
        password = st.text_input("Passwort", type="password")
        register_button = st.button("Registrieren")

        if register_button:
            if self.register_user(username, password, email):
                st.success("✅ Registrierung erfolgreich. Bitte melden Sie sich an.")
