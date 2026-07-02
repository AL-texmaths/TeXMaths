from assistant_progression.services.regex_service import SearchLineEdit

from PySide6.QtWidgets import (
    QListWidget, QWidget, QComboBox, QVBoxLayout
)


class RegexPanel(QWidget):
    def __init__(self, search_service, default_label=None):
        super().__init__()

        self.layout = QVBoxLayout()

        self.search_service = search_service
        self.catalogue_combo = QComboBox()
        self.type_combo = QComboBox()
        
        self.view_mode_combo = QComboBox()
        self.view_mode_combo.addItems([
            "Afichage unique",
            "Liste complète filtrée"
        ])

        self.list_widget = QListWidget()
        self.search_line = SearchLineEdit(self.list_widget)
        self.search_line.setPlaceholderText("Regex sur code ou contenu")

        self.search_service.populate_filters(
            self.catalogue_combo
        )

        if default_label is not None:
            index = self.catalogue_combo.findText(default_label)
        else:
            index = 0
        if index >= 0:
            self.catalogue_combo.setCurrentIndex(index)
        
        self.build_qvboxlayout()
    
    def build_qvboxlayout(self):
        self.layout.addWidget(self.catalogue_combo)
        self.layout.addWidget(self.type_combo)
        self.layout.addWidget(self.view_mode_combo)
        self.layout.addWidget(self.search_line)
        self.layout.addWidget(self.list_widget)

        self.setLayout(self.layout)