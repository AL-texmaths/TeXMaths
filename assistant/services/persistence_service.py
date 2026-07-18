import subprocess
from assistant.utils.resolve import USR_CONFIG_PATH, DEF_CONFIG_PATH, resolve_executable
from assistant.models.config import Config
from pathlib import Path
import json

class PersistenceService:

    @staticmethod
    def load_config(usr: bool = True) -> Config:
        if usr:
            with open(USR_CONFIG_PATH, encoding="utf8") as f:
                config = Config.model_validate(json.load(f))
        else:
            with open(DEF_CONFIG_PATH, encoding="utf8") as f:
                config = Config.model_validate(json.load(f))
        return config

    @staticmethod
    def save_config(config: Config) -> None:
        with open(USR_CONFIG_PATH, "w", encoding="utf8") as f:
            json.dump(
                config.model_dump(by_alias=True),
                f,
                indent=4,
                ensure_ascii=False,
            )
    
    def restore_default_settings(self) -> None:
        default_config = self.load_config(usr=False)
        self.save_config(default_config)

    def open_config_file(self):
        subprocess.run(
            [
                str(resolve_executable("blocnote", self.load_config())),
                str(USR_CONFIG_PATH)
            ],
            check=False
            )

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
