# application_context.py
from dataclasses import dataclass
from src_ap.services.persistence_service import PersistenceService
from src_ap.models.config import Config
from src_ap.models.paths import Paths
from src_ap.controllers.code_index_document_controller import CodeIndexDocumentController
from src_ap.services.code_service import CodeService
from src_ap.controllers.progression_document_controller import ProgressionDocumentController
from src_ap.services.theme_service import ThemeService
from src_ap.services.undo_redo_service import UndoRedoService
from src_ap.services.catalogue_service import CatalogueService
from src_ap.services.export_service import ExportService
from src_ap.services.progression_analysis_service import ProgressionAnalysisService
from src_ap.services.progression_service import ProgressionService
from src_ap.services.search_service import SearchService
from src_ap.controllers.progression_controller import ProgressionController
from src_ap.controllers.code_index_controller import CodeIndexController
from src_ap.controllers.session_controller import SessionController
from src_ap.services.search_pdf_service import SearchPDFService
from src_ap.services.pedago_data_service import PedagoDataService
from src_ap.services.process_service import ProcessService


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
    pedago_data_service = PedagoDataService(paths.code_index / config.settings.current.pdf_data_file_name)

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
        repository=pedago_data_service,
    )
    
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
        process_service=process_service
    )