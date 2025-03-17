import fsspec
import posixpath
import streamlit as st
import pandas as pd
from utils.data_handler import DataHandler

class DataManager:
    """
    Singleton-Klasse für das Management von Anwendungsdaten und Benutzerspeicherung.
    Diese Klasse verwendet das Streamlit Session-State für Konsistenz zwischen Reruns.
    """

    def __new__(cls, *args, **kwargs):
        """ Singleton-Pattern: Gibt die bestehende Instanz zurück, falls vorhanden. """
        if 'data_manager' in st.session_state:
            return st.session_state.data_manager
        else:
            instance = super(DataManager, cls).__new__(cls)
            st.session_state.data_manager = instance
            return instance
    
    def _init_(self, fs_protocol='file', fs_root_folder='app_data'):
        """ Initialisiert das Dateisystem für Speicherung. """
        if hasattr(self, 'fs'):  # Falls schon initialisiert, überspringen
            return
            
        self.fs_root_folder = fs_root_folder
        self.fs = self._init_filesystem(fs_protocol)
        self.app_data_reg = {}
        self.user_data_reg = {}

    @staticmethod
    def _init_filesystem(protocol: str):
        """ Erstellt ein Dateisystem (lokal oder WebDAV). """
        if protocol == 'webdav':
            secrets = st.secrets['webdav']
            return fsspec.filesystem('webdav', 
                                     base_url=secrets['base_url'], 
                                     auth=(secrets['username'], secrets['password']))
        elif protocol == 'file':
            return fsspec.filesystem('file')
        else:
            raise ValueError(f"Unsupported protocol: {protocol}")

# Beispiel für die Verwendung der DataManager-Klasse
data_manager = DataManager(fs_protocol='webdav', fs_root_folder="BMLD_cblsf_App")