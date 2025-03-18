import fsspec, posixpath
import streamlit as st
import pandas as pd
from utils.data_handler import DataHandler

class DataManager:
    """
    A singleton class for managing application data persistence and user-specific storage.
    
    This class provides a centralized interface for handling both application-wide and
    user-specific data storage operations.
    
    Key Features:
        - Singleton implementation for consistent state management
        - Flexible filesystem support (local and WebDAV)
        - Separate handling of application and user-specific data
        - Integration with Streamlit's session state
        - Automatic data persistence
    
    Attributes:
        fs (fsspec.AbstractFileSystem): The filesystem interface for data storage
        fs_root_folder (str): Root directory for all file operations
        app_data_reg (dict): Registry of application-wide data files
        user_data_reg (dict): Registry of user-specific data files
    """

    def __new__(cls, *args, **kwargs):
        """ Singleton implementation using Streamlit session state. """
        if 'data_manager' in st.session_state:
            return st.session_state.data_manager
        else:
            instance = super(DataManager, cls).__new__(cls)
            st.session_state.data_manager = instance
            return instance
    
    def __init__(self, fs_protocol='file', fs_root_folder='app_data'):
        """ Initialize filesystem and storage configuration. """
        if hasattr(self, 'fs'):
            return  # Skip initialization if already set
            
        self.fs_root_folder = fs_root_folder
        self.fs = self._init_filesystem(fs_protocol)
        self.app_data_reg = {}
        self.user_data_reg = {}

    @staticmethod
    def _init_filesystem(protocol: str):
        """
        Creates and configures an fsspec filesystem instance.
        
        Args:
            protocol: 'webdav' or 'file'
            
        Returns:
            fsspec.AbstractFileSystem instance
            
        Raises:
            ValueError: If protocol is invalid
        """
        if protocol == 'webdav':
            secrets = st.secrets['webdav']
            return fsspec.filesystem('webdav', 
                                     base_url=secrets['base_url'], 
                                     auth=(secrets['username'], secrets['password']))
        elif protocol == 'file':
            return fsspec.filesystem('file')
        else:
            raise ValueError(f"DataManager: Invalid filesystem protocol: {protocol}")

    def _get_data_handler(self, subfolder: str = None):
        """ Returns a DataHandler instance for the given folder. """
        path = self.fs_root_folder if subfolder is None else posixpath.join(self.fs_root_folder, subfolder)
        return DataHandler(self.fs, path)

    def load_app_data(self, session_state_key, file_name, initial_value=None, **load_args):
        """
        Loads application-wide data into Streamlit session state.

        Args:
            session_state_key (str): Session state key
            file_name (str): File to load data from
            initial_value: Default value if file doesn't exist
        """
        if session_state_key in st.session_state:
            return
        
        dh = self._get_data_handler()
        data = dh.load(file_name, initial_value, **load_args)
        st.session_state[session_state_key] = data
        self.app_data_reg[session_state_key] = file_name

    def load_user_data(self, session_state_key, file_name, initial_value=None, **load_args):
        """
        Loads user-specific data into Streamlit session state.

        Args:
            session_state_key (str): Session state key
            file_name (str): User-specific data file
            initial_value: Default value if file doesn't exist
        """
        username = st.session_state.get('username', None)
        if username is None:
            self._clear_user_data()
            st.error(f"DataManager: No user logged in, cannot load `{file_name}`")
            return

        if session_state_key in st.session_state:
            return

        user_folder = f'user_data_{username}'
        dh = self._get_data_handler(user_folder)
        data = dh.load(file_name, initial_value, **load_args)
        st.session_state[session_state_key] = data
        self.user_data_reg[session_state_key] = dh.join(user_folder, file_name)

    def _clear_user_data(self):
        """ Clears all user-specific session data when logging out. """
        for key in self.user_data_reg:
            st.session_state.pop(key, None)
        self.user_data_reg = {}

    @property
    def data_reg(self):
        """ Returns the combined app and user data registry. """
        return {**self.app_data_reg, **self.user_data_reg}

    def save_data(self, session_state_key):
        """
        Saves data from session state to persistent storage.

        Args:
            session_state_key (str): Key identifying the data
        """
        if session_state_key not in self.data_reg:
            raise ValueError(f"DataManager: No registered data for `{session_state_key}`")

        if session_state_key not in st.session_state:
            raise ValueError(f"DataManager: `{session_state_key}` not found in session state")

        dh = self._get_data_handler()
        dh.save(self.data_reg[session_state_key], st.session_state[session_state_key])

    def save_all_data(self):
        """ Saves all user and app data from session state to storage. """
        for key in self.data_reg.keys():
            if key in st.session_state:
                self.save_data(key)

    def append_record(self, session_state_key, record_dict):
        """
        Appends a record to session state data.

        Args:
            session_state_key (str): Key in session state
            record_dict (dict): Data to append
        """
        if not isinstance(record_dict, dict):
            raise ValueError("DataManager: `record_dict` must be a dictionary")

        if session_state_key not in st.session_state:
            raise ValueError(f"DataManager: `{session_state_key}` not found in session state")

        data_value = st.session_state[session_state_key]

        if isinstance(data_value, pd.DataFrame):
            data_value = pd.concat([data_value, pd.DataFrame([record_dict])], ignore_index=True)
        elif isinstance(data_value, list):
            data_value.append(record_dict)
        else:
            raise ValueError(f"DataManager: `{session_state_key}` must be a DataFrame or list")

        st.session_state[session_state_key] = data_value
        self.save_data(session_state_key)
