# regex_help.py
from typing import Callable

from PySide6.QtCore import QObject, Qt
from PySide6.QtGui import QAction, QKeySequence, QShortcut
from PySide6.QtWidgets import QLineEdit, QStyle

from assistant.gui.dialogs.regex_help_dialog import RegexHelpDialog
from assistant.utils.regex_help import regex_error

BASE_TOOLTIP = "Regex — cliquer sur « ? » ou Ctrl+Maj+R pour l'aide"
ERROR_STYLE = "QLineEdit { border: 2px solid #d9534f; }"


class RegexHelp(QObject):
    """Ajoute à un QLineEdit un bouton d'aide regex et un retour visuel sur les erreurs."""

    def __init__(
        self,
        line_edit: QLineEdit,
        count_provider: Callable[[str], int] | None = None,
        auto_validate: bool = True,
    ):
        super().__init__(line_edit)
        self.line_edit = line_edit
        self.count_provider = count_provider
        self._dialog: RegexHelpDialog | None = None

        line_edit.setToolTip(BASE_TOOLTIP)

        icon = line_edit.style().standardIcon(QStyle.SP_MessageBoxQuestion)
        action = QAction(icon, "Aide regex", line_edit)
        action.setToolTip("Aide-mémoire et constructeur de regex")
        action.triggered.connect(self.open_dialog)
        line_edit.addAction(action, QLineEdit.TrailingPosition)

        shortcut = QShortcut(QKeySequence("Ctrl+Shift+R"), line_edit)
        shortcut.setContext(Qt.WidgetShortcut)
        shortcut.activated.connect(self.open_dialog)

        if auto_validate:
            line_edit.textChanged.connect(
                lambda text: self.set_error(regex_error(text))
            )

    def set_error(self, message: str | None):
        if message:
            self.line_edit.setStyleSheet(ERROR_STYLE)
            self.line_edit.setToolTip(f"Regex invalide : {message}")
        else:
            self.line_edit.setStyleSheet("")
            self.line_edit.setToolTip(BASE_TOOLTIP)

    def open_dialog(self):
        if self._dialog is None:
            self._dialog = RegexHelpDialog(
                self.line_edit,
                self.count_provider,
                parent=self.line_edit.window(),
            )
        self._dialog.show()
        self._dialog.raise_()
        self._dialog.activateWindow()


def install_regex_help(
    line_edit: QLineEdit,
    count_provider: Callable[[str], int] | None = None,
    auto_validate: bool = True,
) -> RegexHelp:
    return RegexHelp(line_edit, count_provider, auto_validate)
