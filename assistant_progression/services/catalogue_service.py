# catalogue_service.py
import re
import subprocess
from pathlib import Path
from assistant_progression.models.entry import Entry, Catalogue
from assistant_progression.utils.resolve import resolve_executable
from assistant_progression.models.config import Config


class CatalogueService:

    def __init__(self, code_index_data: dict, catalogues_config: dict):
        self.code_index_data = code_index_data
        self.catalogues_config = catalogues_config
        self.entries = []
        self.refresh()
    
    def refresh(self):
        self.build_catalogues()
        self.build_index()

    def build_catalogues(self):
        self.catalogues = {Catalogue.ALL: Catalogue()}

        for catalogue_key, catalogue_metadata in self.catalogues_config.items():
            catalogue = Catalogue(
                key=catalogue_key,
                data=self.code_index_data.get(catalogue_key, {}),
                **catalogue_metadata.model_dump()
                )
            
            self.catalogues[catalogue_key] = catalogue

    def get_catalogue(self, key:str) -> dict:
        return self.catalogues.get(key, {})
    
    def get_catalogue_from_name(self, name: str) -> Catalogue:
        for catalogue in self.catalogues.values():
            if catalogue.name == name:
                return catalogue
        return Catalogue()
    
    def get_catalogue_names(self) -> list:
        return sorted(
            [catalogue.name for catalogue in self.catalogues.values()]
        )
    
    def open_catalogue_package(self, name: str, texmf_dir: Path, config:Config):

        catalogue = self.get_catalogue_from_name(name)
        if not catalogue:
            print(f"Catalogue '{name}' not found.")
            return

        sty_file_name = catalogue.sty_file_name
        package_path = next(texmf_dir.rglob(sty_file_name), None)

        if package_path is None:
            print(f"Fichier introuvable {sty_file_name} dans {texmf_dir}")
        else:
            print(f"Analysing package {sty_file_name} at {package_path}")
        
        subprocess.run([resolve_executable("blocnote", config), str(package_path)])

    def build_index(self):

        self.entries = []

        for catalogue in self.catalogues.values():

            catalogue_data = catalogue.data

            if catalogue.data is None:
                continue

            if all(
                isinstance(v, str)
                for v in catalogue_data.values()
            ):

                for code, text in catalogue_data.items():

                    entry = Entry(
                            catalogue=catalogue.name,
                            type="",
                            code=code,
                            text=text
                        )
                    self.entries.append(entry)

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
                                catalogue=catalogue.name,
                                type=source_type,
                                code=code,
                                text=text
                            )
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
        catalogue_name="Tous",
        source_type="Tous",
        regex_text=""
    ):
        entries = self.entries

        # Filtre catalogue
        if catalogue_name != "Tous":

            entries = [
                e
                for e in entries
                if e.catalogue == catalogue_name
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
    
    def get_entry_by_code(self, code):
        for entry in self.entries:
            if entry.code == code:
                return entry
        return None
