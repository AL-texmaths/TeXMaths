from src_ap.app.application_context import create_context
from src_ap.services.update_data_service import UpdateDataService

if __name__ == "__main__":
    print('UPDATING : data index ...')
    update_data_service = UpdateDataService(create_context(None))
    update_data_service.update_data_index()
    print(f'module {__file__} ok')