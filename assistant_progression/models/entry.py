# models/entry.py
from dataclasses import dataclass

@dataclass(frozen=True)
class Entry:
    catalogue: str
    type: str
    code: str
    text: str
