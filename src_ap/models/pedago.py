from typing import Any
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class PedagoDoc:
    type: str
    id: str
    tex: Path
    pdf: Path
    enonce: str

    preview: str | None = None
    source: str | None = None
    BO: str | None = None
    cycle: str | None = None

    competencesDuSocle: list[str] | None = None
    connaissancesRequises: list[str] | None = None
    competencesTravaillees: list[str] | None = None
    automatismes: list[str] | None = None
    objectifsApprentissage: list[str] | None = None
    prolongements: list[str] | None = None

    motsCles: str | None = None

    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        # normalize paths
        if isinstance(self.tex, (str, Path)) and self.tex != "":
            self.tex = Path(self.tex)
        if isinstance(self.pdf, (str, Path)) and self.pdf != "":
            self.pdf = Path(self.pdf)

        # normalize empty strings to None for optional fields
        for name, value in list(self.__dict__.items()):
            if name in ("tex", "pdf"):
                continue
            if value == "":
                setattr(self, name, None)
            if isinstance(value, list) and "" in value:
                print(f'WARNING: Empty string in list for field {name} in PedagoDoc {self.type} {self.id}')