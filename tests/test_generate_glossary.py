import contextlib
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

from src.generate_glossary import generer_latex


ROOT = Path(__file__).resolve().parents[1]


class GenerateGlossaryTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.source = Path(self.directory.name) / "glossaire.yaml"
        self.destination = Path(self.directory.name) / "generated.tex"

    def write_words(self, words):
        self.source.write_text(
            yaml.safe_dump({"mots": words}, allow_unicode=True), encoding="utf-8"
        )

    def generate(self, niveau_maximal=None):
        with contextlib.redirect_stdout(io.StringIO()):
            generer_latex(self.source, self.destination, niveau_maximal=niveau_maximal)
        return self.destination.read_text(encoding="utf-8")

    def test_sorts_and_writes_only_two_arguments_per_line(self):
        self.write_words([
            {"nom": "Évaluer", "niveau": "3e", "definition_ecrite": "Premier\nsecond\n\nDernier\n"},
            {"nom": "Développer", "niveau": "4e", "definition_ecrite": r"Un \textbf{produit}."},
            {"nom": "Encadrer", "niveau": "6e", "definition_ecrite": "Deux bornes."},
        ])
        self.assertEqual(
            self.generate(),
            "\\writeword{Développer}{Un \\textbf{produit}.}%\n"
            "\\writeword{Encadrer}{Deux bornes.}%\n"
            "\\writeword{Évaluer}{Premier second\\par Dernier}%\n",
        )

    def test_filters_by_maximum_level_inclusively(self):
        self.write_words([
            {"nom": niveau, "niveau": niveau, "definition_ecrite": niveau}
            for niveau in ("6e", "5e", "4e", "3e")
        ])
        for maximum, expected in (
            ("6e", ("6e",)),
            ("5e", ("5e", "6e")),
            ("4e", ("4e", "5e", "6e")),
            ("3e", ("3e", "4e", "5e", "6e")),
        ):
            with self.subTest(maximum=maximum):
                self.assertEqual(
                    self.generate(maximum),
                    "".join(f"\\writeword{{{level}}}{{{level}}}%\n" for level in expected),
                )

    def test_invalid_level_is_reported_when_filtering(self):
        self.write_words([{"nom": "Mot", "niveau": "", "definition_ecrite": "Définition."}])
        with self.assertRaisesRegex(ValueError, "Niveau invalide"):
            self.generate("5e")
        with self.assertRaisesRegex(ValueError, "Niveau maximal invalide"):
            self.generate("2e")

    def test_command_line_with_default_destination_and_filter(self):
        self.write_words([
            {"nom": "A", "niveau": "6e", "definition_ecrite": "A"},
            {"nom": "B", "niveau": "5e", "definition_ecrite": "B"},
        ])
        result = subprocess.run(
            [sys.executable, "-m", "src.generate_glossary", "--niveau-maximal", "5e", str(self.source)],
            cwd=ROOT, capture_output=True, check=True,
        )
        self.assertIn(b"2 mots export", result.stdout)
        self.assertEqual(
            (self.source.parent / "glossaire-generated.tex").read_text(encoding="utf-8"),
            "\\writeword{A}{A}%\n\\writeword{B}{B}%\n",
        )


if __name__ == "__main__":
    unittest.main()
