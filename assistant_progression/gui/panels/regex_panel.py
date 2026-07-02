import re
from assistant_progression.services.regex_service import SearchLineEdit

from PySide6.QtWidgets import (
    QListWidget, QWidget, QComboBox, QVBoxLayout
)
from PySide6.QtCore import QEvent


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
    
        self.init_signals()

        
        self.install_event_filter(self)
    
    def install_event_filter(self, widget):
        for widget in (
            self.catalogue_combo,
            self.type_combo,
            self.view_mode_combo,
            self.search_line,
            self.list_widget,
        ):
            widget.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.FocusIn:
            self.last_focused = obj
        return super().eventFilter(obj, event)

    def init_signals(self):
        self.search_line.textChanged.connect(
            lambda _: self.update_search()
        )
        self.type_combo.currentTextChanged.connect(
            lambda _: self.update_search()
        )

    def build_qvboxlayout(self):
        self.layout.addWidget(self.catalogue_combo)
        self.layout.addWidget(self.type_combo)
        self.layout.addWidget(self.view_mode_combo)
        self.layout.addWidget(self.search_line)
        self.layout.addWidget(self.list_widget)

        self.setLayout(self.layout)
    
    def update_search(self) -> list:

        regex_text = self.search_line.text()

        try:
            entries = self.search_service.search(
                self.catalogue_combo,
                self.type_combo,
                regex_text
            )

        except re.error:

            return

        self.current_matches = entries

        self.list_widget.clear()

        for entry in entries:

            self.list_widget.addItem(
                f"{entry.code} [{entry.type}]" if entry.type else f"{entry.code}"
            )
        

        if entries:

            self.list_widget.setCurrentRow(0)

        return entries
    
    def update_type_filter(self):
        self.search_service.update_type_filter(
            self.catalogue_combo,
            self.type_combo
        )

    def selected_catalogue(self):
        return self.search_service.selected_catalogue(
            self.catalogue_combo
        )

    def get_selected_entry(self):
        current_row = self.list_widget.currentRow()
        if current_row >= 0 and current_row < len(self.current_matches):
            return self.current_matches[current_row]
        return None