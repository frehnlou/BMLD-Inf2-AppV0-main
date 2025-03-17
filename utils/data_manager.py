import fsspec
import posixpath
import streamlit as st
import pandas as pd
from utils.data_handler import DataHandler

class DataManager:
    """
    Singleton-Klasse für die Verwaltung von Anwendungsdaten und benutzerspezifischer Speicherung.
    Diese Klasse bietet eine zentrale Schnittstelle für die Verwaltung von Anwendungs- und
    benutzerspezifischen Daten. Sie implementiert ein Singleton-Pattern mit Streamlit's
    Sitzungszustand, um Konsistenz zwischen App-Neustarts zu gewährleisten.
    """

    def __new__(cls, *args, **kwargs):
        """ Singleton-Pattern: Gibt die bestehende Instanz zurück, falls vorhanden. """
        if 'data_manager' in st.session_state:
            return st.session_state.data_manager
        else:
            instance = super(DataManager, cls).__new__(cls)
            st.session_state.data_manager = instance
            return instance
    
    def __init__(self, fs_protocol='file', fs_root_folder='app_data'):
        """
        Initialisiert den Data Manager mit Dateisystemkonfiguration.
        Setzt die Dateisystemschnittstelle und initialisiert Datenregister für die Anwendung.
        Falls die Instanz bereits initialisiert ist (hat 'fs' Attribut), wird die Initialisierung übersprungen.
        """
        if hasattr(self, 'fs'):  # Überprüfen, ob die Instanz bereits initialisiert ist
            return
            
        # Initialisierung der Dateisystemkomponenten
        self.fs_root_folder = fs_root_folder
        self.fs = self._init_filesystem(fs_protocol)
        self.app_data_reg = {}
        self.user_data_reg = {}

    @staticmethod
    def _init_filesystem(protocol: str):
        """
        Erstellt und konfiguriert eine fsspec-Dateisysteminstanz.

        Unterstützt das WebDAV-Protokoll mit Anmeldeinformationen aus Streamlit-Secrets und lokalen Dateisystemzugriff.
        
        Args:
            protocol: Das zu initialisierende Dateisystemprotokoll ('webdav' oder 'file')
            
        Returns:
            fsspec.AbstractFileSystem: Konfigurierte Dateisysteminstanz
            
        Raises:
            ValueError: Wenn ein nicht unterstütztes Protokoll angegeben wird
        """
        if protocol == 'webdav':
            secrets = st.secrets['webdav']
            return fsspec.filesystem('webdav', 
                                     base_url=secrets['base_url'], 
                                     auth=(secrets['username'], secrets['password']))
        elif protocol == 'file':
            return fsspec.filesystem('file')
        else:
            raise ValueError(f"DataManager: Ungültiges Dateisystemprotokoll: {protocol}")

    def _get_data_handler(self, subfolder: str = None):
        """
        Erstellt eine DataHandler-Instanz für den angegebenen Unterordner.

        Args:
            subfolder: Optionaler Unterordnerpfad relativ zum Stammordner

        Returns:
            DataHandler: Konfiguriert für Operationen im angegebenen Ordner
        """
        if subfolder is None:
            return DataHandler(self.fs, self.fs_root_folder)
        else:
            folder_path = posixpath.join(self.fs_root_folder, subfolder)
            if not self.fs.exists(folder := posixpath.join(self.fs_root_folder, subfolder)):
                self.fs.mkdir(folder)
            return DataHandler(self.fs, folder_path)

    def load_user_data(self, session_state_key, file_name, initial_value=pd.DataFrame(), **load_args):
        username = st.session_state.get('username', None)
        if username is None:
            raise ValueError("Kein Benutzer angemeldet!")

        user_folder = f"user_data_{username}"
        dh = self._get_data_handler(user_folder=user_folder)

        if not dh.exists(file_name):
            dh.save(file_name, initial_value)

        data = dh.load(file_name, initial_value, **load_args)
        st.session_state[session_state_key] = data
        self.user_data_reg[session_state_key] = dh.join(user_data_folder, file_name)
        return data

    def append_record(self, file_name, record_dict):
        username = st.session_state.get('username', None)
        if not username:
            raise ValueError("Kein Benutzer angemeldet!")

        user_data_folder = f'user_data_{username}'
        dh = self._get_data_handler(user_data_folder)

        if not dh.exists(file_name):
            dh.save(file_name, pd.DataFrame([record_dict]))
        else:
            data = dh.load(file_name)
            data = pd.concat([data, pd.DataFrame([record_dict])], ignore_index=True)
            dh.save(file_name, data)