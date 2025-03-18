import streamlit as st
import posixpath
import pandas as pd
from utils.data_handler import DataHandler

def save_user_data(self, session_state_key, username):
    """
    Speichert die Benutzerdaten in eine benutzerspezifische Datei.
    
    Args:
        session_state_key (str): Der Key im Streamlit Session-State für die Daten.
        username (str): Der Benutzername für die individuelle Datei.
    """
    if not username:
        st.warning("⚠️ Kein Benutzername gefunden! Anmeldung erforderlich.")
        return

    file_name = posixpath.join(self.fs_root_folder, f"{username}_data.csv")

    if session_state_key not in st.session_state:
        st.warning("⚠️ Keine Daten zum Speichern gefunden.")
        return

    df = st.session_state[session_state_key]

    # ✅ Datenhandler erstellen und Datei speichern
    dh = DataHandler(self.fs, self.fs_root_folder)

    try:
        dh.save(file_name, df)
        st.success(f"✅ Daten für {username} erfolgreich gespeichert!")
    except Exception as e:
        st.error(f"⚠️ Fehler beim Speichern der Datei: {e}")
