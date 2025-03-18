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
        """
        Gibt den DataManager selbst als Daten-Handler zurück.
        """
        return self

    def load(self, file_name, initial_value=None):
        """
        Lädt Daten aus einer Datei.
        """
        file_path = os.path.join(self.fs_root_folder, file_name)
        try:
            with open(file_path, 'r') as file:
                return pd.read_csv(file)  # Beispiel: CSV-Datei laden
        except FileNotFoundError:
            return initial_value

    def save(self, file_name, data):
        """
        Speichert Daten in einer Datei.
        """
        file_path = os.path.join(self.fs_root_folder, file_name)
        try:
            data.to_csv(file_path, index=False)
        except Exception as e:
            st.error(f"Fehler beim Speichern der Datei {file_name}: {e}")