import os
import pandas as pd
import streamlit as st

class DataManager:
    def __init__(self, fs_protocol='local', fs_root_folder='data'):
        self.fs_protocol = fs_protocol
        self.fs_root_folder = fs_root_folder

        # Erstelle den Root-Ordner, falls er nicht existiert
        if not os.path.exists(self.fs_root_folder):
            os.makedirs(self.fs_root_folder)

    def save_user_data(self, session_state_key, username):
        """
        Speichert die nutzerspezifischen Daten in einer Datei.
        """
        # Verwende einen konsistenten Dateinamen
        user_file = os.path.join(self.fs_root_folder, f"{username}_data.csv")
        data = st.session_state.get(session_state_key)
        if data is not None and not data.empty:
            try:
                data.to_csv(user_file, index=False)
                st.write(f"Daten erfolgreich gespeichert: {user_file}")  # Debugging-Ausgabe
            except Exception as e:
                st.error(f"Fehler beim Speichern der Daten: {e}")
        else:
            st.warning(f"Keine Daten zum Speichern für Benutzer: {username}")

    def load_user_data(self, session_state_key, username, initial_value=None, parse_dates=None):
        """
        Lädt die nutzerspezifischen Daten aus einer Datei.
        """
        # Verwende denselben konsistenten Dateinamen
        user_file = os.path.join(self.fs_root_folder, f"{username}_data.csv")
        try:
            # Versuche, die Datei zu laden
            data = pd.read_csv(user_file, parse_dates=parse_dates)
        except FileNotFoundError:
            # Initialisiere mit Standardwerten, falls die Datei nicht existiert
            data = initial_value if initial_value is not None else pd.DataFrame()
        return data