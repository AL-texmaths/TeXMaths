from dataclasses import dataclass
from pathlib import Path

@dataclass
class Document:

    id: str

    pdf: Path
    preview: Path
    tex: Path

    type: str

    tags: list[str]

    metadata: dict