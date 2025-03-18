import os
import pandas as pd
import streamlit as st
import fsspec
import posixpath
from utils.data_handler import DataHandler

class DataManager:
    def __init__(self, fs_protocol='file', fs_root_folder='app_data'):
        self.fs_protocol = fs_protocol
        self.fs_root_folder = fs_root_folder

        # Erstelle den Root-Ordner, falls er nicht existiert
        if not os.path.exists(self.fs_root_folder):
            os.makedirs(self.fs_root_folder)

    def load_user_data(self, session_state_key, file_name, initial_value=None, **load_args):
        """
        Lädt benutzerspezifische Daten aus einer Datei im Benutzerordner.
        """
        username = st.session_state.get('username', None)
        if username is None:
            st.error("DataManager: Kein Benutzer eingeloggt. Daten können nicht geladen werden.")
            return initial_value if initial_value is not None else pd.DataFrame()

        user_folder = os.path.join(self.fs_root_folder, f"user_data_{username}")
        if not os.path.exists(user_folder):
            os.makedirs(user_folder)

        file_path = os.path.join(user_folder, file_name)

        try:
            return pd.read_csv(file_path, **load_args)
        except FileNotFoundError:
            return initial_value if initial_value is not None else pd.DataFrame()

    def save_user_data(self, session_state_key, file_name):
        """
        Speichert benutzerspezifische Daten in einer Datei im Benutzerordner.
        """
        username = st.session_state.get('username', None)
        if username is None:
            st.error("DataManager: Kein Benutzer eingeloggt. Daten können nicht gespeichert werden.")
            return

        user_folder = os.path.join(self.fs_root_folder, f"user_data_{username}")
        if not os.path.exists(user_folder):
            os.makedirs(user_folder)

        file_path = os.path.join(user_folder, file_name)

        data = st.session_state.get(session_state_key, None)
        if data is not None:
            data.to_csv(file_path, index=False)