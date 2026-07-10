from src_ap.app.application_context import create_context
from src_ap.services.extract_flash_preview_service import FlashPreviewService

print(f'Running {__file__} as main')
flash_preview_service = FlashPreviewService(context=create_context(None), logger=print)
flash_preview_service.update_previews()
print(f'module {__file__} ok')