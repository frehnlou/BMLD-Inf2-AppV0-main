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

    def _new_(cls, *args, **kwargs):
        """ Singleton-Pattern: Gibt die bestehende Instanz zurück, falls vorhanden. """
        if 'data_manager' in st.session_state:
            return st.session_state.data_manager
        else:
            instance = super(DataManager, cls)._new_(cls)
            st.session_state.data_manager = instance
            return instance
    
    def _init_(self, fs_protocol='file', fs_root_folder='app_data'):
        """
        Initialisiert den Data Manager mit Dateisystemkonfiguration.
        Setzt die Dateisystemschnittstelle und initialisiert Datenregister für die Anwendung.
        Falls die Instanz bereits initialisiert ist (hat 'fs' Attribut), wird die Initialisierung übersprungen.
        """
        if hasattr(self, 'fs'):  # Falls schon initialisiert, überspringen
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
            
            # 🔥 Falls Benutzerverzeichnis nicht existiert → Erstellen
            if not self.fs.exists(folder_path):
                self.fs.mkdir(folder_path)
                
            return DataHandler(self.fs, folder_path)

    def load_user_data(self, session_state_key, file_name, initial_value=pd.DataFrame(), **load_args):
        """
        Lädt benutzerspezifische Daten aus einer Datei im Benutzerordner.
        Falls die Datei nicht existiert, wird sie mit initialen Werten erstellt.

        Args:
            session_state_key (str): Schlüssel im Sitzungszustand
            file_name (str): Name der Datei
            initial_value: Standardwert, falls Datei nicht existiert
            **load_args: Zusätzliche Parameter für das Laden

        Returns:
            Geladene Daten als Pandas DataFrame
        """
        username = st.session_state.get('username', None)
        if username is None:
            raise ValueError("❌ Kein Benutzer angemeldet!")

        user_folder = f"user_data_{username}"
        dh = self._get_data_handler(subfolder=user_folder)

        # Falls Datei nicht existiert, erstelle sie mit initial_value
        if not dh.exists(file_name):
            dh.save(file_name, initial_value)

        data = dh.load(file_name, initial_value, **load_args)
        
        # 🔧 Korrektur: Pfad wird nun mit posixpath.join() erstellt
        user_data_path = posixpath.join(user_folder, file_name)

        # Speichern im Session State
        st.session_state[session_state_key] = data
        self.user_data_reg[session_state_key] = user_data_path  
        
        return data

    def append_record(self, file_name, record_dict):
        """
        Fügt eine neue Zeile zu einer bestehenden CSV-Datei im Benutzerverzeichnis hinzu.

        Args:
            file_name (str): Name der Datei
            record_dict (dict): Die neue Zeile als Dictionary
        """
        username = st.session_state.get('username', None)
        if not username:
            raise ValueError("❌ Kein Benutzer angemeldet!")

        # 🔥 Benutzerordner explizit definieren
        user_data_folder = f"user_data_{username}"
        
        # ✅ Stelle sicher, dass der Ordner existiert
        dh = self._get_data_handler(subfolder=user_data_folder)

        if not dh.exists(file_name):
            dh.save(file_name, pd.DataFrame([record_dict]))
        else:
            data = dh.load(file_name)
            data = pd.concat([data, pd.DataFrame([record_dict])], ignore_index=True)
            dh.save(file_name, data)

    def save_user_data(self, session_state_key, file_name):
        """
        Speichert die Benutzerdaten in der Datei.

        Args:
            session_state_key (str): Schlüssel im Sitzungszustand
            file_name (str): Name der Datei
        """
        username = st.session_state.get('username', None)
        if not username:
            raise ValueError("❌ Kein Benutzer angemeldet!")

        user_folder = f"user_data_{username}"
        dh = self._get_data_handler(subfolder=user_folder)

        if session_state_key in st.session_state:
            dh.save(file_name, st.session_state[session_state_key])

    def load_data(self, session_state_key, file_name, initial_value=None, **load_args):
        """
        Lädt allgemeine Anwendungsdaten.

        Args:
            session_state_key (str): Schlüssel im Streamlit-Session-State
            file_name (str): Name der Datei
            initial_value: Standardwert, falls Datei nicht existiert

        Returns:
            Geladene Daten als Pandas DataFrame oder initial_value
        """
        dh = self._get_data_handler()
        if not dh.exists(file_name):
            if initial_value is not None:
                return initial_value
            raise FileNotFoundError(f"Datei nicht gefunden: {file_name}")

        data = dh.load(file_name, initial_value, **load_args)
        st.session_state[session_state_key] = data
        return data