import os
import pandas as pd
import streamlit as st
from utils.data_handler import DataHandler

class DataManager:
    def __init__(self, fs_protocol='file', fs_root_folder='app_data'):
        """
        Initialisiert den DataManager.

        Args:
            fs_protocol (str): Das Protokoll für das Dateisystem (z. B. 'file').
            fs_root_folder (str): Der Root-Ordner für alle Dateioperationen.
        """
        self.fs_protocol = fs_protocol
        self.fs_root_folder = fs_root_folder

        # Erstelle den Root-Ordner, falls er nicht existiert
        if not os.path.exists(self.fs_root_folder):
            os.makedirs(self.fs_root_folder)

    def _get_data_handler(self, subfolder=None):
        """
        Erstellt eine DataHandler-Instanz für Dateioperationen.

        Args:
            subfolder (str): Optionaler Unterordner relativ zum Root-Ordner.

        Returns:
            DataHandler: Eine Instanz des DataHandlers.
        """
        if subfolder is None:
            return DataHandler(self.fs_protocol, self.fs_root_folder)
        else:
            return DataHandler(self.fs_protocol, os.path.join(self.fs_root_folder, subfolder))

    def load_user_data(self, session_state_key, file_name, initial_value=None, **load_args):
        """
        Lädt benutzerspezifische Daten aus einer Datei im Benutzerordner.

        Args:
            session_state_key (str): Der Schlüssel im Session-State, unter dem die Daten gespeichert werden.
            file_name (str): Der Name der Datei, aus der die Daten geladen werden.
            initial_value: Der Standardwert, falls die Datei nicht existiert.
            **load_args: Zusätzliche Argumente für die Ladefunktion.

        Returns:
            pd.DataFrame: Die geladenen Daten oder der Standardwert.
        """
        username = st.session_state.get('username', None)
        if username is None:
            st.error("⚠️ Kein Benutzer eingeloggt. Daten können nicht geladen werden.")
            return initial_value if initial_value is not None else pd.DataFrame()

        # Benutzerordner erstellen, falls er nicht existiert
        user_folder = os.path.join(self.fs_root_folder, f"user_data_{username}")
        data_handler = self._get_data_handler(user_folder)

        try:
            return data_handler.load(file_name, initial_value=initial_value, **load_args)
        except FileNotFoundError:
            st.warning(f"⚠️ Datei {file_name} nicht gefunden. Rückgabe des Standardwerts.")
            return initial_value if initial_value is not None else pd.DataFrame()
        except Exception as e:
            st.error(f"❌ Fehler beim Laden der Datei {file_name}: {e}")
            return initial_value if initial_value is not None else pd.DataFrame()

    def save_user_data(self, session_state_key, file_name):
        """
        Speichert benutzerspezifische Daten in einer Datei im Benutzerordner.

        Args:
            session_state_key (str): Der Schlüssel im Session-State, unter dem die Daten gespeichert sind.
            file_name (str): Der Name der Datei, in der die Daten gespeichert werden sollen.
        """
        username = st.session_state.get('username', None)
        if username is None:
            st.error("⚠️ Kein Benutzer eingeloggt. Daten können nicht gespeichert werden.")
            return

        # Benutzerordner erstellen, falls er nicht existiert
        user_folder = os.path.join(self.fs_root_folder, f"user_data_{username}")
        data_handler = self._get_data_handler(user_folder)

        data = st.session_state.get(session_state_key, None)
        if data is not None:
            try:
                data_handler.save(file_name, data)
                st.success(f"✅ Daten erfolgreich in {file_name} gespeichert.")
            except Exception as e:
                st.error(f"❌ Fehler beim Speichern der Datei {file_name}: {e}")
        else:
            st.warning(f"⚠️ Keine Daten im Session-State unter {session_state_key} gefunden.")