import unittest

from assistant.models.config import CatalogueMetadata
from assistant.services.catalogue_service import CatalogueService


class CatalogueSearchTests(unittest.TestCase):
    def setUp(self):
        self.service = CatalogueService(
            {
                "z": {"cours": {"b": "commun", "a": "autre"}},
                "a": {
                    "exercice": {"b": "commun", "a": "commun"},
                    "cours": {"c": "commun"},
                },
            },
            {
                "z": CatalogueMetadata(name="Premier", tex_file_name="", sty_file_name=""),
                "a": CatalogueMetadata(name="Second", tex_file_name="", sty_file_name=""),
            },
        )

    def test_all_catalogues_sorted_by_key_type_and_code(self):
        self.assertEqual(
            [entry.id for entry in self.service.search()],
            ["a:cours:c", "a:exercice:a", "a:exercice:b", "z:cours:a", "z:cours:b"],
        )

    def test_catalogue_type_and_text_filters_keep_working(self):
        catalogue = self.service.get_catalogue("a")
        self.assertEqual(
            [entry.id for entry in self.service.search(
                catalogue=catalogue, source_type="exercice", regex_text="commun"
            )],
            ["a:exercice:a", "a:exercice:b"],
        )
        self.assertEqual(
            [entry.id for entry in self.service.search(source_type="cours", regex_text="commun")],
            ["a:cours:c", "z:cours:b"],
        )


if __name__ == "__main__":
    unittest.main()
