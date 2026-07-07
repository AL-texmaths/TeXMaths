import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from src_ap.gui.main_window import MainWindow
from src_ap.utils.resolve import check_project_layout
from src_ap.app.logger import logger


BASE_DIR = Path(__file__).resolve().parent
check_project_layout(BASE_DIR)
app = QApplication(sys.argv)
w = MainWindow()
w.show()
logger.info("starting application")
sys.exit(app.exec())