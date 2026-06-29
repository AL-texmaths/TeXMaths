from src.app.context import AppContext
from src.app.config import ConfigManager

from src.services.document_repository import DocumentRepository
from src.services.process_service import ProcessService
# from src.services.theme_service import ThemeService
# from src.services.database_service import DatabaseService


def create_context():

    config = ConfigManager()

    repository = DocumentRepository(
        config.get_path_by_key("data index")
    )

    process_service = ProcessService()

    # theme_service = ThemeService(config)

    # database_service = DatabaseService(config)

    return AppContext(
        config=config,
        repository=repository,
        process_service=process_service,
        # theme_service=theme_service,
        # database_service=database_service
    )