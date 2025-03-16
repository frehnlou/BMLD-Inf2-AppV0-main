import fsspec
import posixpath
import streamlit as st
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
            return DataHandler(self.fs, posixpath.join(self.fs_root_folder, subfolder))

    def load_app_data(self, session_state_key, file_name, initial_value=None, **load_args):
        """
        Lädt Anwendungsdaten aus einer Datei und speichert sie im Streamlit-Sitzungszustand.

        Args:
            session_state_key (str): Schlüssel, unter dem die Daten im Sitzungszustand von Streamlit gespeichert werden
            file_name (str): Name der Datei, aus der die Daten geladen werden sollen
            initial_value (Any, optional): Standardwert, falls die Datei nicht existiert. Standard ist None.
            **load_args: Zusätzliche Schlüsselwortargumente, die an die Load-Methode des Data Handlers übergeben werden

        Returns:
            None: Die geladenen Daten werden direkt im Sitzungszustand von Streamlit gespeichert

        Note:
            Die Methode registriert auch den Dateinamen im app_data_reg-Wörterbuch unter Verwendung des session_state_key
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

        Args:
            session_state_key (str): Schlüssel, unter dem die Daten im Sitzungszustand von Streamlit gespeichert werden
            file_name (str): Name der Datei, aus der die Daten geladen werden sollen
            initial_value: Standardwert, falls die Datei nicht existiert (Standard: None)
            **load_args: Zusätzliche Argumente, die an die Load-Methode des Data Handlers übergeben werden

        Returns:
            Die geladenen Daten aus der Datei

        Raises:
            ValueError: Wenn kein Benutzer aktuell angemeldet ist

        Notes:
            - Die Methode registriert den Dateinamen im user_data_reg-Wörterbuch
            - Der Benutzerordner wird als 'user_data_<username>' benannt
            - Wenn kein Benutzer angemeldet ist, werden alle Benutzerdaten aus dem Sitzungszustand gelöscht
        """
        username = st.session_state.get('username', None)
        if username is None:
            for key in self.user_data_reg:  # Alle Benutzerdaten löschen
                st.session_state.pop(key)
            self.user_data_reg = {}
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
        return {**self.app_data_reg, **self.user_data_reg}

    def save_data(self, session_state_key):
        """
        Speichert Daten aus dem Sitzungszustand in den persistenten Speicher unter Verwendung des registrierten Data Handlers.

        Args:
            session_state_key (str): Schlüssel, der die Daten sowohl im Sitzungszustand als auch im Datenregister identifiziert

        Raises:
            ValueError: Wenn der session_state_key nicht im data_reg registriert ist
            ValueError: Wenn der session_state_key nicht im Sitzungszustand gefunden wird

        Example:
            >>> data_manager.save_data("user_settings")
        """
        if session_state_key not in self.data_reg:
            raise ValueError(f"DataManager: Keine Daten für den Sitzungszustandsschlüssel {session_state_key} registriert")
        
        if session_state_key not in st.session_state:
            raise ValueError(f"DataManager: Schlüssel {session_state_key} nicht im Sitzungszustand gefunden")
        
        dh = self._get_data_handler()
        dh.save(self.data_reg[session_state_key], st.session_state[session_state_key])

    def save_all_data(self):
        """
        Speichert alle gültigen Daten aus dem Sitzungszustand in den persistenten Speicher.

        Diese Methode iteriert durch alle registrierten Datenschlüssel und speichert die entsprechenden 
        Daten, falls sie im aktuellen Sitzungszustand existieren.

        Verwendet intern die save_data() Methode für jeden einzelnen Schlüssel.
        """
        keys = [key for key in self.data_reg.keys() if key in st.session_state]
        for key in keys:
            self.save_data(key)

    def append_record(self, session_state_key, record_dict):
        if session_state_key not in st.session_state:
            st.session_state[session_state_key] = []
        st.session_state[session_state_key].append(record_dict)
        # Code hinzufügen, um die Daten bei Bedarf zu speichern