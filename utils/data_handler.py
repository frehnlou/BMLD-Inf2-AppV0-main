import json
import yaml
import posixpath
import pandas as pd
from io import StringIO
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataHandler:
    def __init__(self, filesystem, root_path):
        """
        Initialisiert den DataHandler.

        Args:
            filesystem: Das Dateisystemobjekt (z. B. fsspec).
            root_path: Der Root-Pfad für alle Dateioperationen.
        """
        self.filesystem = filesystem
        self.root_path = root_path

    def join(self, *args):
        """
        Verbindet Pfade mit posixpath.

        Returns:
            str: Der verbundene Pfad.
        """
        return posixpath.join(*args)

    def _resolve_path(self, relative_path):
        """
        Löst den relativen Pfad in einen absoluten Pfad auf.

        Args:
            relative_path: Der relative Pfad.

        Returns:
            str: Der absolute Pfad.
        """
        return self.join(self.root_path, relative_path)

    def exists(self, relative_path):
        """
        Überprüft, ob eine Datei oder ein Verzeichnis existiert.

        Args:
            relative_path: Der relative Pfad.

        Returns:
            bool: True, wenn die Datei existiert, sonst False.
        """
        full_path = self._resolve_path(relative_path)
        return self.filesystem.exists(full_path)

    def read_text(self, relative_path):
        """
        Liest den Inhalt einer Textdatei.

        Args:
            relative_path: Der relative Pfad.

        Returns:
            str: Der Inhalt der Datei.
        """
        full_path = self._resolve_path(relative_path)
        with self.filesystem.open(full_path, "r") as f:
            return f.read()

    def read_binary(self, relative_path):
        """
        Liest den Inhalt einer Binärdatei.

        Args:
            relative_path: Der relative Pfad.

        Returns:
            bytes: Der Inhalt der Datei.
        """
        full_path = self._resolve_path(relative_path)
        with self.filesystem.open(full_path, "rb") as f:
            return f.read()

    def write_text(self, relative_path, content):
        """
        Schreibt Textinhalt in eine Datei.

        Args:
            relative_path: Der relative Pfad.
            content: Der zu schreibende Textinhalt.
        """
        full_path = self._resolve_path(relative_path)
        with self.filesystem.open(full_path, "w") as f:
            f.write(content)

    def write_binary(self, relative_path, content):
        """
        Schreibt Binärinhalt in eine Datei.

        Args:
            relative_path: Der relative Pfad.
            content: Der zu schreibende Binärinhalt.
        """
        full_path = self._resolve_path(relative_path)
        with self.filesystem.open(full_path, "wb") as f:
            f.write(content)

    def load(self, relative_path, initial_value=None, **load_args):
        """
        Lädt den Inhalt einer Datei basierend auf der Dateiendung.

        Args:
            relative_path: Der relative Pfad.
            initial_value: Der Standardwert, falls die Datei nicht existiert.

        Returns:
            Der geladene Inhalt der Datei.
        """
        logger.info(f"Lade Datei: {relative_path}")
        if not self.exists(relative_path):
            if initial_value is not None:
                logger.warning(f"Datei nicht gefunden: {relative_path}. Rückgabe des Standardwerts.")
                return initial_value
            raise FileNotFoundError(f"Datei existiert nicht: {relative_path}")

        ext = posixpath.splitext(relative_path)[-1].lower()
        if ext == ".json":
            return json.loads(self.read_text(relative_path))
        elif ext in [".yaml", ".yml"]:
            return yaml.safe_load(self.read_text(relative_path))
        elif ext == ".csv":
            with self.filesystem.open(self._resolve_path(relative_path), "r") as f:
                return pd.read_csv(f, **load_args)
        elif ext == ".txt":
            return self.read_text(relative_path)
        else:
            raise ValueError(f"Nicht unterstützte Dateiendung: {ext}")

    def save(self, relative_path, content):
        """
        Speichert den Inhalt in einer Datei basierend auf der Dateiendung.

        Args:
            relative_path: Der relative Pfad.
            content: Der zu speichernde Inhalt.
        """
        logger.info(f"Speichere Datei: {relative_path}")
        full_path = self._resolve_path(relative_path)
        parent_dir = posixpath.dirname(full_path)

        if not self.filesystem.exists(parent_dir):
            self.filesystem.mkdirs(parent_dir, exist_ok=True)

        ext = posixpath.splitext(relative_path)[-1].lower()

        if isinstance(content, pd.DataFrame) and ext == ".csv":
            self.write_text(relative_path, content.to_csv(index=False))
        elif isinstance(content, (dict, list)) and ext == ".json":
            self.write_text(relative_path, json.dumps(content, indent=4))
        elif isinstance(content, (dict, list)) and ext in [".yaml", ".yml"]:
            self.write_text(relative_path, yaml.dump(content, default_flow_style=False))
        elif isinstance(content, str) and ext == ".txt":
            self.write_text(relative_path, content)
        elif isinstance(content, bytes):
            self.write_binary(relative_path, content)
        else:
            raise ValueError(f"Nicht unterstützter Inhaltstyp für Dateiendung {ext}")

