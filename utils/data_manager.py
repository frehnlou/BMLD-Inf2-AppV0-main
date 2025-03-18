import os
import pandas as pd
import streamlit as st
import fsspec
import posixpath
from utils.data_handler import DataHandler


class DataManager:
    """
    Eine Singleton-Klasse zur Verwaltung von Anwendungs- und Benutzerdaten mit persistenter Speicherung.
    Unterstützt Multi-User-Umgebungen und speichert Daten für jeden Benutzer separat.
    """

    def __new__(cls, *args, **kwargs):
        """
        Implementiert das Singleton-Muster, indem die vorhandene Instanz aus dem Session-State zurückgegeben wird.
        """
        if 'data_manager' in st.session_state:
            return st.session_state.data_manager
        else:
            instance = super(DataManager, cls).__new__(cls)
            st.session_state.data_manager = instance
            return instance

    def __init__(self, fs_protocol='file', fs_root_folder='app_data'):
        """
        Initialisiert den DataManager mit Konfigurationen für das Dateisystem.
        """
        if hasattr(self, 'fs'):  # Überprüfen, ob die Instanz bereits initialisiert ist
            return

        self.fs_root_folder = fs_root_folder
        self.fs = self._init_filesystem(fs_protocol)
        self.app_data_reg = {}
        self.user_data_reg = {}

        # Erstelle den Root-Ordner, falls er nicht existiert
        if not os.path.exists(self.fs_root_folder):
            os.makedirs(self.fs_root_folder)

    @staticmethod
    def _init_filesystem(protocol: str):
        """
        Erstellt und konfiguriert eine fsspec-Dateisysteminstanz.
        """
        if protocol == 'webdav':
            secrets = st.secrets['webdav']
            return fsspec.filesystem(
                'webdav',
                base_url=secrets['base_url'],
                auth=(secrets['username'], secrets['password'])
            )
        elif protocol == 'file':
            return fsspec.filesystem('file')
        else:
            raise ValueError(f"DataManager: Ungültiges Dateisystemprotokoll: {protocol}")

    def _get_data_handler(self, subfolder: str = None):
        """
        Erstellt eine DataHandler-Instanz für den angegebenen Unterordner.
        """
        if subfolder is None:
            return DataHandler(self.fs, self.fs_root_folder)
        else:
            return DataHandler(self.fs, posixpath.join(self.fs_root_folder, subfolder))

    def load_user_data(self, session_state_key, file_name, initial_value=None, **load_args):
        """
        Lädt benutzerspezifische Daten aus einer Datei im Benutzerordner.

        Args:
            session_state_key (str): Schlüssel im Session-State, unter dem die Daten gespeichert werden.
            file_name (str): Name der Datei, aus der die Daten geladen werden.
            initial_value: Standardwert, falls die Datei nicht existiert.
            **load_args: Zusätzliche Argumente für die Ladefunktion.

        Returns:
            pd.DataFrame: Die geladenen oder initialisierten Benutzerdaten.
        """
        username = st.session_state.get('username', None)
        if username is None:
            st.error("DataManager: Kein Benutzer eingeloggt. Daten können nicht geladen werden.")
            return initial_value

        user_folder = os.path.join(self.fs_root_folder, f"user_data_{username}")
        if not os.path.exists(user_folder):
            os.makedirs(user_folder)

        file_path = os.path.join(user_folder, file_name)

        try:
            return pd.read_csv(file_path, **load_args)
        except FileNotFoundError:
            return initial_value

    def save_user_data(self, session_state_key, file_name):
        """
        Speichert benutzerspezifische Daten in einer Datei im Benutzerordner.

        Args:
            session_state_key (str): Schlüssel im Session-State, unter dem die Daten gespeichert sind.
            file_name (str): Name der Datei, in der die Daten gespeichert werden.
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

    def append_record(self, session_state_key, record_dict):
        """
        Fügt einen neuen Datensatz zu einer im Session-State gespeicherten Liste oder DataFrame hinzu.

        Args:
            session_state_key (str): Schlüssel im Session-State, unter dem die Daten gespeichert sind.
            record_dict (dict): Neuer Datensatz, der hinzugefügt werden soll.
        """
        data = st.session_state.get(session_state_key, None)

        if data is None:
            st.error(f"DataManager: Keine Daten für Schlüssel {session_state_key} gefunden.")
            return

        if isinstance(data, pd.DataFrame):
            new_data = pd.DataFrame([record_dict])
            st.session_state[session_state_key] = pd.concat([data, new_data], ignore_index=True)
        elif isinstance(data, list):
            data.append(record_dict)
            st.session_state[session_state_key] = data
        else:
            st.error(f"DataManager: Daten für Schlüssel {session_state_key} müssen ein DataFrame oder eine Liste sein.")