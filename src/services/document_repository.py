import json
from pathlib import Path
class DocumentRepository:

    def __init__(self, data_index_path: str | Path):
        """
        Classe représentant un dépôt de documents.
        """
        self.path = Path(data_index_path)
    
    def load(self):
        """"""
        with open(self.path, "r") as f:
            return json.load(f)

    def save(self):
        """"""
        data = self.load()
        with open(self.path, "w") as f:
            json.dump(data, f)

    def get_doc_by_key(self, key: str) -> dict:
        """"""
        return self.load().get(key, {})

    def get_all_document(self):
        """"""