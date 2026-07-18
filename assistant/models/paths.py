from pathlib import Path
from assistant.utils.resolve import resolve_path

class Paths:

    def __init__(self, config):

        for key, candidates in config.paths_candidates.items():
            try:
                resolved_path = resolve_path(candidates, config)
                setattr(self, f"{key}", resolved_path)
            except FileNotFoundError as e:
                print(f"Error occurred while resolving path for key '{key}': {e}")
                setattr(self, f"{key}", None)

        code_index_file_name = config.settings.current.code_index_file_name
        
        if not hasattr(self, "code_index") or self.code_index is None:
            self.code_index_file = Path.cwd() / code_index_file_name
        else:
            self.code_index_file = self.code_index / code_index_file_name
        
        data_index_file_name = config.settings.current.pdf_data_file_name
        
        if not hasattr(self, "data_index") or self.data_index is None:
            self.data_index_file = Path.cwd() / data_index_file_name
        else:
            self.data_index_file = self.data_index / data_index_file_name