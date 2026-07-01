from pathlib import Path
from assistant_progression.utils.resolve import resolve_path

class Paths:

    def __init__(self, config):

        for key, candidates in config.paths_candidates.items():
            resolved_path = resolve_path(candidates, config)
            setattr(self, f"{key}", resolved_path)
        
        if not hasattr(self, "code_index"):
            self.code_index_file = Path.cwd() / "code_index.json"
        else:
            self.code_index_file = self.code_index / "code_index.json"