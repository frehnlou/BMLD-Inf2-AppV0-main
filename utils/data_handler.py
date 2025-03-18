import json
import yaml
import posixpath
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)  # Korrektur hier

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
        """ Verbindet Pfade mit posixpath. """
        return posixpath.join(*args)

    def _resolve_path(self, relative_path):
        """ Löst den relativen Pfad in einen absoluten Pfad auf. """
        return self.join(self.root_path, relative_path)

    def exists(self, relative_path):
        """ Überprüft, ob eine Datei oder ein Verzeichnis existiert. """
        full_path = self._resolve_path(relative_path)
        return self.filesystem.exists(full_path)

    def save(self, relative_path, content):
        """
        Speichert den Inhalt in einer Datei basierend auf der Dateiendung.

        Args:
            relative_path: Der relative Pfad.
            content: Der zu speichernde Inhalt.
        """
        full_path = self._resolve_path(relative_path)
        parent_dir = posixpath.dirname(full_path)

        if not self.filesystem.exists(parent_dir):
            try:
                self.filesystem.mkdirs(parent_dir, exist_ok=True)
            except Exception as e:
                logger.error(f"❌ Fehler beim Erstellen des Ordners {parent_dir}: {e}")

        ext = posixpath.splitext(relative_path)[-1].lower()

        try:
            if isinstance(content, pd.DataFrame) and ext == ".csv":
                with self.filesystem.open(full_path, "w") as f:
                    content.to_csv(f, index=False)
            elif isinstance(content, (dict, list)) and ext == ".json":
                with self.filesystem.open(full_path, "w") as f:
                    json.dump(content, f, indent=4)
            elif isinstance(content, (dict, list)) and ext in [".yaml", ".yml"]:
                with self.filesystem.open(full_path, "w") as f:
                    yaml.dump(content, f, default_flow_style=False)
            elif isinstance(content, str) and ext == ".txt":
                with self.filesystem.open(full_path, "w") as f:
                    f.write(content)
            elif isinstance(content, bytes):
                with self.filesystem.open(full_path, "wb") as f:
                    f.write(content)
            else:
                raise ValueError(f"Nicht unterstützter Inhaltstyp für Dateiendung {ext}")
        except Exception as e:
            logger.error(f"❌ Fehler beim Speichern von {relative_path}: {e}")

    def load(self, relative_path, initial_value=None):
        """
        Lädt den Inhalt einer Datei basierend auf der Dateiendung.

        Args:
            relative_path: Der relative Pfad.
            initial_value: Der Standardwert, falls die Datei nicht existiert.

        Returns:
            Der geladene Inhalt oder der Standardwert.
        """
        full_path = self._resolve_path(relative_path)

        if not self.filesystem.exists(full_path):
            return initial_value

        ext = posixpath.splitext(relative_path)[-1].lower()

        try:
            if ext == ".csv":
                with self.filesystem.open(full_path, "r") as f:
                    return pd.read_csv(f)
            elif ext == ".json":
                with self.filesystem.open(full_path, "r") as f:
                    return json.load(f)
            elif ext in [".yaml", ".yml"]:
                with self.filesystem.open(full_path, "r") as f:
                    return yaml.safe_load(f)
            elif ext == ".txt":
                with self.filesystem.open(full_path, "r") as f:
                    return f.read()
            else:
                raise ValueError(f"Nicht unterstützter Inhaltstyp für Dateiendung {ext}")
        except Exception as e:
            logger.error(f"❌ Fehler beim Laden von {relative_path}: {e}")
            return initial_value