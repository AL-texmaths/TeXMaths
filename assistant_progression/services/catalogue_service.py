import re

from assistant_progression.models.entry import Entry
from assistant_progression.utils.textools import compile_latex, resolve_path

class CatalogueService:

    def __init__(self, data, code_labels):

        self.data = data
        self.code_labels = code_labels

        self.entries = []

        self.build_index()

    def display_name(self, code):

        return self.code_labels.get(
            code,
            code
        )

    def internal_name(self, display):

        for code, label in self.code_labels.items():

            if label == display:
                return code

        return display

    def build_index(self):

        self.entries.clear()

        for catalogue, catalogue_data in self.data.items():

            if not isinstance(
                catalogue_data,
                dict
            ):
                continue

            # structure plate
            if all(
                isinstance(v, str)
                for v in catalogue_data.values()
            ):

                for code, text in catalogue_data.items():

                    self.entries.append(
                        Entry(
                            catalogue=catalogue,
                            type=catalogue,
                            code=code,
                            text=text
                        )
                    )

            else:

                for source_type, source_data in catalogue_data.items():

                    if not isinstance(
                        source_data,
                        dict
                    ):
                        continue

                    for code, text in source_data.items():

                        self.entries.append(
                            Entry(
                                catalogue=catalogue,
                                type=source_type,
                                code=code,
                                text=text
                            )
                        )
    
    def code_label(self, code: str) -> str:
        return self.code_labels.get(code, code)

    @property
    def labels(self):
        return self.code_labels

    def get_catalogues(self):

        return sorted(
            self.data.keys()
        )

    def get_types(
        self,
        catalogue
    ):

        types = set()

        for entry in self.entries:

            if (
                catalogue == "Tous"
                or entry.catalogue == catalogue
            ):
                types.add(entry.type)

        return sorted(types)

    def search(
        self,
        catalogue="Tous",
        source_type="Tous",
        regex_text=""
    ):

        entries = self.entries

        # Filtre catalogue
        if catalogue != "Tous":

            entries = [
                e
                for e in entries
                if e.catalogue == catalogue
            ]

        # Filtre type
        if source_type != "Tous":

            entries = [
                e
                for e in entries
                if e.type == source_type
            ]

        # Recherche
        if regex_text:

            code_match = re.search(
                r"code:(\S+)",
                regex_text,
                re.IGNORECASE
            )

            text_match = re.search(
                r"text:(.+?)(?=\s+\w+:|$)",
                regex_text,
                re.IGNORECASE
            )

            # Recherche ciblée sur le code
            if code_match:

                code_regex = re.compile(
                    code_match.group(1),
                    re.IGNORECASE
                )

                entries = [
                    e
                    for e in entries
                    if code_regex.search(e.code)
                ]

            # Recherche ciblée sur le texte
            if text_match:

                text_regex = re.compile(
                    text_match.group(1).strip(),
                    re.IGNORECASE
                )

                entries = [
                    e
                    for e in entries
                    if text_regex.search(e.text)
                ]

            # Recherche classique si aucun filtre spécial
            if not code_match and not text_match:

                regex = re.compile(
                    regex_text,
                    re.IGNORECASE
                )

                entries = [
                    e
                    for e in entries
                    if (
                        regex.search(e.code)
                        or regex.search(e.text)
                    )
                ]

        return sorted(
            entries,
            key=lambda e: (
                e.catalogue,
                e.type,
                e.code
            )
        )

    def update_code_label(self):
        
        update_code_path = resolve_path("latex") / "catalogues" / "update_code_index.tex"
        compile_latex(update_code_path)