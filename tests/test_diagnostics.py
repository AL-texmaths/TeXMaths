import os
import tempfile
import threading
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from typing import cast
from unittest.mock import Mock, patch

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from assistant.gui.dialogs.diagnostic_dialog import DiagnosticDialog
from assistant.models.config import Config
from assistant.services.check_database_service import CheckDatabaseService
from assistant.services.update_data_service import UpdateDataService
from assistant.utils.textools import check_code_index_data, update_code_index


class CodeIndexDiagnosticTests(unittest.TestCase):
    def test_all_files_are_checked_and_compilation_failure_preserves_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            labels = root / "labels"
            labels.mkdir()
            for name in ("a", "b"):
                (labels / f"{name}.tex").write_text("", encoding="utf-8")
            index = root / "code_index.json"
            index.write_text("original", encoding="utf-8")
            seen = []

            def compile_file(path, **kwargs):
                seen.append(path.name)
                kwargs["logger"](f"compilation {path.name}")
                return SimpleNamespace(returncode=1 if path.name == "a.tex" else 0)

            messages = []
            with patch("assistant.utils.textools.compile_latex", side_effect=compile_file):
                result = update_code_index(labels, root, root, logger=messages.append)
            self.assertEqual(result, 1)
            self.assertEqual(set(seen), {"a.tex", "b.tex"})
            self.assertEqual(index.read_text(encoding="utf-8"), "original")
            self.assertTrue(any("compilation a.tex" in message for message in messages))

    def test_missing_package_and_missing_compilation_output_are_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "catalogue.tex").write_text("", encoding="utf-8")
            config = cast(Config, SimpleNamespace(catalogues={
                "cat": SimpleNamespace(tex_file_name="catalogue.tex", sty_file_name="absent.sty")
            }))
            messages = []
            with patch("assistant.utils.textools.compile_latex",
                       return_value=SimpleNamespace(returncode=0)):
                result = check_code_index_data(root, root, config, messages.append)
            self.assertEqual(result, 1)
            self.assertTrue(any("introuvable" in message for message in messages))
            self.assertTrue(any("did not produce" in message for message in messages))

    def test_compilation_success_returns_integer_and_writes_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "catalogue.tex").write_text("", encoding="utf-8")

            def compile_file(path, **kwargs):
                path.with_name("catalogue-data.txt").write_text(
                    "cat|:|key|:|value\n", encoding="utf-8"
                )
                return SimpleNamespace(returncode=0)

            with patch("assistant.utils.textools.compile_latex", side_effect=compile_file):
                result = update_code_index(root, root, root, logger=lambda _: None)
            self.assertEqual(result, 0)
            self.assertIn("value", (root / "code_index.json").read_text(encoding="utf-8"))

    def test_configured_index_filename_is_used(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "catalogue-data.txt").write_text("cat|:|key|:|value\n", encoding="utf-8")
            config = cast(Config, SimpleNamespace(
                catalogues={},
                settings=SimpleNamespace(current=SimpleNamespace(code_index_file_name="custom.json")),
            ))
            result = update_code_index(root, root, root, config, logger=lambda _: None)
            self.assertEqual(result, 0)
            self.assertTrue((root / "custom.json").exists())


class ServiceDiagnosticTests(unittest.TestCase):
    def test_database_compilation_uses_diagnostic_logger(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "exercice-1-data.tex").write_text("start end", encoding="utf-8")
            doc_type = SimpleNamespace(dir_name=".", name_pattern=r"-\d+-data\.tex$")
            settings = SimpleNamespace(pedago_service=SimpleNamespace(
                pedago_doc_types={"exercice": doc_type}, string_check_order=["start", "end"],
                tex_non_optional_keys=[],
            ))
            messages = []
            report = messages.append
            service = CheckDatabaseService(settings, root, logger=report)
            with patch("assistant.services.check_database_service.get_pattern",
                       return_value=r"exercice-\d+-data\.tex$"), \
                 patch("assistant.services.check_database_service.compile_latex") as compile_mock:
                compile_mock.return_value.returncode = 0
                service.check_database()
            self.assertIs(compile_mock.call_args.kwargs["logger"], report)
            self.assertEqual(service.database_errors, 0)

    def test_data_errors_reset_for_each_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            settings = SimpleNamespace(
                pedago_service=SimpleNamespace(pedago_doc_types={}),
                current=SimpleNamespace(pdf_data_file_name="data.json"),
            )
            context = SimpleNamespace(
                config=SimpleNamespace(settings=settings),
                paths=SimpleNamespace(latex=root, code_index=root),
            )
            service = UpdateDataService(context, logger=lambda _: None)
            service.errors = 5
            service.update_data_index()
            self.assertEqual(service.errors, 0)


class DiagnosticDialogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def run_dialog(self, dialog):
        timed_out = []
        def finish_when_ready():
            if not dialog._running:
                timer.stop()
                dialog.accept()
        timer = QTimer()
        timer.timeout.connect(finish_when_ready)
        timer.start(10)
        def timeout():
            timed_out.append(True)
            dialog._worker.requestInterruption()
            dialog._worker.wait(3000)
            dialog._running = False
            dialog.reject()
        timeout_timer = QTimer()
        timeout_timer.setSingleShot(True)
        timeout_timer.timeout.connect(timeout)
        timeout_timer.start(5000)
        dialog.start()
        timer.stop()
        timeout_timer.stop()
        self.assertFalse(timed_out, "Diagnostic did not finish")

    def test_messages_summary_and_reload_are_logged(self):
        with tempfile.TemporaryDirectory() as tmp:
            calls = []
            def operation(report):
                report("Première ligne\nDeuxième ligne")
                return True, "Terminé. Anomalies : 2."
            dialog = DiagnosticDialog("Test", operation, lambda: calls.append("reload"), log_dir=tmp)
            self.run_dialog(dialog)
            assert dialog.log_path is not None
            content = dialog.log_path.read_text(encoding="utf-8")
            self.assertIn("Première ligne\nDeuxième ligne", content)
            self.assertIn("Anomalies : 2", content)
            self.assertIn("Première ligne", dialog.output.toPlainText())
            self.assertEqual(calls, ["reload"])

    def test_exception_and_logging_failure_are_visible(self):
        with tempfile.TemporaryDirectory() as tmp:
            invalid_dir = Path(tmp) / "not-a-directory"
            invalid_dir.write_text("", encoding="utf-8")
            calls = []
            def operation(report):
                raise ValueError("erreur de test")
            dialog = DiagnosticDialog("Test", operation, lambda: calls.append(1), log_dir=invalid_dir)
            self.run_dialog(dialog)
            self.assertIn("erreur de test", dialog.output.toPlainText())
            self.assertIn("Journal indisponible", dialog.status.text())
            self.assertEqual(calls, [])

    def test_dialog_stays_responsive_and_cannot_close_during_execution(self):
        with tempfile.TemporaryDirectory() as tmp:
            release = threading.Event()
            observed = []
            def operation(report):
                if not release.wait(3):
                    raise TimeoutError("Interface bloquée")
                return True, "Terminé"
            dialog = DiagnosticDialog("Test", operation, log_dir=tmp)
            def attempt_close():
                dialog.reject()
                observed.append(dialog.isVisible())
                release.set()
            QTimer.singleShot(30, attempt_close)
            self.run_dialog(dialog)
            self.assertEqual(observed, [True])

    def test_old_diagnostic_logs_are_removed(self):
        with tempfile.TemporaryDirectory() as tmp:
            old = Path(tmp) / "diagnostic-old.log"
            old.write_text("old", encoding="utf-8")
            timestamp = time.time() - 91 * 24 * 60 * 60
            os.utime(old, (timestamp, timestamp))
            dialog = DiagnosticDialog("Test", lambda report: (True, "Terminé"), log_dir=tmp)
            self.run_dialog(dialog)
            self.assertFalse(old.exists())
            assert dialog.log_path is not None
            self.assertTrue(dialog.log_path.exists())

    def test_reload_failure_is_logged_instead_of_reported_as_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            def reload_index():
                raise ValueError("échec de rechargement")
            dialog = DiagnosticDialog(
                "Test", lambda report: (True, "Terminé"), reload_index, log_dir=tmp
            )
            self.run_dialog(dialog)
            self.assertIn("rechargement de l'interface a échoué", dialog.status.text())
            assert dialog.log_path is not None
            self.assertIn("échec de rechargement", dialog.log_path.read_text(encoding="utf-8"))


class MainWindowDiagnosticTests(unittest.TestCase):
    def test_menu_operations_route_output_and_reload_only_on_success(self):
        from assistant.gui.main_window import MainWindow

        messages = []
        results = []

        class FakeDialog:
            def __init__(self, title, operation, on_success=None, parent=None):
                self.operation = operation
                self.on_success = on_success

            def start(self):
                success, summary = self.operation(messages.append)
                results.append((success, summary))
                if success and self.on_success:
                    self.on_success()

        context = SimpleNamespace(
            paths=SimpleNamespace(code_labels="labels", code_index="index", texmf="texmf", latex="latex"),
            config=SimpleNamespace(settings=object()),
            code_index_controller=SimpleNamespace(reload_code_index=Mock(return_value={"new": {}})),
            code_index_data={},
        )
        update_search = Mock()
        load_data = Mock()
        window = cast(MainWindow, SimpleNamespace(
            context=context, update_search=update_search,
            document_tab=SimpleNamespace(load_data=load_data),
        ))
        data_service = Mock(errors=3)
        database_service = Mock(database_errors=2)

        def build_index(*args, logger):
            logger("code")
            return 0

        with patch("assistant.gui.main_window.DiagnosticDialog", FakeDialog), \
             patch("assistant.gui.main_window.build_code_index", side_effect=build_index), \
             patch("assistant.gui.main_window.UpdateDataService", return_value=data_service) as data_class, \
             patch("assistant.gui.main_window.CheckDatabaseService", return_value=database_service) as database_class:
            MainWindow.update_code_index(window)
            MainWindow.update_data_index(window)
            MainWindow.check_database(window)

        self.assertIn("code", messages)
        self.assertEqual(context.code_index_data, {"new": {}})
        update_search.assert_called_once()
        load_data.assert_called_once()
        data_service.update_data_index.assert_called_once()
        database_service.check_database.assert_called_once()
        self.assertEqual(data_class.call_args.kwargs["logger"].__self__, messages)
        self.assertEqual(database_class.call_args.kwargs["logger"].__self__, messages)
        self.assertIn("3", results[1][1])
        self.assertIn("2", results[2][1])

        with patch("assistant.gui.main_window.DiagnosticDialog", FakeDialog), \
             patch("assistant.gui.main_window.build_code_index", return_value=1):
            MainWindow.update_code_index(window)
        self.assertFalse(results[-1][0])
        update_search.assert_called_once()


if __name__ == "__main__":
    unittest.main()
