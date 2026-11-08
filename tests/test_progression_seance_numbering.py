import io
import unittest
from types import SimpleNamespace

from PySide6.QtWidgets import QApplication, QLineEdit, QTreeWidget

from assistant.gui.panels.progression_panel import _MultilineDelegate
from assistant.services.export_service import ExportService
from assistant.services.progression_service import ProgressionService


class Catalogue:
    entries = []

    def get_entry_by_id(self, _entry_id):
        return None


class SeanceNumberingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.service = ProgressionService(None, Catalogue(), None, None)
        self.tree = QTreeWidget()
        self.level = self.service.make_item("Niveau")
        self.tree.addTopLevelItem(self.level)
        self.chapter = self.service.make_item("Chapitre")
        self.level.addChild(self.chapter)
        self.group = self.service.make_item("Séances")
        self.chapter.addChild(self.group)
        self.first = self.service.make_item("Découverte", "seance")
        self.second = self.service.make_item("Application", "seance")
        self.group.addChildren([self.first, self.second])

    def update_display(self):
        self.service.update_seance_displays(self.tree)
        self.service.update_chapter_numbers(self.tree)

    def test_level_displays_chapter_and_seance_totals(self):
        other_chapter = self.service.make_item("Autre chapitre")
        other_group = self.service.make_item("Séances")
        other_group.addChild(self.service.make_item("Bilan", "seance"))
        other_chapter.addChild(other_group)
        self.level.addChild(other_chapter)

        self.service.update_level_displays(self.tree)
        self.service.update_level_displays(self.tree)

        self.assertEqual(
            self.level.text(0),
            "Niveau (2 chapitres | 3 séances)",
        )
        self.assertEqual(self.service._get_raw_text(self.level), "Niveau")

    def test_numbering_is_per_group_and_updates_after_reordering(self):
        other_chapter = self.service.make_item("Autre chapitre")
        self.level.addChild(other_chapter)
        other_group = self.service.make_item("Séances")
        other_chapter.addChild(other_group)
        other = self.service.make_item("Bilan", "seance")
        other_group.addChild(other)
        other_item = self.service.make_item("Autre élément", "prerequis")
        other_group.addChild(other_item)

        self.update_display()
        self.update_display()
        self.assertEqual(self.group.text(0), "Séances (2)")
        self.assertEqual(self.first.text(0), "1. Découverte")
        self.assertEqual(self.second.text(0), "2. Application")
        self.assertEqual(other.text(0), "1. Bilan")
        self.assertEqual(other_item.text(0), "Autre élément")

        self.tree.setCurrentItem(self.second)
        self.service.move_item(self.tree, -1)
        self.update_display()
        self.assertEqual(self.second.text(0), "1. Application")
        self.assertEqual(self.first.text(0), "2. Découverte")
        self.service.delete_item(self.tree)
        self.update_display()
        self.assertEqual(self.first.text(0), "1. Découverte")
        self.assertEqual(self.group.text(0), "Séances (1)")

    def test_edit_snapshot_restore_and_export_use_raw_text(self):
        self.update_display()
        delegate = _MultilineDelegate(self.tree, self.service._get_raw_text)
        editor = QLineEdit()
        delegate.setEditorData(editor, self.tree.indexFromItem(self.first))
        self.assertEqual(editor.text(), "Découverte")

        self.first.setText(0, "Renommée")
        self.update_display()
        self.assertEqual(self.first.text(0), "1. Renommée")
        data = self.service.snapshot(self.tree)
        seances = data[0]["children"][0]["children"][0]["children"]
        self.assertEqual([item["text"] for item in seances], ["Renommée", "Application"])

        labels = {
            code: SimpleNamespace(name=name)
            for code, name in [
                ("aut", "Automatismes"),
                ("obj", "Objectifs"),
                ("pro", "Prolongements"),
                ("sea", "Séances"),
                ("prq", "Prérequis"),
            ]
        }
        output = io.StringIO()
        ExportService(labels).export_sequence(data[0]["children"][0], output)
        self.assertIn("\\seance{Renommée}\n", output.getvalue())
        self.assertNotIn("\\seance{1. Renommée}", output.getvalue())

        self.service.restore(self.tree, data)
        self.update_display()
        level = self.tree.topLevelItem(0)
        assert level is not None
        restored = level.child(0).child(0)
        self.assertEqual(restored.child(0).text(0), "1. Renommée")
        self.assertEqual(restored.child(1).text(0), "2. Application")

    def test_detailed_mode_preserves_numbered_seances(self):
        self.update_display()
        self.service.toggle_detailed_mode(self.tree)
        self.assertEqual(self.first.text(0), "1. Découverte")
        self.service.refresh_detailed_mode(self.tree)
        self.service.toggle_detailed_mode(self.tree)
        self.assertEqual(self.second.text(0), "2. Application")


if __name__ == "__main__":
    unittest.main()
