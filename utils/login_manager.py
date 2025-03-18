def login(self, stop=True):
    """
    Rendert das Login-Formular und verarbeitet Authentifizierungsstatusmeldungen.
    """
    if st.session_state.get("authentication_status") is True:
        # Benutzer ist bereits eingeloggt, Logout-Button anzeigen
        self.authenticator.logout("Logout", "sidebar")
    else:
        try:
            # Login-Formular anzeigen
            name, authentication_status, username = self.authenticator.login("Login", location="sidebar")
            
            # Verarbeite den Authentifizierungsstatus
            if authentication_status:
                st.success(f"Willkommen {name}!")
            elif authentication_status is False:
                st.error("Benutzername oder Passwort ist falsch.")
            elif authentication_status is None:
                st.warning("Bitte geben Sie Ihren Benutzernamen und Ihr Passwort ein.")
        except Exception as e:
            # Fehlerbehandlung
            st.error(f"Fehler bei der Anmeldung: {e}")
        
        # Stoppe die Ausführung, falls `stop=True`
        if stop:
            st.stop()