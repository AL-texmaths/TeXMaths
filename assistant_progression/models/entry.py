# models/entry.py
from assistant_progression.models.catalogue import Catalogue


class Entry:

    def __init__(
            self,
            code: str,
            text: str,
            catalogue:Catalogue,
            type: str="",
            locations: str = "",
            ):
        self.catalogue = catalogue
        self.type = type
        self.code = code
        self.text = text
        self.locations = locations
        self.id = ":".join([self.catalogue.key, self.type, self.code])

    def __repr__(self):
        return f'Entry({self.id})'
    
    def __eq__(self, other):
        if not isinstance(other, Entry):
            return NotImplemented
        return self.id == other.id