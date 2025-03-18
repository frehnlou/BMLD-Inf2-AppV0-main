import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd
from utils.data_manager import DataManager
from utils.login_manager import LoginManager

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

        # ✅ Fehlerbehandlung hinzufügen
        try:
            dh.save(file_name, df)
            st.success(f"✅ Daten für {username} erfolgreich gespeichert!")
        except Exception as e:
            st.error(f"⚠️ Fehler beim Speichern der Datei: {e}")
