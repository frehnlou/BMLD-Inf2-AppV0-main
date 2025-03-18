import pandas as pd
import os

class DataManager:
    def __init__(self, fs_protocol='local', fs_root_folder='data'):
        self.fs_protocol = fs_protocol
        self.fs_root_folder = fs_root_folder

        # Erstelle den Root-Ordner, falls er nicht existiert
        if not os.path.exists(self.fs_root_folder):
            os.makedirs(self.fs_root_folder)

    def load_user_data(self, session_state_key, username, initial_value=None, parse_dates=None):
        """
        Lädt die nutzerspezifischen Daten aus einer Datei.
        """
        user_file = os.path.join(self.fs_root_folder, f"{username}_data.csv")
        try:
            # Versuche, die Datei zu laden
            data = pd.read_csv(user_file, parse_dates=parse_dates)
        except FileNotFoundError:
            # Initialisiere mit Standardwerten, falls die Datei nicht existiert
            data = initial_value if initial_value is not None else pd.DataFrame()
        return data

    def save_user_data(self, session_state_key, username):
        """
        Speichert die nutzerspezifischen Daten in einer Datei.
        """
        user_file = os.path.join(self.fs_root_folder, f"{username}_data.csv")
        data = st.session_state.get(session_state_key)
        if data is not None:
            # Speichere die Daten in der Datei
            data.to_csv(user_file, index=False)

    def load_app_data(self, file_name, initial_value=None, parse_dates=None):
        """
        Lädt globale App-Daten (falls benötigt).
        """
        file_path = os.path.join(self.fs_root_folder, file_name)
        try:
            data = pd.read_csv(file_path, parse_dates=parse_dates)
        except FileNotFoundError:
            data = initial_value if initial_value is not None else pd.DataFrame()
        return data

    def save_app_data(self, file_name, data):
        """
        Speichert globale App-Daten (falls benötigt).
        """
        file_path = os.path.join(self.fs_root_folder, file_name)
        data.to_csv(file_path, index=False)