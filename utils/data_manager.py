import fsspec
import posixpath
import streamlit as st
import pandas as pd
from utils.data_handler import DataHandler

class DataManager:
    """
    Klasse zur Verwaltung der Benutzerdaten.
    """

    def __init__(self, fs_protocol='file', fs_root_folder='app_data'):
        """ Initialisiert das Dateisystem für Speicherung. """
        self.fs_root_folder = fs_root_folder
        self.fs_protocol = fs_protocol
        self.fs = self._init_filesystem(fs_protocol)
        self.data_handler = DataHandler(self.fs, self.fs_root_folder)

    def _init_filesystem(self, protocol: str):
        """ Erstellt ein Dateisystem (lokal oder WebDAV). """
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
            raise ValueError(f"Unsupported protocol: {protocol}")

    def load_user_data(self, username, initial_value=None, parse_dates=None):
        """
        Lädt die Benutzerdaten aus einer Datei.

        Args:
            username (str): Der Benutzername für die individuelle Datei.
            initial_value (pd.DataFrame, optional): Standardwert, falls die Datei nicht existiert.
            parse_dates (list, optional): Spaltennamen, die als Datetime geparst werden sollen.

        Returns:
            pd.DataFrame: Die geladenen Benutzerdaten.
        """
        if not username:
            return pd.DataFrame()

        file_name = posixpath.join(self.fs_root_folder, f"{username}_data.csv")

        try:
            if not self.fs.exists(file_name):
                df = initial_value if initial_value is not None else pd.DataFrame()
                self.data_handler.save(file_name, df)
                return df
        except Exception:
            return pd.DataFrame()

        df = self.data_handler.load(file_name, initial_value=initial_value)
        
        if parse_dates:
            for col in parse_dates:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col])

        return df

    def save_user_data(self, username):
        """
        Speichert die Benutzerdaten.

        Args:
            username (str): Der Benutzername für die individuelle Datei.
        """
        if "user_data" in st.session_state:
            df = st.session_state["user_data"]
            file_name = posixpath.join(self.fs_root_folder, f"{username}_data.csv")

            try:
                self.data_handler.save(file_name, df)
                st.success("✅ Daten erfolgreich gespeichert!")
            except Exception as e:
                st.error(f"❌ Fehler beim Speichern: {e}")
