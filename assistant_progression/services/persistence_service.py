from assistant_progression.utils.resolve import CONFIG_PATH
from pathlib import Path
import json


class PersistenceService:

    @staticmethod
    def load_config():
        with open(CONFIG_PATH, encoding="utf8") as f:
            return json.load(f)

    @staticmethod
    def load_progression(filename):

        filename = Path(filename)

        if not filename.exists():
            return None

        with filename.open(
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    @staticmethod
    def save_progression(
        filename,
        progression
    ):

        filename = Path(filename)

        with filename.open(
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                progression,
                f,
                ensure_ascii=False,
                indent=2
            )
        
    def save_config_value(self, *keys, value):
        """
        Modifie une valeur dans config.json.

        Exemple :
            save_config_value(
                "settings",
                "current",
                "theme",
                value="Nord Dark"
            )
        """

        with open(CONFIG_PATH, encoding="utf8") as f:
            config = json.load(f)

        node = config

        for key in keys[:-1]:
            node = node.setdefault(key, {})

        node[keys[-1]] = value

        with open(CONFIG_PATH, "w", encoding="utf8") as f:
            json.dump(
                config,
                f,
                indent=4,
                ensure_ascii=False
            )