# models/entry.py
from dataclasses import dataclass

@dataclass(frozen=True)
class Entry:
    catalogue: str
    type: str
    code: str
    text: str
    locations: str = ""
@dataclass(frozen=True)
class Catalogue:
    ALL: str = "Tous"
    key: str = ALL
    name: str = ALL
    tex_file_name: str = ""
    sty_file_name: str = ""
    types: tuple = ()
    data: dict = None
