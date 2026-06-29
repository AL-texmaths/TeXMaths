from dataclasses import dataclass

@dataclass
class SearchFilters:
    pattern: str
    active_prefixes: list[str]
    active_fields: list[str]
    empty_fields: list[str]
    sort_mode: int