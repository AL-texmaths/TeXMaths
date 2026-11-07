import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class SortGlossaryTests(unittest.TestCase):
    def test_sorts_words_without_accents_or_case(self):
        words = [
            "Expliquer",
            "Évaluer",
            "Encadrer",
            "Développer",
            "Décomposer",
            "e\u0301valuer",
            "Evaluer",
            "Factoriser",
        ]
        with tempfile.TemporaryDirectory() as directory:
            wordlist = Path(directory) / "wordlist.txt"
            sortedindex = Path(directory) / "sortedindex.txt"
            wordlist.write_text("[\n" + "\n".join(words) + "\n]\n", encoding="utf-8")

            subprocess.run(
                [sys.executable, "-m", "src.sort_glossary", str(wordlist), str(sortedindex)],
                cwd=ROOT,
                check=True,
            )

            self.assertEqual(sortedindex.read_text(encoding="utf-8"), "4,3,2,1,5,6,0,7%")

if __name__ == "__main__":
    unittest.main()
