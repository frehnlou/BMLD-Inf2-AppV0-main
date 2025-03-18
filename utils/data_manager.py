import fsspec
import posixpath
import streamlit as st
import pandas as pd
from utils.data_handler import DataHandler

class DataManager:
    """
    Verwaltet die Speicherung und das Laden von Benutzerdaten.
    Unterstützt lokale Speicherung und WebDAV.
    """

    def __init__(self, fs_protocol='file', fs_root_folder='app_data'):
        """ Initialisiert das Dateisystem für Speicherung. """
        self.fs_root_folder = fs_root_folder
        self.fs_protocol = fs_protocol
        self.fs = self._init_filesystem(fs_protocol)

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
            raise ValueError(f"⚠️ Unsupported protocol: {protocol}")

    def _get_data_handler(self):
        """ Erstellt und gibt einen Daten-Handler zurück. """
        return DataHandler(self.fs, self.fs_root_folder)

    def load_user_data(self, session_state_key, username, initial_value=None, parse_dates=None):
        """
        Lädt die Benutzerdaten aus einer Datei. Erstellt die Datei, falls nicht vorhanden.
        """
        if not username:
            st.error("⚠️ Kein Benutzername gefunden! Anmeldung erforderlich.")
            return pd.DataFrame()

        file_name = posixpath.join(self.fs_root_folder, f"{username}_data.csv")
        dh = self._get_data_handler()

        # Prüfe, ob die Datei existiert
        try:
            if not self.fs.exists(file_name):
                df = initial_value if initial_value is not None else pd.DataFrame(columns=["datum_zeit", "blutzuckerwert", "zeitpunkt"])
                dh.save(file_name, df)
                return df
        except Exception as e:
            st.error(f"⚠️ Fehler beim Zugriff auf WebDAV: {e}")
            return pd.DataFrame()

        # Datei laden
        df = dh.load(file_name, initial_value=initial_value)

        # Falls `parse_dates` definiert ist, konvertiere Spalten zu `datetime`
        if parse_dates:
            for col in parse_dates:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col])

        return df

    def save_user_data(self, session_state_key, username):
        """
        Speichert die Benutzerdaten eines Nutzers.
        """
        if not username:
            st.error("⚠️ Kein Benutzername gefunden! Anmeldung erforderlich.")
            return

        file_name = posixpath.join(self.fs_root_folder, f"{username}_data.csv")

        if session_state_key in st.session_state:
            df = st.session_state[session_state_key]
            dh = self._get_data_handler()

            # Speichern mit Fehlerbehandlung für WebDAV
            try:
                dh.save(file_name, df)
                st.success(f"✅ Daten für {username} erfolgreich gespeichert!")
            except Exception as e:
                st.error(f"⚠️ Fehler beim Speichern in WebDAV: {e}")
