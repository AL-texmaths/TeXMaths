# regex_panel.py
import re
from src_ap.services.regex_service import SearchLineEdit
from src_ap.app.logger import logger

from PySide6.QtWidgets import (
    QListWidget, QListWidgetItem, QWidget, QComboBox, QVBoxLayout, QCheckBox
)
from PySide6.QtCore import QEvent, Qt


class ViewMode:
    SINGLE = "Affichage unique"
    FILTERED_LIST = "Liste complète filtrée"


class RegexPanel(QWidget):
    def __init__(self, search_service, analysis_service=None, default_catalogue_label=None, default_type_label:str|None=None):
        super().__init__()

        self.layout = QVBoxLayout()

        self.search_service = search_service
        self.analysis_service = analysis_service
        self.tree = None
        self.catalogue_combo = QComboBox()
        self.type_combo = QComboBox()

        
        self.view_mode_combo = QComboBox()

        self.view_mode_combo.addItems([
            ViewMode.SINGLE,
            ViewMode.FILTERED_LIST
        ])

        self.list_widget = QListWidget()
        self.search_line = SearchLineEdit(self.list_widget)
        self.search_line.setPlaceholderText("Regex sur code ou contenu")

        self.hide_located_checkbox = QCheckBox("Masquer les items déjà utilisés")

        self.search_service.populate_catalogue_combobox(
            self.catalogue_combo
        )

        if default_catalogue_label is not None:
            catalogue_index = self.catalogue_combo.findText(default_catalogue_label)
        else:
            catalogue_index = 0
        if catalogue_index >= 0:
            self.catalogue_combo.setCurrentIndex(catalogue_index)

        self.search_service.populate_type_combobox(
            self.catalogue_combo,
            self.type_combo
        )
        if default_type_label is not None:
            type_index = self.type_combo.findText(default_type_label)
        else:
            type_index = 0
        if type_index >= 0:
            self.type_combo.setCurrentIndex(type_index)
        
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
            self.hide_located_checkbox,
        ):
            widget.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.FocusIn:
            self.last_focused = obj
        return super().eventFilter(obj, event)

    def init_signals(self):
        self.search_line.textChanged.connect(
            self.update_search
        )
        self.hide_located_checkbox.stateChanged.connect(
            self.update_search
        )

    def build_qvboxlayout(self):
        self.layout.addWidget(self.catalogue_combo)
        self.layout.addWidget(self.type_combo)
        self.layout.addWidget(self.view_mode_combo)
        self.layout.addWidget(self.search_line)
        self.layout.addWidget(self.list_widget)
        self.layout.addWidget(self.hide_located_checkbox)

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
            return []

        if self.hide_located_checkbox.isChecked() and self.analysis_service and self.tree:
            used_ids = self.analysis_service.get_used_ids(self.tree)
            entries = [e for e in entries if e.id not in used_ids]

        self.current_matches = entries
        self.list_widget.clear()

        for entry in entries:

            text = (
                f"{entry.code} [{entry.type}]"
                if entry.type else entry.code
            )

            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, entry.id)
            self.list_widget.addItem(item)

        if entries:
            self.list_widget.setCurrentRow(0)

        return entries
    
    def update_type_filter(self):
        self.search_service.populate_type_combobox(
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