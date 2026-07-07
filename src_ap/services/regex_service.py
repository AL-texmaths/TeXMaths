from PySide6.QtWidgets import QLineEdit
from PySide6.QtCore import Qt

class SearchLineEdit(QLineEdit):

    def __init__(self, list_widget):
        super().__init__()
        self.list_widget = list_widget

    def keyPressEvent(self, event):

        row = self.list_widget.currentRow()

        if event.key() == Qt.Key_Down:
            if self.list_widget.count():
                self.list_widget.setFocus()
                if row < self.list_widget.count() - 1:
                    self.list_widget.setCurrentRow(row + 1)
            return

        if event.key() == Qt.Key_Up:
            if self.list_widget.count():
                self.list_widget.setFocus()
                if row > 0:
                    self.list_widget.setCurrentRow(row - 1)
            return

        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.list_widget.setFocus()
            return

        super().keyPressEvent(event)