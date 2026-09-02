# application_context.py
from dataclasses import dataclass
from assistant.services.persistence_service import PersistenceService
from assistant.models.config import Config
from assistant.models.paths import Paths
from assistant.controllers.code_index_document_controller import CodeIndexDocumentController
from assistant.services.code_service import CodeService
from assistant.controllers.progression_document_controller import ProgressionDocumentController
from assistant.services.theme_service import ThemeService
from assistant.services.undo_redo_service import UndoRedoService
from assistant.services.catalogue_service import CatalogueService
from assistant.services.export_service import ExportService
from assistant.services.progression_analysis_service import ProgressionAnalysisService
from assistant.services.progression_service import ProgressionService
from assistant.services.search_service import SearchService
from assistant.controllers.progression_controller import ProgressionController
from assistant.controllers.code_index_controller import CodeIndexController
from assistant.controllers.session_controller import SessionController
from assistant.services.search_pdf_service import SearchPDFService
from assistant.services.pedago_data_service import PedagoDataService
from assistant.services.process_service import ProcessService
from assistant.services.html_service import HtmlService
from pathlib import Path


@dataclass
class AppContext:
    persistence_service: PersistenceService
    config: Config
    session_controller: SessionController
    paths: Paths
    export_service: ExportService
    undo_redo_service: UndoRedoService
    progression_analysis_service: ProgressionAnalysisService
    progression_service: ProgressionService
    progression_controller: ProgressionController
    code_index_controller: CodeIndexController
    code_index_data: dict
    code_service: CodeService
    catalogue_service: CatalogueService
    search_service: SearchService
    theme_service: ThemeService
    document_controller: ProgressionDocumentController
    code_index_controller: CodeIndexController
    pedago_data_service: PedagoDataService
    search_pdf_service: SearchPDFService
    process_service: ProcessService
    html_service: HtmlService

def create_context(main_window) -> AppContext:

    persistence_service = PersistenceService()
    config = persistence_service.load_config()
    session_controller = SessionController(
        config,
        persistence_service,
        main_window
        )
    paths = Paths(config)
    export_service = ExportService(config.codes)
    undo_redo_service = UndoRedoService()
    if not hasattr(paths, "code_index") or paths.code_index is None:
        print("Warning: 'code_index' path is not set. Using current working directory.")
        paths.code_index = Path.cwd()
    pedago_data_service = PedagoDataService(
        paths.code_index / config.settings.current.pdf_data_file_name,
        to_convert = config.settings.pedago_service.to_convert)

    code_index_document_controller = CodeIndexDocumentController(paths.code_index_file)
    code_index_data = code_index_document_controller.load_data()
    code_service = CodeService(config.codes)
    catalogue_service = CatalogueService(code_index_data, config.catalogues)
    code_index_controller = CodeIndexController(
        paths,
        config,
        catalogue_service,
        code_index_document_controller
    )
    search_service = SearchService(code_service, catalogue_service)
    progression_analysis_service = ProgressionAnalysisService(catalogue_service)
    progression_service = ProgressionService(
        code_service,
        catalogue_service,
        progression_analysis_service,
        config
        )
    progression_controller = ProgressionController(
        progression_service,
        undo_redo_service,
    )
    document_controller = ProgressionDocumentController(
        progression_service=progression_service,
        persistence_service=persistence_service,
        session_controller=session_controller,
        export_service=export_service,
        undo_redo_service=undo_redo_service,
        code_service=code_service,
        paths=paths,
        current_file=config.settings.current.current_file_path
    )
    theme_name = config.settings.current.theme
    theme_service = ThemeService(
        themes=config.settings.themes,
        default_theme=theme_name
        )

    search_pdf_service = SearchPDFService(
        pedago_data_service=pedago_data_service,
    )

    html_service = HtmlService()
    
    process_service = ProcessService()

    return AppContext(
        persistence_service=persistence_service,
        config=config,
        paths=paths,
        session_controller=session_controller,
        export_service=export_service,
        undo_redo_service=undo_redo_service,
        progression_analysis_service=progression_analysis_service,
        progression_service=progression_service,
        progression_controller=progression_controller,
        code_index_controller=code_index_controller,
        code_index_data=code_index_data,
        code_service=code_service,
        catalogue_service=catalogue_service,
        search_service=search_service,
        document_controller=document_controller,
        theme_service=theme_service,
        pedago_data_service=pedago_data_service,
        search_pdf_service=search_pdf_service,
        process_service=process_service,
        html_service=html_service
    )