import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QListWidget, QPushButton, QWidget

from assistant.gui.tabs.document_tab import DocumentTab
from assistant.gui.widgets.pdf_filters import PDFFiltersButton
from assistant.models.config import Config, DocumentTabGUIModel, PDFFiltersModel
from assistant.models.search_filters import SearchFilters
from assistant.services.search_pdf_service import SearchPDFService
from assistant.services.persistence_service import PersistenceService


class PDFFilterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.filters = PDFFiltersModel()
        self.button = PDFFiltersButton(self.filters)
        self.button.set_items(["cours", "exercice"], ["titre", "mots"])

    def test_select_only_multiple_empty_and_reset(self):
        self.button.types.select_only("cours")
        self.assertEqual(self.button.types.checked_items(), ["cours"])
        self.assertEqual(self.button.fields.checked_items(), ["titre", "mots"])
        self.assertIn("cours", self.button.toolTip())
        self.assertIn("•", self.button.text())

        self.button.types.checkboxes["exercice"].setChecked(True)
        self.assertEqual(self.button.types.checked_items(), ["cours", "exercice"])
        self.button.fields.select_none()
        self.assertEqual(self.button.empty_selection_message(), "Aucun champ sélectionné")
        self.button.reset_filters()
        self.assertTrue(self.filters.types.all_selected)
        self.assertTrue(self.filters.fields.all_selected)
        self.assertEqual(self.button.text(), "Filtres")

    def test_saved_selection_survives_reload_missing_and_new_items(self):
        self.button.types.select_only("cours")
        saved = self.filters.model_dump_json()
        restored = PDFFiltersModel.model_validate_json(saved)
        button = PDFFiltersButton(restored)
        button.set_items(["exercice", "nouveau"], ["titre", "nouveau"])
        self.assertEqual(button.types.checked_items(), [])
        self.assertEqual(button.fields.checked_items(), ["titre", "nouveau"])
        button.types.checkboxes["exercice"].setChecked(True)
        button.set_items(["cours", "exercice", "nouveau"], ["titre"])
        self.assertEqual(button.types.checked_items(), ["cours", "exercice"])
        self.assertEqual(restored.types.selected, ["cours", "exercice"])
        button.deleteLater()

    def test_old_configuration_and_empty_selection_round_trip(self):
        old = DocumentTabGUIModel.model_validate(
            {"vertical_splitter": 100, "horizontal_splitter": 200}
        )
        self.assertTrue(old.pdf_filters.types.all_selected)
        self.assertTrue(old.pdf_filters.fields.all_selected)
        self.button.types.select_none()
        restored = PDFFiltersModel.model_validate_json(self.filters.model_dump_json())
        self.assertFalse(restored.types.all_selected)
        self.assertEqual(restored.types.selected, [])

    def test_popup_stays_open_for_clicks(self):
        self.button.show()
        self.button.menu().popup(self.button.mapToGlobal(self.button.rect().bottomLeft()))
        self.app.processEvents()
        only = next(
            button for button in self.button.types.findChildren(QPushButton)
            if button.accessibleName() == "Sélectionner uniquement cours"
        )
        QTest.mouseClick(only, Qt.LeftButton)
        self.assertTrue(self.button.menu().isVisible())
        self.assertEqual(self.button.types.checked_items(), ["cours"])
        QTest.mouseClick(self.button.types.checkboxes["exercice"], Qt.LeftButton)
        self.assertTrue(self.button.menu().isVisible())
        self.assertEqual(self.button.types.checked_items(), ["cours", "exercice"])
        self.button.menu().close()

    def test_long_lists_scroll_in_bounded_popup(self):
        names = [f"élément {index}" for index in range(100)]
        self.button.set_items(names, names)
        self.button.show()
        self.button.menu().popup(self.button.mapToGlobal(self.button.rect().bottomLeft()))
        self.app.processEvents()
        for section in (self.button.types, self.button.fields):
            self.assertLessEqual(section.scroll_area.height(), 150)
            self.assertGreater(section.scroll_area.verticalScrollBar().maximum(), 0)
        self.button.menu().close()

    def tearDown(self):
        self.button.close()
        self.button.deleteLater()


class PDFSearchIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_empty_fields_never_match_even_empty_regex_match(self):
        data = SimpleNamespace(data={"doc": SimpleNamespace(type="cours", titre="abc")})
        service = SearchPDFService(data)
        filters = SearchFilters("^$", ["cours"], [], 0)
        self.assertEqual(service.search(filters), [])

    def test_document_tab_updates_and_debounces_persistence(self):
        config_path = Path("assistant") / "default_data" / "config.json"
        config = Config.model_validate(json.loads(config_path.read_text(encoding="utf-8")))
        documents = {
            "cours-1": SimpleNamespace(type="cours", titre="algèbre"),
            "exercice-1": SimpleNamespace(type="exercice", titre="algèbre"),
        }
        data = SimpleNamespace(
            data=documents, refresh=lambda: None,
            get_types=lambda: ["cours", "exercice"],
            get_fields=lambda: ["titre"],
        )
        saved = []
        context = SimpleNamespace(
            config=config,
            pedago_data_service=data,
            search_pdf_service=SearchPDFService(data),
            persistence_service=SimpleNamespace(
                save_config=lambda value: saved.append(value.model_dump())
            ),
        )

        class FakeViewer:
            def __init__(self):
                self.view = QWidget()

        class FakeResults(QListWidget):
            def __init__(self, *_args):
                super().__init__()

        with patch("assistant.gui.tabs.document_tab.PdfViewerWidget", FakeViewer), \
             patch("assistant.gui.tabs.document_tab.MetadataView", lambda _context: QWidget()), \
             patch("assistant.gui.tabs.document_tab.ResultsList", FakeResults):
            tab = DocumentTab(context)
            tab.load_data()
            tab.sort_order_combo.setCurrentIndex(0)
            tab.search_input.setText("algèbre")
            tab.update_results()
            self.assertEqual(tab.results_list.count(), 2)
            tab.pdf_filters.types.select_only("cours")
            self.assertEqual(tab.results_list.count(), 1)
            tab.pdf_filters.fields.select_none()
            self.assertEqual(tab.results_list.count(), 0)
            self.assertIn("Aucun champ", tab.filter_status.text())
            QTest.qWait(650)
            self.assertEqual(len(saved), 1)
            persisted = saved[0]["settings"]["gui"]["documents_tab"]["pdf_filters"]
            self.assertEqual(persisted["types"]["selected"], ["cours"])
            self.assertEqual(persisted["fields"], {"all_selected": False, "selected": []})
            tab.pdf_filters.fields.select_all()
            tab.flush_pending_filter_save()
            self.assertEqual(len(saved), 2)
            self.assertTrue(saved[-1]["settings"]["gui"]["documents_tab"]
                            ["pdf_filters"]["fields"]["all_selected"])
            tab.pdf_filters.types.select_none()
            tab.cancel_pending_filter_save()
            config.settings.gui.documents_tab.pdf_filters = PDFFiltersModel()
            tab.restore_filter_settings()
            self.assertEqual(tab.results_list.count(), 2)
            self.assertFalse(tab._save_filter_settings_timer.isActive())
            tab.close()
            tab.deleteLater()

    def test_persistence_service_round_trip(self):
        config_path = Path("assistant") / "default_data" / "config.json"
        config = Config.model_validate(json.loads(config_path.read_text(encoding="utf-8")))
        config.settings.gui.documents_tab.pdf_filters.types.all_selected = False
        config.settings.gui.documents_tab.pdf_filters.types.selected = ["cours", "absent"]
        config.settings.gui.documents_tab.pdf_filters.fields.all_selected = False
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            with patch("assistant.services.persistence_service.USR_CONFIG_PATH", path):
                PersistenceService.save_config(config)
                restored = PersistenceService.load_config()
        filters = restored.settings.gui.documents_tab.pdf_filters
        self.assertEqual(filters.types.selected, ["cours", "absent"])
        self.assertFalse(filters.fields.all_selected)
        self.assertEqual(filters.fields.selected, [])


if __name__ == "__main__":
    unittest.main()
