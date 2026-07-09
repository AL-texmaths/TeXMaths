import os
import subprocess


class LatexService:
    def __init__(self, context):
        self.context = context
        self.types_dict = self.context.config.settings.pedago_service.pedago_doc_types

    def get_types_keys(self):
        return list(self.types_dict.keys())

    def latexmk_all_tex_files(self):
        for _type in self.types_dict.values():
             self.latexmk_all_tex_files_for_type(_type)
    
    def latexmk_all_tex_files_for_type(self, _type):
            base_name = _type.tex_name
            cwd = str(self.context.paths.latex / _type.dir_name)
            result = subprocess.Popen(
                [
                    "latexmk",
                    "-lualatex",
                    "-interaction=nonstopmode",
                    "-file-line-error",
                    "-shell-escape",
                    "-recorder",
                    "-synctex=1",
                    base_name
                    ],
                cwd=cwd,
                # stdout=subprocess.PIPE,
                # stderr=subprocess.STDOUT,
                text=True)
            print(result.stdout)
            return result