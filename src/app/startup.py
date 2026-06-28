from app.context import AppContext
from app.config import ConfigManager

from services.document_repository import DocumentRepository
from services.process_service import ProcessService
from services.theme_service import ThemeService
from services.database_service import DatabaseService


def create_context():

    config = ConfigManager()

    repository = DocumentRepository(
        config.database_path
    )

    process_service = ProcessService(config)

    theme_service = ThemeService(config)

    database_service = DatabaseService(config)

    return AppContext(
        config=config,
        repository=repository,
        process_service=process_service,
        theme_service=theme_service,
        database_service=database_service
    )