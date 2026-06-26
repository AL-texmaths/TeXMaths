from pathlib import Path
import json


class PersistenceService:

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