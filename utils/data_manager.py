import fsspec
import posixpath
import streamlit as st
import pandas as pd
from utils.data_handler import DataHandler

class DataManager:
    def __new__(cls, *args, **kwargs):
        if 'data_manager' in st.session_state:
            return st.session_state.data_manager
        else:
            instance = super(DataManager, cls).__new__(cls)
            st.session_state.data_manager = instance
            return instance

    def __init__(self, fs_protocol='file', fs_root_folder='app_data'):
        if hasattr(self, 'fs'):
            return

        self.fs_root_folder = fs_root_folder
        self.fs = self._init_filesystem(fs_protocol=fs_protocol)
        self.app_data_reg = {}
        self.user_data_reg = {}

    @staticmethod
    def _init_filesystem(fs_protocol):
        if fs_protocol == 'webdav':
            secrets = st.secrets['webdav']
            return fsspec.filesystem('webdav', 
                                     base_url=secrets['base_url'], 
                                     auth=(secrets['username'], secrets['password']))
        elif fs_protocol == 'file':
            return fsspec.filesystem('file')
        else:
            raise ValueError(f"Ungültiges Dateisystemprotokoll: {fs_protocol}")

    def _get_data_handler(self, subfolder=None):
        if subfolder is None:
            return DataHandler(self.fs, self.fs_root_folder)
        else:
            folder_path = posixpath.join(self.fs_root_folder, subfolder)
            if not self.fs.exists(folder_path):
                self.fs.mkdir(folder_path)
            return DataHandler(self.fs, folder_path)

    def load_user_data(self, session_state_key, file_name, initial_value=pd.DataFrame(), **load_args):
        username = st.session_state.get('username', None)
        if username is None:
            raise ValueError("❌ Kein Benutzer angemeldet!")

        user_folder = f"user_data_{username}"
        dh = self._get_data_handler(subfolder=user_folder)

        if not dh.exists(file_name):
            dh.save(file_name, initial_value)

        data = dh.load(file_name, initial_value, **load_args)

        user_data_path = posixpath.join(user_folder, file_name)
        st.session_state[session_state_key] = data
        self.user_data_reg[session_state_key] = user_data_path  

        return data

    def save_user_data(self, session_state_key, file_name, data):
        username = st.session_state.get('username', None)
        if username is None:
            raise ValueError("❌ Kein Benutzer angemeldet!")

        user_folder = f"user_data_{username}"
        dh = self._get_data_handler(subfolder=user_folder)
        dh.save(file_name, data)

    def append_record(self, file_name, record_dict):
        username = st.session_state.get('username', None)
        if username is None:
            raise ValueError("❌ Kein Benutzer angemeldet!")

        user_folder = f'user_data_{username}'
        dh = self._get_data_handler(subfolder=user_data_folder)

        if not dh.exists(file_name):
            dh.save(file_name, pd.DataFrame([record_dict]))
        else:
            data = dh.load(file_name)
            data = pd.concat([data, pd.DataFrame([record_dict])], ignore_index=True)
            dh.save(file_name, data)