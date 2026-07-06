from PySide6.QtCore import QObject, QThread, Signal

from src.workers.database_worker import DatabaseWorker


class DatabaseReloadController(QObject):

    message = Signal(str)
    finished = Signal(int, int)

    def __init__(self, config=None):
        super().__init__()
        self.config = config

        self._thread = None
        self._worker = None

    def reload(self):

        if self._thread is not None:
            return

        self._thread = QThread()

        self._worker = DatabaseWorker(config=self.config)

        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)

        self._worker.message.connect(self.message)

        self._worker.finished.connect(self.finished)

        self._worker.finished.connect(self._thread.quit)

        self._worker.finished.connect(self._worker.deleteLater)

        self._thread.finished.connect(self._thread.deleteLater)

        self._thread.finished.connect(self._cleanup)

        self._thread.start()

    def _cleanup(self):

        self._thread = None
        self._worker = None