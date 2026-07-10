import json
from pathlib import Path
class DocumentRepository:

    def __init__(self, data_index_path: str | Path):
        """
        Classe représentant un dépôt de documents.
        """
        self.path = Path(data_index_path)
        self.load()

    def load(self):
        """"""
        with open(self.path, "r", encoding="utf-8") as f:
            self.data = json.load(f)

    def save(self):
        """"""
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f)

    def get_doc_by_key(self, key: str) -> dict:
        """"""
        document = self.data.get(key, {})
        return document

    def get_types(self) -> list[str]:
        """"""
        prefixes = set()
        for key in self.data.keys():
            prefix = key.split()[0]
            prefixes.add(prefix)
        return sorted(prefixes)

    def get_fields(self) -> list[str]:
        """"""
        fields = set()
        for document in self.data.values():
            fields.update(document.keys())
        return sorted(fields)
