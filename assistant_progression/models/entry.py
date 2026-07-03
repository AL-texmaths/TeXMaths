# models/entry.py
from dataclasses import dataclass

@dataclass(frozen=True)
class Entry:
    catalogue: str
    type: str
    code: str
    text: str
    locations: str = ""

    @property
    def tree_code(self):
        return ':'.join([self.catalogue, self.type, self.code])

@dataclass(frozen=True)
class Catalogue:
    ALL: str = "Tous"
    key: str = ALL
    name: str = ALL
    tex_file_name: str = ""
    sty_file_name: str = ""
    types: tuple = ()
    data: dict = None
