import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QListWidget, QDialog
from PySide6.QtCore import Qt

class BOcodeGUI(QWidget):
    def __init__(self):
        super().__init__()

    def show_unused_items(self):

        unused = self.get_unused_entries()

        dialog = QDialog()
        dialog.setWindowTitle("Items non utilisés")
        dialog.resize(700, 800)

        dialog_layout = QVBoxLayout()

        liste = QListWidget()
        for entry in unused:
            texte = f'{entry["code"]} [{entry["type"]}] - {entry["text"]}'
            liste.addItem(texte)

        dialog_layout.addWidget(liste)
        dialog.setLayout(dialog_layout)

        # Installer un événement sur le dialogue pour intercepter les raccourcis clavier
        dialog.installEventFilter(self)

        self.unused_window = dialog

    def get_unused_entries(self):
        # Implémentez cette méthode pour renvoyer la liste des entrées non utilisées
        return [{"code": "001", "type": "Type1", "text": "Text1"}, {"code": "002", "type": "Type2", "text": "Text2"}]

    def eventFilter(self, obj, event):
        if event.type() == event.KeyPress:
            # Intercepter le raccourci Ctrl+Q
            if (event.modifiers() & Qt.ControlModifier) and (event.key() == Qt.Key_Q):
                self.unused_window.close()
                return True  # Consommer l'événement pour éviter qu'il ne soit traité par d'autres widgets
        return super().eventFilter(obj, event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BOcodeGUI()
    window.show_unused_items()
    sys.exit(app.exec())