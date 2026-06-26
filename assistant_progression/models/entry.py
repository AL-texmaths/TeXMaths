# models/entry.py
from dataclasses import dataclass, field

@dataclass(frozen=True)
class Entry:
    catalogue: str
    type: str
    code: str
    text: str
