import contextlib
import io
import runpy
import subprocess
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pypdf


class ExportExempleTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.examples = self.root / "exemples"
        self.examples.mkdir()
        self.tex = self.examples / "6e-Ch5-cours_exemple_1.tex"
        self.tex.write_text("%scale[1]\n", encoding="utf-8")
        self.output = self.root / "6e-Ch5-cours_exemple_1.pdf"
        (self.root / "6e-Ch5-cours.pdf").touch()

    def run_export(self, result, create_pdf=False):
        def compile_example(path, cmd_args):
            self.assertIn("-shell-escape", cmd_args)
            if create_pdf:
                writer = pypdf.PdfWriter()
                writer.add_blank_page(width=100, height=100)
                writer.write(path.with_suffix(".pdf"))
            return result

        with (
            patch("src.tools.LATEX_DIR", self.root),
            patch("src.tools.get_cours_file_path", return_value=self.output),
            patch("src.tools.get_last_run_date", return_value=datetime(2000, 1, 1)),
            patch("src.tools.update_last_run_date") as update_date,
            patch("src.tools.compile_latex", side_effect=compile_example),
            contextlib.redirect_stdout(io.StringIO()) as stdout,
        ):
            try:
                runpy.run_module("src.export_exemple", run_name="__main__")
            except SystemExit as error:
                return error.code, stdout.getvalue(), update_date.called
            return 0, stdout.getvalue(), update_date.called

    def test_success_exports_pdf_and_updates_date(self):
        code, _, updated = self.run_export(
            subprocess.CompletedProcess([], 0, "", ""), create_pdf=True
        )
        self.assertEqual(code, 0)
        self.assertTrue(self.output.is_file())
        self.assertTrue(updated)

    def test_compile_failure_does_not_export_stale_pdf_or_update_date(self):
        self.tex.with_suffix(".pdf").write_bytes(b"stale PDF")
        code, output, updated = self.run_export(
            subprocess.CompletedProcess([], 1, "Python failed", "details")
        )
        self.assertEqual(code, 1)
        self.assertIn("Python failed", output)
        self.assertIn("details", output)
        self.assertFalse(self.output.exists())
        self.assertFalse(updated)


if __name__ == "__main__":
    unittest.main()
