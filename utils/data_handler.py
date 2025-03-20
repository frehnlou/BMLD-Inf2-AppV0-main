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
        """ Verbindet Pfade mit posixpath. """
        return posixpath.join(*args)

    def _resolve_path(self, relative_path):
        """ Löst den relativen Pfad in einen absoluten Pfad auf. """
        return self.join(self.root_path, relative_path)

    def exists(self, relative_path):
        """ Überprüft, ob eine Datei oder ein Verzeichnis existiert. """
        full_path = self._resolve_path(relative_path)
        return self.filesystem.exists(full_path)

    def read_text(self, relative_path):
        """ Liest den Inhalt einer Textdatei. """
        full_path = self._resolve_path(relative_path)
        with self.filesystem.open(full_path, "r") as f:
            return f.read()

    def read_binary(self, relative_path):
        """ Liest den Inhalt einer Binärdatei. """
        full_path = self._resolve_path(relative_path)
        with self.filesystem.open(full_path, "rb") as f:
            return f.read()

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
                df = pd.read_csv(f, **load_args)
                
                # Debugging: Zeigt die Spalten der geladenen Datei
                print(f"Geladene Spalten in {relative_path}: {df.columns.tolist()}")

                if df.empty:
                    raise ValueError(f"Die Datei {relative_path} ist leer!")

                # Prüft, ob 'timestamp' existiert
                if 'timestamp' not in df.columns:
                    alternative_date_columns = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
                    if alternative_date_columns:
                        # Nimmt die erste gefundene alternative Datums-Spalte
                        df[alternative_date_columns[0]] = pd.to_datetime(df[alternative_date_columns[0]])
                        print(f"⚠️ 'timestamp' nicht gefunden. Verwende stattdessen '{alternative_date_columns[0]}' als Datums-Spalte.")
                    else:
                        print("❌ 'timestamp' oder eine alternative Datumsspalte konnte nicht gefunden werden!")
                
                return df
        elif ext == ".txt":
            return self.read_text(relative_path)
        else:
            raise ValueError(f"Nicht unterstützte Dateiendung: {ext}")
