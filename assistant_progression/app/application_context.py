# application_context.py
from dataclasses import dataclass
from assistant_progression.services.persistence_service import PersistenceService
from assistant_progression.models.config import Config
from assistant_progression.models.paths import Paths
from assistant_progression.controllers.code_index_document_controller import CodeIndexDocumentController
from assistant_progression.services.code_service import CodeService
from assistant_progression.controllers.progression_document_controller import ProgressionDocumentController
from assistant_progression.services.theme_service import ThemeService
from assistant_progression.services.undo_redo_service import UndoRedoService
from assistant_progression.services.catalogue_service import CatalogueService
from assistant_progression.services.export_service import ExportService
from assistant_progression.services.progression_analysis_service import ProgressionAnalysisService
from assistant_progression.services.progression_service import ProgressionService
from assistant_progression.services.search_service import SearchService
from assistant_progression.controllers.progression_controller import ProgressionController


@dataclass
class AppContext:
    persistence_service: PersistenceService
    config: Config
    paths: Paths
    export_service: ExportService
    undo_redo_service: UndoRedoService
    progression_analysis_service: ProgressionAnalysisService
    progression_service: ProgressionService
    progression_controller: ProgressionController
    code_index_document_controller: CodeIndexDocumentController
    code_index_data: dict
    code_service: CodeService
    catalogue_service: CatalogueService
    search_service: SearchService
    theme_service: ThemeService
    document_controller: ProgressionDocumentController

def create_context() -> AppContext:

    persistence_service = PersistenceService()
    config = persistence_service.load_config()
    paths = Paths(config)
    export_service = ExportService()
    undo_redo_service = UndoRedoService()

    code_index_document_controller = CodeIndexDocumentController(paths.code_index_file)
    code_index_data = code_index_document_controller.load_data()
    code_service = CodeService(config.codes)
    catalogue_service = CatalogueService(code_index_data, config.catalogues)
    progression_analysis_service = ProgressionAnalysisService(catalogue_service)
    progression_service = ProgressionService(
        code_service,
        catalogue_service,
        progression_analysis_service,
        config
        )
    search_service = SearchService(code_service, catalogue_service)
    progression_controller = ProgressionController(
        progression_service,
        undo_redo_service,
    )
    document_controller = ProgressionDocumentController(
        progression_service=progression_service,
            persistence_service=persistence_service,
            export_service=export_service,
            undo_redo_service=undo_redo_service,
            code_service=code_service,
            paths=paths,
    )
    theme_name = config.settings.current.theme
    theme_service = ThemeService(
        themes=config.settings.themes,
        default_theme=theme_name
        )

    return AppContext(
        persistence_service=persistence_service,
        config=config,
        paths=paths,
        code_index_document_controller=code_index_document_controller,
        code_index_data=code_index_data,
        code_service=code_service,
        catalogue_service=catalogue_service,
        search_service=search_service,
        progression_analysis_service=progression_analysis_service,
        progression_service=progression_service,
        progression_controller=progression_controller,
        theme_service=theme_service,
        export_service=export_service,
        undo_redo_service=undo_redo_service,
        document_controller=document_controller
    )