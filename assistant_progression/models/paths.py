from pathlib import Path
from assistant_progression.utils.resolve import resolve_path

class Paths:

    def __init__(self, config):

        for key, candidates in config.paths_candidates.items():
            try:
                resolved_path = resolve_path(candidates, config)
                setattr(self, f"{key}", resolved_path)
                print(f"Resolved path for key '{key}': {resolved_path}")
            except FileNotFoundError as e:
                print(f"Error occurred while resolving path for key '{key}': {e}")

        code_index_file_name = config.settings.current.code_index_file_name
        
        if not hasattr(self, "code_index"):
            self.code_index_file = Path.cwd() / code_index_file_name
        else:
            self.code_index_file = self.code_index / code_index_file_name