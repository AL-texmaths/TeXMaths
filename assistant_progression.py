import sys
from PySide6.QtWidgets import QApplication
from assistant_progression.gui.main_window import MainWindow

app = QApplication(sys.argv)
w = MainWindow()
w.show()
sys.exit(app.exec())