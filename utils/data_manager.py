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

    def __init__(self, fs_protocol='file', fs_root_folder='app_data'):
        """ Initialisiert das Dateisystem für Speicherung. """
        if hasattr(self, '_initialized') and self._initialized:
            return  # Verhindert erneutes Initialisieren

        self.fs_root_folder = fs_root_folder
        self.fs_protocol = fs_protocol
        self.fs = self._init_filesystem(fs_protocol)  # Initialisiere das Dateisystem
        self.app_data_reg = {}
        self.user_data_reg = {}

        self._initialized = True  # Markiere als initialisiert

    def _init_filesystem(self, protocol: str):
        """ Erstellt ein Dateisystem (lokal oder WebDAV). """
        if protocol == 'webdav':
            secrets = st.secrets['webdav']
            return fsspec.filesystem('webdav',
                                     base_url=secrets['base_url'],
                                     auth=(secrets['username'], secrets['password']))
        elif protocol == 'file':
            return fsspec.filesystem('file')  # Lokales Dateisystem
        else:
            raise ValueError(f"Unsupported protocol: {protocol}")

    def _get_data_handler(self):
        """ Erstellt und gibt einen Daten-Handler zurück. """
        return DataHandler(self.fs, self.fs_root_folder)

    def load_user_data(self, session_state_key, username, initial_value=None, parse_dates=None):
        """
        Lädt die Benutzerdaten aus einer benutzerspezifischen Datei oder erstellt eine neue Datei.

        Args:
            session_state_key (str): Der Key im Streamlit Session-State für die Daten.
            username (str): Der Benutzername für die individuelle Datei.
            initial_value (pd.DataFrame, optional): Der Standardwert, falls die Datei nicht existiert.
            parse_dates (list, optional): Spaltennamen, die als Datetime geparst werden sollen.

        Returns:
            pd.DataFrame: Die geladenen Benutzerdaten.
        """
        if not username:
            st.error("⚠️ Kein Benutzername gefunden! Anmeldung erforderlich.")
            return pd.DataFrame()

        file_name = posixpath.join(self.fs_root_folder, f"{username}_data.csv")
        dh = self._get_data_handler()

        try:
            if not self.fs.exists(file_name):
                df = initial_value if initial_value is not None else pd.DataFrame()
                dh.save(file_name, df)
                return df
        except Exception as e:
            st.error(f"⚠️ Fehler beim Zugriff auf das Dateisystem: {e}")
            return pd.DataFrame()

        try:
            df = dh.load(file_name, initial_value=initial_value)
        except Exception as e:
            st.error(f"⚠️ Fehler beim Laden der Datei: {e}")
            return pd.DataFrame()

        if parse_dates:
            for col in parse_dates:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col])

        return df

    def save_user_data(self, session_state_key, username):
        """
        Speichert die Benutzerdaten in eine benutzerspezifische Datei.

        Args:
            session_state_key (str): Der Key im Streamlit Session-State für die Daten.
            username (str): Der Benutzername für die individuelle Datei.
        """
        if not username:
            st.error("⚠️ Kein Benutzername gefunden! Anmeldung erforderlich.")
            return

        file_name = posixpath.join(self.fs_root_folder, f"{username}_data.csv")

        if session_state_key in st.session_state:
            df = st.session_state[session_state_key]
            dh = self._get_data_handler()

            try:
                dh.save(file_name, df)
            except Exception as e:
                st.error(f"⚠️ Fehler beim Speichern der Daten: {e}")