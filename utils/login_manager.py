def register(self, stop=True):
    """
    Zeigt das Registrierungsformular an und ersetzt englische Labels durch Deutsch.
    """
    if st.session_state.get("authentication_status") is True:
        self.authenticator.logout()
    else:
        st.info("""
        🔒 **Passwortanforderungen:**  
        - **8-20 Zeichen lang**  
        - Mindestens **1 Großbuchstabe**  
        - Mindestens **1 Kleinbuchstabe**  
        - Mindestens **1 Zahl**  
        - Mindestens **1 Sonderzeichen** (@$!%*?&)  
        """)

        # Standard `register_user()` ausführen
        res = self.authenticator.register_user()

        if res and res[1] is not None:
            st.success(f"✅ Benutzer {res[1]} wurde erfolgreich registriert!")
            try:
                self._save_auth_credentials()
                st.success("✅ Zugangsdaten wurden gespeichert.")
            except Exception as e:
                st.error(f"⚠️ Fehler beim Speichern der Zugangsdaten: {e}")

        # 🔥 Endgültiger Fix: Ändert die Labels per JavaScript direkt im Browser
        st.markdown(
            """
            <script>
            setTimeout(() => {
                let labels = {
                    "Register user": "Benutzer registrieren",
                    "First name": "Vorname",
                    "Last name": "Nachname",
                    "Email": "E-Mail",
                    "Username": "Benutzername",
                    "Password": "Passwort",
                    "Repeat password": "Passwort wiederholen",
                    "Password hint": "Passworthinweis",
                    "Captcha": "Sicherheitscode"
                };

                document.querySelectorAll("label").forEach(label => {
                    let text = label.innerText.trim();
                    if (labels[text]) {
                        label.innerText = labels[text];
                    }
                });

                document.querySelectorAll("button").forEach(button => {
                    if (button.innerText.trim() === "Register") {
                        button.innerText = "Registrieren";
                    }
                });
            }, 1500);  // Warten, damit Streamlit das Formular vollständig lädt
            </script>
            """,
            unsafe_allow_html=True
        )

        if stop:
            st.stop()
