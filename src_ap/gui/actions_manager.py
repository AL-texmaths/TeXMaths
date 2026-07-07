# actions_manager.py
from PySide6.QtGui import QAction, Qt
from PySide6.QtWidgets import QPushButton
from PySide6.QtGui import QKeySequence


class ActionManager:

    def __init__(self, parent):
        self.parent = parent
        self.actions = {}
        self.buttons = {}

    def register(self, definition):

        action = QAction(definition.text, self.parent)
        if definition.shortcut is not None:
            if definition.shortcut.startswith("special:"):
                special_shortcut = definition.shortcut.split(":")[1]
                action.setShortcut(getattr(QKeySequence, special_shortcut))
            else:
                action.setShortcut(QKeySequence(definition.shortcut))
        action.setCheckable(definition.checkable)

        action.triggered.connect(definition.slot)

        self.parent.addAction(action)

        self.actions[definition.id] = action

        if definition.button:
            button = QPushButton(action.text())
            button.setToolTip(action.shortcut().toString())
            button.clicked.connect(action.trigger)
            self.buttons[definition.id] = button

    def action(self, id_):
        return self.actions[id_]

    def button(self, id_):
        return self.buttons.get(id_)