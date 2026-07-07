class Catalogue:
    def __init__(
            self,
            key: str,
            name: str,
            tex_file_name: str = "",
            sty_file_name: str = "",
            types: list = [],
            data: dict = {}
        ):
        self.key = key
        self.name = name
        self.tex_file_name = tex_file_name
        self.sty_file_name = sty_file_name
        self.types = types
        self.data  = data

    def __repr__(self):
        return f"Catalogue(key={self.key})"
    
    def __str__(self):
        return self.name

    def __eq__(self, other):
        if not isinstance(other, Catalogue):
            return NotImplemented
        return self.key == other.key

ALL_CATALOGUES = Catalogue("All", "Tous")