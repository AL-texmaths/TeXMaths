from dataclasses import dataclass
from src.app.config import ConfigManager
from src.services.document_repository import DocumentRepository
# from src.services.database_service import DatabaseService
# from src.services.process_service import ProcessService
# from src.services.theme_service import ThemeService

@dataclass
class AppContext:

    config: ConfigManager

    repository: DocumentRepository

    # process_service: ProcessService

    # theme_service: ThemeService

    # database_service: DatabaseService