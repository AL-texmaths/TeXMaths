import os
import glob
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
            cwd = str(self.context.paths.latex / _type.dir_name)
            tex_files = glob.glob(os.path.join(cwd, _type.tex_name))
            if not tex_files:
                print(f"No files matching '{_type.tex_name}' in {cwd}")
                return None
            results = []
            for tex_file in tex_files:
                base_name = os.path.basename(tex_file)
                print(f"Compiling {base_name} in {cwd} using latexmk...")
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
                    text=True)
                results.append(result)
            return results