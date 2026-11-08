from datetime import datetime, timedelta
from pathlib import Path
import traceback
from uuid import uuid4

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import (
    QDialog, QLabel, QPlainTextEdit, QPushButton, QVBoxLayout,
)

from assistant.app.logger import LOG_DIR, logger


class DiagnosticThread(QThread):
    message = Signal(str)
    outcome = Signal(bool, str)

    def __init__(self, operation, parent=None):
        super().__init__(parent)
        self.operation = operation

    def run(self):
        try:
            success, summary = self.operation(self.message.emit)
        except Exception:
            details = traceback.format_exc()
            logger.exception("Échec du diagnostic")
            self.message.emit(details)
            self.outcome.emit(False, "Échec du diagnostic ; voir les détails ci-dessus.")
        else:
            self.outcome.emit(success, summary)


class DiagnosticDialog(QDialog):
    def __init__(self, title, operation, on_success=None, parent=None, log_dir=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(850, 550)
        self.on_success = on_success
        self._running = True
        self._success = False
        self._summary = "Le diagnostic s'est arrêté sans résultat."
        self._log = None
        self._log_error = False

        layout = QVBoxLayout(self)
        self.status = QLabel("Diagnostic en cours…")
        self.log_label = QLabel()
        self.log_label.setWordWrap(True)
        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        self.close_button = QPushButton("Fermer")
        self.close_button.setEnabled(False)
        self.close_button.clicked.connect(self.accept)
        layout.addWidget(self.status)
        layout.addWidget(self.log_label)
        layout.addWidget(self.output)
        layout.addWidget(self.close_button)

        directory = Path(log_dir) if log_dir is not None else LOG_DIR / "diagnostics"
        try:
            directory.mkdir(parents=True, exist_ok=True)
            self.log_path = directory.resolve() / (
                f"diagnostic-{datetime.now():%Y%m%d-%H%M%S}-{uuid4().hex}.log"
            )
            self._log = self.log_path.open("x", encoding="utf-8")
            self.log_label.setText(f"Journal : {self.log_path}")
        except OSError as exc:
            self.log_path = None
            self._report_log_error(exc)

        self._append(f"{title} — {datetime.now():%Y-%m-%d %H:%M:%S}")
        if self._log is not None:
            self._remove_old_logs(directory)
        self._worker = DiagnosticThread(operation, self)
        self._worker.message.connect(self._append)
        self._worker.outcome.connect(self._receive_outcome)
        self._worker.finished.connect(self._finish)

    def start(self):
        self._worker.start()
        return self.exec()

    def _report_log_error(self, exc):
        logger.error("Impossible d'écrire le journal de diagnostic : %s", exc)
        self._log_error = True
        self.log_label.setText(f"Journal indisponible ou incomplet : {exc}")
        self.output.appendPlainText(f"ERREUR de journalisation : {exc}")

    def _remove_old_logs(self, directory):
        cutoff = (datetime.now() - timedelta(days=90)).timestamp()
        try:
            for path in directory.glob("diagnostic-*.log"):
                if path != self.log_path and path.stat().st_mtime < cutoff:
                    path.unlink()
        except OSError as exc:
            self._append(f"Attention : nettoyage des anciens journaux impossible : {exc}")
            logger.warning("Nettoyage des journaux de diagnostic impossible : %s", exc)

    def _append(self, message):
        self.output.appendPlainText(str(message))
        if self._log is not None:
            try:
                self._log.write(f"{message}\n")
                self._log.flush()
            except OSError as exc:
                self._report_log_error(exc)
                try:
                    self._log.close()
                except OSError:
                    pass
                self._log = None

    def _receive_outcome(self, success, summary):
        self._success = success
        self._summary = summary

    def _finish(self):
        if self._success and self.on_success is not None:
            try:
                self.on_success()
            except Exception:
                logger.exception("Échec du rechargement après diagnostic")
                self._append(traceback.format_exc())
                self._summary = "Diagnostic terminé, mais le rechargement de l'interface a échoué."
        self._append(self._summary)
        if self._log is not None:
            try:
                self._log.close()
            except OSError as exc:
                self._report_log_error(exc)
            self._log = None
        self.status.setText(
            self._summary + (" Journal indisponible ou incomplet." if self._log_error else "")
        )
        self._running = False
        self.close_button.setEnabled(True)

    def reject(self):
        if not self._running:
            super().reject()

    def closeEvent(self, event):
        if self._running:
            event.ignore()
        else:
            super().closeEvent(event)
