from PySide6.QtGui import QAction
from PySide6.QtWidgets import QPushButton


class ActionManager:

    def __init__(self, parent):
        self.parent = parent
        self.actions = {}

    def register(self, definition):

        action = QAction(definition.text, self.parent)
        if definition.shortcut is not None:
            action.setShortcut(definition.shortcut)
        action.setCheckable(definition.checkable)

        action.triggered.connect(definition.slot)

        self.parent.addAction(action)

        self.actions[definition.id] = action

    def action(self, id_):
        return self.actions[id_]

    def button(self, id_):

        action = self.actions[id_]

        button = QPushButton(action.text())
        button.setToolTip(action.shortcut().toString())
        button.clicked.connect(action.trigger)

        return button