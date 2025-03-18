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
        # Beispiel: Anmeldedaten können hier statisch definiert oder aus einer Datei geladen werden
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