import sys
import json
from pathlib import Path
from src.app.resolve import resolve_executable, resolve_paths

def base_dir():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent.parent
    return Path(__file__).resolve().parent.parent.parent

CONFIG_PATH = base_dir() / "config.json"


class ConfigManager:

    def __init__(self):
        self.config_path = CONFIG_PATH
        self.current_config = self.load()

    def load(self):
        """"""
        config_path = self.config_path
        if not config_path.exists():
            raise FileNotFoundError(f"Config introuvable : {config_path}")

        # print(f"Chargement de la config depuis : {config_path}")
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        return config

    def save(self):
        """"""
        config_path = self.config_path
        # print(f"Enregistrement de la config dans : {config_path}")
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(self.current_config, f, indent=4, ensure_ascii=False)
    
    def get(self, *keys: str):
        """"""
        config = self.load()
        loaded_keys = []
        for key in keys:
            config = config.get(key, {})
            loaded_keys.append(key)
            if not config:
                print(f"Clés introuvables dans la config : {loaded_keys}")
                break
        return config

    def set(self, *keys: str, value):
        """"""
        self.current_config = self.load()
        current = self.current_config
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[keys[-1]] = value
        self.save()
    
    def get_path_by_key(self, key: str):
        """"""
        candidates = self.get("paths", key)
        if not candidates:
            print(f"WARNING: Clé introuvable dans la config : paths.{key}")
            return None
        return resolve_paths(*candidates)

    def get_exe_by_key(self, key: str):
        """"""
        candidates = [key]
        candidates = candidates + self.get("executables", key)
        if not candidates:
            print(f"WARNING: Clé introuvable dans la config : executables.{key}")
            return None
        return resolve_executable(key)