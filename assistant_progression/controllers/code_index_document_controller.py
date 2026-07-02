import json
from pathlib import Path

class CodeIndexDocumentController:

    def __init__(self, document_path: str|Path=None):
        self.document_path = Path(document_path) if document_path else None

    def load_data(self):
        if self.document_path is None:
            return {}
        else:
            with open(self.document_path, 'r', encoding='utf-8') as f:
                return json.load(f)