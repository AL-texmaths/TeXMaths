from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QLineEdit


class SearchInput(QLineEdit):
    def __init__(self, callback, results_list=None):
        super().__init__()
        self.setPlaceholderText("Recherche (regex)")
        self.textChanged.connect(self.schedule_search)
        self.callback = callback
        self.results_list = results_list

        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.callback)
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Down:
            if self.results_list and self.results_list.count() > 0:
                self.results_list.setCurrentRow(0)
                self.results_list.setFocus()
                return
        super().keyPressEvent(event)
        
    def schedule_search(self):
        self.search_timer.start(300)

