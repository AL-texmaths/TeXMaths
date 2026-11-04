# regex_help_dialog.py
from typing import Callable

from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from assistant.utils.regex_help import (
    GENERAL_NOTE,
    PLACEHOLDER,
    PREFIX_NOTE,
    RECIPES,
    build_regex,
    regex_error,
    split_words,
)


class RegexHelpDialog(QDialog):
    """Aide-mémoire et constructeur de regex liés à une barre de recherche."""

    def __init__(
        self,
        target: QLineEdit,
        count_provider: Callable[[str], int] | None = None,
        parent=None,
    ):
        super().__init__(parent)
        self.target = target
        self.count_provider = count_provider
        self.setWindowTitle("Aide regex")
        self.resize(760, 480)

        tabs = QTabWidget()
        tabs.addTab(self._build_cheatsheet_tab(), "Aide-mémoire")
        tabs.addTab(self._build_builder_tab(), "Constructeur")

        layout = QVBoxLayout(self)
        layout.addWidget(tabs)

    # --- Aide-mémoire -------------------------------------------------

    def _build_cheatsheet_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)

        note = QLabel(f"{GENERAL_NOTE}\n{PREFIX_NOTE}")
        note.setWordWrap(True)
        layout.addWidget(note)

        self.table = QTableWidget(len(RECIPES), 3)
        self.table.setHorizontalHeaderLabels(["Besoin", "Syntaxe", "Exemple"])
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setStretchLastSection(True)
        for row, recipe in enumerate(RECIPES):
            for col, value in enumerate((recipe.need, recipe.syntax, recipe.example)):
                self.table.setItem(row, col, QTableWidgetItem(value))
        self.table.cellDoubleClicked.connect(self._insert_recipe)
        layout.addWidget(self.table)

        hint = QLabel("Double-clic sur une ligne : insère la syntaxe dans la barre de recherche.")
        layout.addWidget(hint)
        return tab

    def _insert_recipe(self, row: int, _column: int = 0):
        self._set_target_text(RECIPES[row].syntax, select=PLACEHOLDER)

    # --- Constructeur -------------------------------------------------

    def _build_builder_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)

        form = QFormLayout()
        self.all_edit = QLineEdit()
        self.any_edit = QLineEdit()
        self.none_edit = QLineEdit()
        self.all_edit.setPlaceholderText("fraction pourcentage")
        self.any_edit.setPlaceholderText("4e 3e")
        self.none_edit.setPlaceholderText("brevet")
        form.addRow("Doit contenir TOUS ces mots (ET) :", self.all_edit)
        form.addRow("Doit contenir AU MOINS UN de ces mots (OU) :", self.any_edit)
        form.addRow("Ne doit contenir AUCUN de ces mots (SAUF) :", self.none_edit)
        layout.addLayout(form)

        layout.addWidget(QLabel('Séparer les mots par des espaces ; "entre guillemets" pour une expression.'))

        self.whole_word_checkbox = QCheckBox("Mots entiers uniquement")
        layout.addWidget(self.whole_word_checkbox)

        self.result_edit = QLineEdit()
        self.result_edit.setReadOnly(True)
        form_result = QFormLayout()
        form_result.addRow("Regex générée :", self.result_edit)
        layout.addLayout(form_result)

        self.count_label = QLabel("")
        layout.addWidget(self.count_label)

        buttons = QHBoxLayout()
        buttons.addStretch()
        self.insert_button = QPushButton("Insérer dans la barre")
        self.insert_button.setEnabled(False)
        self.insert_button.clicked.connect(self._insert_built)
        buttons.addWidget(self.insert_button)
        layout.addLayout(buttons)
        layout.addStretch()

        for edit in (self.all_edit, self.any_edit, self.none_edit):
            edit.textChanged.connect(self._refresh_builder)
        self.whole_word_checkbox.stateChanged.connect(self._refresh_builder)
        return tab

    def _refresh_builder(self):
        pattern = build_regex(
            split_words(self.all_edit.text()),
            split_words(self.any_edit.text()),
            split_words(self.none_edit.text()),
            self.whole_word_checkbox.isChecked(),
        )
        self.result_edit.setText(pattern)
        self.insert_button.setEnabled(bool(pattern))
        self.count_label.setText(self._count_text(pattern))

    def _count_text(self, pattern: str) -> str:
        if not pattern or self.count_provider is None:
            return ""
        if regex_error(pattern):
            return "Regex invalide"
        try:
            count = self.count_provider(pattern)
        except Exception:
            return ""
        return f"{count} résultat{'s' if count > 1 else ''}"

    def _insert_built(self):
        self._set_target_text(self.result_edit.text())

    # --- Commun -------------------------------------------------------

    def _set_target_text(self, text: str, select: str | None = None):
        self.target.setText(text)
        self.target.setFocus()
        if select:
            index = text.find(select)
            if index >= 0:
                self.target.setSelection(index, len(select))
        self.target.window().activateWindow()
