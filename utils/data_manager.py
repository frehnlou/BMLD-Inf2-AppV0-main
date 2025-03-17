def load_user_data(self, session_state_key, file_name, initial_value=pd.DataFrame(), **load_args):
    """
    Lädt benutzerspezifische Daten aus einer Datei im Benutzerordner.
    Falls die Datei nicht existiert oder leer ist, wird sie mit initialen Werten erstellt.
    """
    username = st.session_state.get('username', None)
    if username is None:
        raise ValueError("❌ Kein Benutzer angemeldet!")

    user_folder = f"user_data_{username}"
    dh = self._get_data_handler(subfolder=user_folder)

    # Falls Datei nicht existiert → Erstelle mit Spaltennamen
    if not dh.exists(file_name):
        st.warning(f"📁 Datei '{file_name}' für {username} nicht gefunden – erstelle eine neue.")
        initial_value = pd.DataFrame(columns=["datum_zeit", "blutzuckerwert", "zeitpunkt"])  # 🔥 Wichtige Spalten setzen
        dh.save(file_name, initial_value)

    try:
        data = dh.load(file_name, **load_args)

        # Falls Datei leer ist → Ersetze mit Spaltennamen
        if data.empty:
            st.warning(f"📂 Datei '{file_name}' ist leer – fülle Standardwerte ein.")
            data = pd.DataFrame(columns=["datum_zeit", "blutzuckerwert", "zeitpunkt"])
            dh.save(file_name, data)

    except pd.errors.EmptyDataError:
        st.error(f"❌ Fehler: Datei '{file_name}' für {username} ist leer oder beschädigt.")
        data = pd.DataFrame(columns=["datum_zeit", "blutzuckerwert", "zeitpunkt"])
        dh.save(file_name, data)

    # Speichern im Session State
    st.session_state[session_state_key] = data
    self.user_data_reg[session_state_key] = posixpath.join(user_folder, file_name)

    return data
