from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMenu,
    QPushButton,
    QScrollArea,
    QToolButton,
    QVBoxLayout,
    QWidget,
    QWidgetAction,
)

from assistant.models.config import PDFFiltersModel, PDFSelectionModel


class FilterSection(QWidget):
    changed = Signal()

    def __init__(self, title: str, selection: PDFSelectionModel, parent=None):
        super().__init__(parent)
        self.title = title
        self.selection = selection
        self.checkboxes: dict[str, QCheckBox] = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(QLabel(title))
        buttons = QHBoxLayout()
        all_button = QPushButton("Tous")
        all_button.clicked.connect(self.select_all)
        none_button = QPushButton("Aucun")
        none_button.clicked.connect(self.select_none)
        buttons.addWidget(all_button)
        buttons.addWidget(none_button)
        buttons.addStretch()
        layout.addLayout(buttons)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setMaximumHeight(150)
        layout.addWidget(self.scroll_area)

    def set_items(self, items: list[str]):
        container = QWidget()
        rows = QVBoxLayout(container)
        rows.setContentsMargins(0, 0, 0, 0)
        self.checkboxes = {}
        for name in items:
            row = QHBoxLayout()
            checkbox = QCheckBox(name)
            checkbox.setChecked(
                self.selection.all_selected or name in self.selection.selected
            )
            checkbox.toggled.connect(
                lambda checked, item=name: self._toggle(item, checked)
            )
            only_button = QPushButton("Seul")
            only_button.setAccessibleName(f"Sélectionner uniquement {name}")
            only_button.clicked.connect(lambda _checked=False, item=name: self.select_only(item))
            row.addWidget(checkbox, 1)
            row.addWidget(only_button)
            rows.addLayout(row)
            self.checkboxes[name] = checkbox
        if not items:
            rows.addWidget(QLabel("Aucun élément disponible"))
        rows.addStretch()
        self.scroll_area.setWidget(container)

    def checked_items(self) -> list[str]:
        return [name for name, checkbox in self.checkboxes.items() if checkbox.isChecked()]

    def _toggle(self, name: str, checked: bool):
        if self.selection.all_selected:
            self.selection.all_selected = False
            self.selection.selected = list(self.checkboxes)
        selected = set(self.selection.selected)
        if checked:
            selected.add(name)
        else:
            selected.discard(name)
        self.selection.selected = sorted(selected)
        self.changed.emit()

    def _apply(self):
        for name, checkbox in self.checkboxes.items():
            checkbox.blockSignals(True)
            checkbox.setChecked(
                self.selection.all_selected or name in self.selection.selected
            )
            checkbox.blockSignals(False)
        self.changed.emit()

    def select_all(self):
        self.selection.all_selected = True
        self.selection.selected = []
        self._apply()

    def select_none(self):
        self.selection.all_selected = False
        self.selection.selected = []
        self._apply()

    def select_only(self, name: str):
        self.selection.all_selected = False
        self.selection.selected = [name]
        self._apply()


class PDFFiltersButton(QToolButton):
    changed = Signal()

    def __init__(self, filters: PDFFiltersModel, parent=None):
        super().__init__(parent)
        self.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        menu = QMenu(self)
        action = QWidgetAction(menu)
        panel = QWidget(menu)
        layout = QVBoxLayout(panel)
        self.types = FilterSection("Types de documents", filters.types, panel)
        self.fields = FilterSection("Champs de recherche", filters.fields, panel)
        layout.addWidget(self.types)
        layout.addWidget(self.fields)
        reset = QPushButton("Réinitialiser les filtres")
        reset.clicked.connect(self.reset_filters)
        layout.addWidget(reset)
        action.setDefaultWidget(panel)
        menu.addAction(action)
        self.setMenu(menu)
        self.types.changed.connect(self._selection_changed)
        self.fields.changed.connect(self._selection_changed)
        self._update_summary()

    def set_items(self, types: list[str], fields: list[str]):
        self.types.set_items(types)
        self.fields.set_items(fields)
        self._update_summary()

    def set_filters(self, filters: PDFFiltersModel):
        types = list(self.types.checkboxes)
        fields = list(self.fields.checkboxes)
        self.types.selection = filters.types
        self.fields.selection = filters.fields
        self.set_items(types, fields)

    def reset_filters(self):
        for section in (self.types, self.fields):
            section.blockSignals(True)
            section.select_all()
            section.blockSignals(False)
        self._selection_changed()

    def _selection_changed(self):
        self._update_summary()
        self.changed.emit()

    def _update_summary(self):
        active = not self.types.selection.all_selected or not self.fields.selection.all_selected
        self.setText("Filtres •" if active else "Filtres")
        summaries = []
        for label, section in (("Types", self.types), ("Champs", self.fields)):
            if section.selection.all_selected:
                description = "tous"
            else:
                checked = section.checked_items()
                description = ", ".join(checked) if checked else "aucun"
            summaries.append(f"{label} : {description}")
        self.setToolTip("\n".join(summaries))

    def empty_selection_message(self) -> str:
        missing = []
        if not self.types.checked_items():
            missing.append("Aucun type sélectionné")
        if not self.fields.checked_items():
            missing.append("Aucun champ sélectionné")
        return " ; ".join(missing)
