from dataclasses import dataclass
from collections.abc import Callable


@dataclass(slots=True, frozen=True)
class ActionDefinition:
    id: str
    text: str
    shortcut: str
    slot: Callable
    icon: str | None = None
    checkable: bool = False