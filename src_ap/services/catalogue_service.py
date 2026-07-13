# catalogue_service.py
import re
import subprocess
from pathlib import Path
from src_ap.models.entry import Entry
from src_ap.models.catalogue import Catalogue, ALL_CATALOGUES
from src_ap.utils.resolve import resolve_executable
from src_ap.utils.textools import latex_text_to_unicode
from src_ap.models.config import Config


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
        self.catalogues = {ALL_CATALOGUES.key: ALL_CATALOGUES}

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
        
        print(f"Opening package {sty_file_name} at {package_path} with {resolve_executable("blocnote", config)}")
        
        subprocess.run([resolve_executable("blocnote", config), str(package_path)])

    def build_index(self):

        self.entries = []

        for catalogue in self.catalogues.values():

            catalogue_data = catalogue.data

            if all(
                isinstance(v, str)
                for v in catalogue_data.values()
            ):

                for code, text in catalogue_data.items():

                    entry = Entry(
                            code=code,
                            text=latex_text_to_unicode(text),
                            catalogue=catalogue,
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
                                code=code,
                                text=latex_text_to_unicode(text),
                                catalogue=catalogue,
                                type=source_type,
                            )
                        )

    def search(
        self,
        catalogue: Catalogue = ALL_CATALOGUES,
        source_type="Tous",
        regex_text=""
    ):
        entries = self.entries

        # Filtre catalogue
        if catalogue != ALL_CATALOGUES:

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
    
    def get_entry_by_id(self, id):
        for entry in self.entries:
            if entry.id == id:
                return entry
        return None
