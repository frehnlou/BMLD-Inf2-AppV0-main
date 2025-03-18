import secrets
import streamlit as st
import streamlit_authenticator as stauth
from utils.data_manager import DataManager


class LoginManager:
    """
    Singleton-Klasse, die den Anwendungszustand, die Speicherung und die Benutzer-Authentifizierung verwaltet.
    """
    def __new__(cls, *args, **kwargs):
        if 'login_manager' in st.session_state:
            return st.session_state.login_manager
        else:
            instance = super(LoginManager, cls).__new__(cls)
            st.session_state.login_manager = instance
            return instance
    
    def __init__(self, data_manager: DataManager = None,
                 auth_credentials_file: str = 'credentials.yaml',
                 auth_cookie_name: str = 'bmld_inf2_streamlit_app'):
        if hasattr(self, 'authenticator'):
            return
        
        if data_manager is None:
            return

        self.data_manager = data_manager
        self.auth_credentials_file = auth_credentials_file
        self.auth_cookie_name = auth_cookie_name
        self.auth_cookie_key = secrets.token_urlsafe(32)
        self.auth_credentials = self._load_auth_credentials()
        self.authenticator = stauth.Authenticate(self.auth_credentials, self.auth_cookie_name, self.auth_cookie_key)

    def _load_auth_credentials(self):
        dh = self.data_manager._get_data_handler()
        return dh.load(self.auth_credentials_file, initial_value={"usernames": {}})

    def _save_auth_credentials(self):
        dh = self.data_manager._get_data_handler()
        dh.save(self.auth_credentials_file, self.auth_credentials)

    def login_register(self, login_title='Anmelden', register_title='Registrieren'):
        if st.session_state.get("authentication_status") is True:
            self.authenticator.logout()
        else:
            login_tab, register_tab = st.tabs((login_title, register_title))
            with login_tab:
                self.login(stop=False)
            with register_tab:
                self.register()

    def login(self, stop=True):
        if st.session_state.get("authentication_status") is True:
            self.authenticator.logout()
        else:
            username = st.text_input("Benutzername", key="login_username")
            password = st.text_input("Passwort", type="password", key="login_password")
            login_button = st.button("Anmelden", key="login_button")

            if login_button:
                user_data = self.auth_credentials["usernames"].get(username)
                if user_data and user_data["password"] == password:
                    st.session_state["username"] = username
                    st.session_state["authentication_status"] = True
                    st.success(f"Willkommen, {username}!")
                else:
                    st.error("Benutzername oder Passwort ist falsch.")
            if stop:
                st.stop()

    def register(self, stop=True):
        if st.session_state.get("authentication_status") is True:
            self.authenticator.logout()
        else:
            st.info("""
            Das Passwort muss 8-20 Zeichen lang sein und mindestens einen Großbuchstaben, 
            einen Kleinbuchstaben, eine Ziffer und ein Sonderzeichen aus @$!%*?& enthalten.
            """)

            # Registrierungsformular in einer Tabelle
            st.markdown("### Benutzer registrieren")
            st.markdown(
                """
                <style>
                table {
                    width: 100%;
                    border-collapse: collapse;
                }
                td {
                    padding: 10px;
                    vertical-align: top;
                }
                </style>
                """,
                unsafe_allow_html=True,
            )

            # Tabelle für das Formular
            st.markdown(
                """
                <table>
                    <tr>
                        <td><label for="first_name">Vorname:</label></td>
                        <td><input type="text" id="first_name" name="first_name" style="width: 100%;"></td>
                    </tr>
                    <tr>
                        <td><label for="last_name">Nachname:</label></td>
                        <td><input type="text" id="last_name" name="last_name" style="width: 100%;"></td>
                    </tr>
                    <tr>
                        <td><label for="email">E-Mail:</label></td>
                        <td><input type="email" id="email" name="email" style="width: 100%;"></td>
                    </tr>
                    <tr>
                        <td><label for="username">Benutzername:</label></td>
                        <td><input type="text" id="username" name="username" style="width: 100%;"></td>
                    </tr>
                    <tr>
                        <td><label for="password">Passwort:</label></td>
                        <td><input type="password" id="password" name="password" style="width: 100%;"></td>
                    </tr>
                    <tr>
                        <td><label for="repeat_password">Passwort wiederholen:</label></td>
                        <td><input type="password" id="repeat_password" name="repeat_password" style="width: 100%;"></td>
                    </tr>
                    <tr>
                        <td><label for="password_hint">Passworthinweis:</label></td>
                        <td><input type="text" id="password_hint" name="password_hint" style="width: 100%;"></td>
                    </tr>
                    <tr>
                        <td><label for="captcha">Captcha (Bitte '1234' eingeben):</label></td>
                        <td><input type="text" id="captcha" name="captcha" style="width: 100%;"></td>
                    </tr>
                </table>
                """,
                unsafe_allow_html=True,
            )

            register_button = st.button("Registrieren", key="register_button")

            if register_button:
                # Überprüfen, ob das Captcha korrekt ist
                captcha = st.session_state.get("captcha", "")
                if captcha != "1234":
                    st.error("Captcha ist falsch. Bitte versuchen Sie es erneut.")
                    return

                # Überprüfen, ob die Passwörter übereinstimmen
                password = st.session_state.get("password", "")
                repeat_password = st.session_state.get("repeat_password", "")
                if password != repeat_password:
                    st.error("Die Passwörter stimmen nicht überein.")
                    return

                # Überprüfen, ob der Benutzername bereits existiert
                username = st.session_state.get("username", "")
                if username in self.auth_credentials["usernames"]:
                    st.error("Benutzername existiert bereits. Bitte wählen Sie einen anderen.")
                    return

                # Benutzer hinzufügen
                self.auth_credentials["usernames"][username] = {
                    "first_name": st.session_state.get("first_name", ""),
                    "last_name": st.session_state.get("last_name", ""),
                    "email": st.session_state.get("email", ""),
                    "password": password,  # Optional: Passwort-Hashing hinzufügen
                    "password_hint": st.session_state.get("password_hint", "")
                }

                try:
                    self._save_auth_credentials()
                    st.success(f"Benutzer {username} erfolgreich registriert.")
                except Exception as e:
                    st.error(f"Fehler beim Speichern der Anmeldedaten: {e}")

                if stop:
                    st.stop()

    def go_to_login(self, login_page_py_file):
        if st.session_state.get("authentication_status") is not True:
            st.switch_page(login_page_py_file)
        else:
            self.authenticator.logout()