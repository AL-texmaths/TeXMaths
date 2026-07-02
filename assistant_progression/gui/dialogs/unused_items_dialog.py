# unused_items_dialog.py
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QListWidget, QPushButton

from assistant_progression.models.config import Config


class UnusedItemsDialog(QDialog):

    def __init__(self, unused_items, config:Config):
        super().__init__()
        title = config.settings.unused_items_dialog.title
        width = config.settings.unused_items_dialog.width
        height = config.settings.unused_items_dialog.height
        self.setWindowTitle(title)
        self.resize(width, height)

        self.layout = QVBoxLayout()
        self.list = QListWidget()
        for entry in unused_items:
            text = (
                f'{entry.code} ',
                f'[{entry.type}] '
                f'- {entry.text}'
            )
            self.list.addItem(''.join(text))
        self.layout.addWidget(self.list)
        self.setLayout(self.layout)