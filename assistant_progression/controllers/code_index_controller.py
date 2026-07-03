
from assistant_progression.utils.textools import update_code_index
from assistant_progression.models.config import Config
from assistant_progression.models.paths import Paths
from assistant_progression.services.catalogue_service import CatalogueService
from assistant_progression.controllers.code_index_document_controller import CodeIndexDocumentController

class CodeIndexController:
    def __init__(
            self,
            paths:Paths,
            config:Config,
            catalogue_service:CatalogueService,
            code_index_document_controller: CodeIndexDocumentController
            ):
        self.paths = paths
        self.config = config
        self.catalogue_service = catalogue_service
        self.code_index_document_controller = code_index_document_controller
        self.code_index_data = self.catalogue_service.code_index_data

    def refresh_code_index(self) -> int:
        result = update_code_index(
            self.paths.code_labels,
            self.paths.code_index,
            self.paths.texmf,
            self.config
        )
        code_index_data = self.code_index_document_controller.load_data()
        self.catalogue_service.code_index_data = code_index_data
        self.catalogue_service.refresh()
        return result