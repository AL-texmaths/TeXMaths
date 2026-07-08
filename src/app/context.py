from dataclasses import dataclass
from src.app.config import ConfigManager
from src_ap.services.document_repository import DocumentRepository
from src.services.process_service import ProcessService
from src.services.search_service import SearchService
# from src.services.database_service import DatabaseService
# from src.services.theme_service import ThemeService

@dataclass
class AppContext:

    config: ConfigManager

    repository: DocumentRepository

    process_service: ProcessService

    search_service: SearchService

    # theme_service: ThemeService

    # database_service: DatabaseService