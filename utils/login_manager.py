import streamlit as st
from streamlit_authenticator import Authenticate

class LoginManager:
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.authenticator = Authenticate(
            credentials=data_manager.get_credentials(),
            cookie_name="auth_cookie",
            key="auth_key",
            cookie_expiry_days=30
        )

    def login_register(self):
        """
        Hauptmethode, um zwischen Login und Registrierung zu wählen.
        """
        st.title("Login oder Registrierung")
        option = st.radio("Wählen Sie eine Option:", ["Login", "Registrieren"])

        if option == "Login":
            self.login()
        elif option == "Registrieren":
            self.register()

    def login(self):
        """
        Login-Logik mit Fehlerbehandlung.
        """
        try:
            name, authentication_status, username = self.authenticator.login("Login", "main")
            if authentication_status:
                st.success(f"Willkommen {name}!")
            elif authentication_status is False:
                st.error("Benutzername oder Passwort ist falsch.")
            elif authentication_status is None:
                st.warning("Bitte geben Sie Ihren Benutzernamen und Ihr Passwort ein.")
        except Exception as e:
            st.error("Ein Fehler ist während des Logins aufgetreten.")
            print(f"Login-Fehler: {e}")

    def register(self):
        """
        Registrierungslogik mit Fehlerbehandlung.
        """
        try:
            res = self.authenticator.register_user()
            if res:
                st.success("Registrierung erfolgreich! Sie können sich jetzt einloggen.")
            else:
                st.warning("Registrierung fehlgeschlagen. Bitte versuchen Sie es erneut.")
        except Exception as e:
            if "Captcha entered incorrectly" in str(e):
                st.error("Registrierung fehlgeschlagen. CAPTCHA wurde falsch eingegeben.")
            else:
                st.error("Ein Fehler ist während der Registrierung aufgetreten.")
            print(f"Registrierungsfehler: {e}")