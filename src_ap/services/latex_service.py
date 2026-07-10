import os
import glob

from src_ap.services.latex_compilation_thread import LatexCompilationThread


class LatexService:
    def __init__(self, context):
        self.context = context
        self.types_dict = self.context.config.settings.pedago_service.pedago_doc_types
        self._compilation_thread = None

    def get_types_keys(self):
        return list(self.types_dict.keys())

    def _collect_tasks_for_type(self, _type):
        cwd = str(self.context.paths.latex / _type.dir_name)
        tex_files = glob.glob(os.path.join(cwd, _type.tex_name))
        if not tex_files:
            print(f"No files matching '{_type.tex_name}' in {cwd}")
            return []
        return [(tex_file, cwd) for tex_file in tex_files]

    def latexmk_all_tex_files(self):
        tasks = []
        for _type in self.types_dict.values():
            tasks.extend(self._collect_tasks_for_type(_type))
        return self._create_compilation_thread(tasks)

    def latexmk_all_tex_files_for_type(self, _type):
        tasks = self._collect_tasks_for_type(_type)
        return self._create_compilation_thread(tasks)

    def _create_compilation_thread(self, tasks):
        if not tasks:
            return None
        if self._compilation_thread is not None and self._compilation_thread.isRunning():
            print("A compilation is already in progress.")
            return None
        self._compilation_thread = LatexCompilationThread(tasks)
        return self._compilation_thread