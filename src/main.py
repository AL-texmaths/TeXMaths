from PySide6.QtWidgets import QApplication

from app.startup import create_context
from views.main_window import MainWindow


def main():

    app = QApplication([])

    context = create_context()

    window = MainWindow(context)

    window.show()

    app.exec()


if __name__ == "__main__":
    main()