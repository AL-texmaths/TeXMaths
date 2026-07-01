# models/entry.py
from dataclasses import dataclass

@dataclass(frozen=True)
class Entry:
    catalogue: str
    type: str
    code: str
    text: str

@dataclass(frozen=True)
class Catalogue:
    key: str = ""
    name: str = ""
    tex_file_name: str = ""
    sty_file_name: str = ""
    childs: tuple = ()
    data: dict = None
