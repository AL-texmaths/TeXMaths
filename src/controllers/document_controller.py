from pathlib import Path

from src.app.context import AppContext


class DocumentController:

    def __init__(self, context: AppContext):
        self._context = context

    def is_subkey_valide(self, document: dict, subkey: str) -> bool:
        return document is not None and subkey in document

    def get_document_dict(self, key: str) -> dict:
        return self._context.repository.get_doc_by_key(key)

    def get_enonce(self, key: str) -> str:

        document = self.get_document_dict(key)

        return document.get("enonce", "")
    
    def get_preview_path(self, key: str) -> Path:
        
        document = self.get_document_dict(key)

        return Path(document.get("preview", ""))
    

    def get_tex_path(self, key:str) -> Path:
        
        document = self.get_document_dict(key)

        return Path(document.get("tex", ""))
    
    def get_pdf_path(self, key:str, preview=True) -> Path:

        document = self.get_document_dict(key)

        if preview and self.is_subkey_valide(document, "preview"):
            return self.get_preview_path(key)
    
        return Path(document.get("pdf", ""))
        
                