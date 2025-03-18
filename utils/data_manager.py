import os
import pandas as pd
import streamlit as st
import fsspec
import posixpath
from utils.data_handler import DataHandler


class DataManager:
    """
    Eine Singleton-Klasse zur Verwaltung von Anwendungsdaten und benutzerspezifischer Speicherung.
    Unterstützt lokale und WebDAV-Dateisysteme und integriert sich in den Streamlit-Session-State.
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

    def load_app_data(self, session_state_key, file_name, initial_value=None, **load_args):
        """
        Lädt Anwendungsdaten aus einer Datei und speichert sie im Streamlit-Session-State.
        """
        if session_state_key in st.session_state:
            return

        dh = self._get_data_handler()
        data = dh.load(file_name, initial_value, **load_args)
        st.session_state[session_state_key] = data
        self.app_data_reg[session_state_key] = file_name

    def load_user_data(self, session_state_key, file_name, initial_value=None, **load_args):
        """
        Lädt benutzerspezifische Daten aus einer Datei im Benutzerordner.
        """
        username = st.session_state.get('username', None)
        if username is None:
            for key in self.user_data_reg:  # Lösche alle Benutzerdaten
                st.session_state.pop(key)
            self.user_data_reg = {}
            st.error(f"DataManager: Kein Benutzer eingeloggt, Datei `{file_name}` kann nicht geladen werden.")
            return
        elif session_state_key in st.session_state:
            return

        user_data_folder = 'user_data_' + username
        dh = self._get_data_handler(user_data_folder)
        data = dh.load(file_name, initial_value, **load_args)
        st.session_state[session_state_key] = data
        self.user_data_reg[session_state_key] = dh.join(user_data_folder, file_name)

    @property
    def data_reg(self):
        """
        Gibt eine kombinierte Registrierung von Anwendungs- und Benutzerdaten zurück.
        """
        return {**self.app_data_reg, **self.user_data_reg}

    def save_data(self, session_state_key):
        """
        Speichert Daten aus dem Session-State in den persistenten Speicher.
        """
        if session_state_key not in self.data_reg:
            raise ValueError(f"DataManager: Kein Eintrag für Schlüssel {session_state_key} registriert.")

        if session_state_key not in st.session_state:
            raise ValueError(f"DataManager: Schlüssel {session_state_key} nicht im Session-State gefunden.")

        dh = self._get_data_handler()
        dh.save(self.data_reg[session_state_key], st.session_state[session_state_key])

    def save_all_data(self):
        """
        Speichert alle registrierten Daten aus dem Session-State in den persistenten Speicher.
        """
        for key in self.data_reg.keys():
            if key in st.session_state:
                self.save_data(key)

    def append_record(self, session_state_key, record_dict):
        """
        Fügt einen neuen Datensatz zu einer im Session-State gespeicherten Liste oder DataFrame hinzu.
        """
        data_value = st.session_state.get(session_state_key)

        if not isinstance(record_dict, dict):
            raise ValueError("DataManager: Der Datensatz muss ein Dictionary sein.")

        if isinstance(data_value, pd.DataFrame):
            data_value = pd.concat([data_value, pd.DataFrame([record_dict])], ignore_index=True)
        elif isinstance(data_value, list):
            data_value.append(record_dict)
        else:
            raise ValueError(f"DataManager: Der Wert für Schlüssel {session_state_key} muss ein DataFrame oder eine Liste sein.")

        st.session_state[session_state_key] = data_value
        self.save_data(session_state_key)