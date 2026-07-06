from PySide6.QtCore import QObject, Signal

from assistant_progression.utils.textools import update_code_index
from src.update_data_index import update_json
from src.check_database import check_database
from src.extract_preview import update_previews


class DatabaseWorker(QObject):
    message = Signal(str)
    finished = Signal(int, int)
    
    def __init__(self, config=None):
        super().__init__()
        self.config = config

    def run(self):
        def log(msg):
            self.message.emit(msg)

        codes_labels_dir = self.config.get_path_by_key("codes_labels")
        code_index_dir = self.config.get_path_by_key("code_index")
        texmf_dir = self.config.get_path_by_key("texmf")
        update_code_index(codes_labels_dir, code_index_dir, texmf_dir, logger=log)
        update_previews(logger=log)
        errors, warnings = check_database(logger=log)
        errors_sup, warnings_sup = 0, 0
        if errors == 0:
            errors_sup, warnings_sup = update_json(logger=log)
        errors += errors_sup
        warnings += warnings_sup

        self.finished.emit(errors, warnings)