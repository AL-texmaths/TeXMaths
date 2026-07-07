from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class DocumentTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.label = QLabel("Document Tab Content")
        self.layout.addWidget(self.label)