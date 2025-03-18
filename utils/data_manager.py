import fsspec
import posixpath
import streamlit as st
import pandas as pd
from utils.data_handler import DataHandler  # Stelle sicher, dass dies korrekt ist!

class DataManager:
    """
    Eine Singleton-Klasse zur Verwaltung der Anwendungsdaten und Benutzerspeicherung.

    Diese Klasse verwendet Streamlit Session-State für Konsistenz zwischen Reruns.
    Sie unterstützt lokale Speicherung sowie WebDAV für die Synchronisation.
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
        if hasattr(self, 'fs'):  # Verhindert erneutes Initialisieren
            return

        self.fs_root_folder = fs_root_folder
        self.fs = self._init_filesystem(fs_protocol)
        self.app_data_reg = {}
        self.user_data_reg = {}

    def _init_filesystem(self, protocol: str):
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

    def _get_data_handler(self, subfolder: str = None):
        """ Erstellt und gibt einen Daten-Handler zurück. """
        if subfolder:
            return DataHandler(self.fs, posixpath.join(self.fs_root_folder, subfolder))
        return DataHandler(self.fs, self.fs_root_folder)

    def load_user_data(self, session_state_key, username, initial_value=None, parse_dates=None):
        """
        Lädt die Benutzerdaten aus einer Datei.

        Args:
            session_state_key (str): Key im Streamlit Session-State für die Daten.
            username (str): Benutzername für die individuelle Datei.
            initial_value (pd.DataFrame, optional): Standardwert, falls die Datei nicht existiert.
            parse_dates (list, optional): Spaltennamen, die als Datetime geparst werden sollen.

        Returns:
            pd.DataFrame: Die geladenen Benutzerdaten.
        """
        if not username:
            st.error("⚠️ Kein Benutzername gefunden! Anmeldung erforderlich.")
            return pd.DataFrame()

        file_name = posixpath.join(self.fs_root_folder, f"user_data_{username}.csv")  # 🔥 Speichert in WebDAV
        dh = self._get_data_handler()
        
        # Prüfe, ob die Datei existiert (Fehlerbehandlung für WebDAV)
        try:
            if not self.fs.exists(file_name):
                df = initial_value if initial_value is not None else pd.DataFrame()
                dh.save(file_name, df)
                return df
        except Exception as e:
            st.error(f"⚠️ Fehler beim Zugriff auf WebDAV: {e}")
            return pd.DataFrame()

        # Lade die Datei
        df = dh.load(file_name, initial_value=initial_value)
        
        # Falls parse_dates definiert ist, konvertiere Spalten zu Datetime
        if parse_dates:
            for col in parse_dates:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col])
        
        return df

    def save_user_data(self, session_state_key, username):
        """
        Speichert die Benutzerdaten in eine Datei.

        Args:
            session_state_key (str): Key im Streamlit Session-State für die Daten.
            username (str): Benutzername für die individuelle Datei.
        """
        if not username:
            st.error("⚠️ Kein Benutzername gefunden! Anmeldung erforderlich.")
            return

        file_name = posixpath.join(self.fs_root_folder, f"user_data_{username}.csv")

        if session_state_key in st.session_state:
            df = st.session_state[session_state_key]
            dh = self._get_data_handler()

            try:
                dh.save(file_name, df)
                st.success(f"✅ Daten für {username} erfolgreich gespeichert!")  
            except Exception as e:
                st.error(f"⚠️ Fehler beim Speichern in WebDAV: {e}")

    def append_record(self, session_state_key, record_dict):
        """
        Fügt einen neuen Eintrag zu den gespeicherten Daten hinzu.

        Args:
            session_state_key (str): Der Key im Streamlit Session-State für die Daten.
            record_dict (dict): Eintrag, der hinzugefügt wird.
        """
        if session_state_key not in st.session_state:
            st.session_state[session_state_key] = pd.DataFrame(columns=record_dict.keys())

        df = st.session_state[session_state_key]
        df = pd.concat([df, pd.DataFrame([record_dict])], ignore_index=True)
        st.session_state[session_state_key] = df

    def save_all_data(self):
        """
        Speichert alle registrierten Daten in den entsprechenden Dateien.
        """
        for key in list(self.app_data_reg.keys()) + list(self.user_data_reg.keys()):
            self.save_data(key)

    def save_data(self, session_state_key):
        """
        Speichert eine einzelne Datenquelle aus dem Streamlit Session-State.

        Args:
            session_state_key (str): Der Key im Streamlit Session-State für die Daten.
        """
        if session_state_key not in st.session_state:
            st.error(f"⚠️ Daten für {session_state_key} nicht im Session-State gefunden!")
            return

        file_name = self.app_data_reg.get(session_state_key) or self.user_data_reg.get(session_state_key)
        if not file_name:
            st.error(f"⚠️ Kein Speicherort für {session_state_key} registriert!")
            return

        dh = self._get_data_handler()
        try:
            dh.save(file_name, st.session_state[session_state_key])
            st.success(f"✅ Daten erfolgreich gespeichert!")
        except Exception as e:
            st.error(f"⚠️ Fehler beim Speichern der Datei: {e}")
