import os
import pandas as pd
import streamlit as st

class DataManager:
    def __init__(self, fs_protocol='local', fs_root_folder='data'):
        self.fs_protocol = fs_protocol
        self.fs_root_folder = fs_root_folder

        # Erstelle den Root-Ordner, falls er nicht existiert
        if not os.path.exists(self.fs_root_folder):
            os.makedirs(self.fs_root_folder)

    def _get_data_handler(self):
        return self

    def load(self, file_name, initial_value=None):
        file_path = os.path.join(self.fs_root_folder, file_name)
        try:
            return pd.read_csv(file_path)
        except FileNotFoundError:
            return initial_value

    def save(self, file_name, data):
        file_path = os.path.join(self.fs_root_folder, file_name)
        data.to_csv(file_path, index=False)

    def get_credentials(self):
        """
        Gibt die Anmeldedaten zurück, die von streamlit_authenticator benötigt werden.
        """
        credentials = {
            "usernames": {
                "admin": {
                    "email": "admin@example.com",
                    "name": "Admin",
                    "password": "$2b$12$KIXQ1vZ8QJH6FJ9Q9Q9Q9u9Q9Q9Q9Q9Q9Q9Q9Q9Q9Q9Q9Q9"  # Beispiel für ein gehashtes Passwort
                }
            }
        }
        return credentials

    def load_user_data(self, session_state_key, username, initial_value=None, parse_dates=None):
        """
        Lädt die Benutzerdaten aus einer Datei oder initialisiert sie, falls keine vorhanden sind.

        Args:
            session_state_key (str): Der Schlüssel im Session-State, unter dem die Daten gespeichert werden.
            username (str): Der Benutzername, um die Datei zu identifizieren.
            initial_value: Der Standardwert, falls keine Datei vorhanden ist.
            parse_dates (list): Spalten, die als Datumswerte geparst werden sollen.

        Returns:
            pd.DataFrame: Die geladenen oder initialisierten Benutzerdaten.
        """
        file_name = f"{username}_data.csv"
        file_path = os.path.join(self.fs_root_folder, file_name)

        try:
            return pd.read_csv(file_path, parse_dates=parse_dates)
        except FileNotFoundError:
            # Falls die Datei nicht existiert, initialisiere mit dem Standardwert
            return initial_value

    def save_user_data(self, session_state_key, username):
        """
        Speichert die Benutzerdaten in einer Datei.

        Args:
            session_state_key (str): Der Schlüssel im Session-State, unter dem die Daten gespeichert werden.
            username (str): Der Benutzername, um die Datei zu identifizieren.
        """
        file_name = f"{username}_data.csv"
        file_path = os.path.join(self.fs_root_folder, file_name)

        # Speichere die Daten aus dem Session-State
        user_data = st.session_state.get(session_state_key)
        if user_data is not None:
            user_data.to_csv(file_path, index=False)