import secrets
import streamlit as st
import streamlit_authenticator as stauth
from utils.data_manager import DataManager


class LoginManager:
    """
    Singleton-Klasse für die Verwaltung von Anwendungszustand, Speicherung und Benutzer-Authentifizierung.
    """
    
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

    file_name = f"{username}_data.csv"  # 🔥 Benutzer bekommt eigene Datei!
    dh = self._get_data_handler()

    # Prüfe, ob die Datei existiert
    try:
        if not self.fs.exists(file_name):
            st.warning(f"📂 Datei für {username} nicht gefunden. Erstelle neue Datei...")
            df = initial_value if initial_value is not None else pd.DataFrame(columns=["datum_zeit", "blutzuckerwert", "zeitpunkt"])
            dh.save(file_name, df)  # ✅ Datei sofort speichern!
            st.toast(f"📁 Neue Datei für {username} wurde erstellt.", icon="💾")
            return df
    except Exception as e:
        st.error(f"⚠️ WebDAV-Verbindungsfehler beim Überprüfen der Datei: {e}")
        return pd.DataFrame()

    # Lade die Datei
    try:
        df = dh.load(file_name, initial_value=initial_value)
    except Exception as e:
        st.error(f"⚠️ Fehler beim Laden der Datei {file_name}: {e}")
        return pd.DataFrame()

    # Falls `parse_dates` definiert ist, konvertiere Spalten zu Datetime
    if parse_dates is not None:
        for col in parse_dates:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')

    return df

