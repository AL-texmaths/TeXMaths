import re
from src_ap.app.application_context import create_context
from src_ap.utils.textools import get_pattern, compile_latex
"""
Analyse la base de données et affiche les erreurs.
"""


class CheckDatabaseService:
    def __init__(self, settings, latex_path, logger=print):
        self.settings = settings
        self.latex_path = latex_path
        self.logger = logger
        self.database_errors = 0
        self.latex_warnings = 0

        self.types_dict = settings.pedago_service.pedago_doc_types
        self.string_check_order = settings.pedago_service.string_check_order
        self.tex_non_optional_keys = settings.pedago_service.tex_non_optional_keys

    def warn(self, message):
        self.logger(message)
        self.database_errors += 1

    def show_warnings_latex(self, log_path):
        """
        Analyse un fichier .log LaTeX et affiche les warnings.
        Compatible encodage Windows (MiKTeX).
        """
        latex_warnings = 0
        # Lecture robuste (utf8 puis fallback cp1252)
        try:
            with open(log_path, "r", encoding="utf8") as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(log_path, "r", encoding="cp1252", errors="replace") as f:
                content = f.read()

        # Regex pour warnings LaTeX
        pattern = r"LaTeX Warning:.*?(?=\n\n|\Z)"

        warnings = re.findall(pattern, content, flags=re.DOTALL)

        if warnings:
            self.logger(f"\n=== LaTeX Warnings ===\n{log_path}")
            for w in warnings:
                self.logger(w.strip())
                self.logger("-" * 60)
                latex_warnings += 1
        return latex_warnings


    def check_name(self, doc_type):

        result = []
        dir_path = self.latex_path / self.types_dict[doc_type].dir_name
        pattern = doc_type + self.types_dict[doc_type].name_pattern
        for file_path in dir_path.glob('*'):
            if file_path.is_file():
                if file_path.suffix in self.tex_non_optional_keys:
                    continue
                matches = re.findall(pattern, str(file_path))
                if not matches:
                    if file_path.suffix == '.tex':
                        self.logger('='*len(str(file_path)))
                        self.logger(str(file_path))
                        self.logger('='*len(str(file_path)))
                    else:
                        self.logger(str(file_path))
                    result.append(file_path)
        return result

    def show_non_matches(self, unlink=False, logger=print):
        path_to_unlink = []
        path_to_unlink_tex = []

        show_uncorrect = False
        for doc_type in self.types_dict.keys():
            for file_path in self.check_name(doc_type):
                if show_uncorrect:
                    logger(f'\n=== Uncorrect files names ===')
                    show_uncorrect = False
                if file_path.suffix == '.tex':
                    path_to_unlink_tex.append(file_path)
                else:
                    path_to_unlink.append(file_path)

        if unlink:
            for pathes,extension in [(path_to_unlink, ''), (path_to_unlink_tex, 'LaTeX')]:
                if len(pathes) > 0:
                    while True:
                        answer = input(f'Voulez-vous supprimer tous ces fichiers ({extension})?')
                        if answer == 'O':
                            for file_path in pathes:
                                file_path.unlink()
                            break
                        if answer == 'N':
                            print('Aucun fichier supprimé')
                            break
                        print('La réponse doit être O ou N')

    def check_database(self):
        """
        """
        self.logger('Checking database ...')
        self.show_non_matches(unlink=False)
        database_errors = 0
        latex_warnings = 0
        
        for doc_type, doc_dict in self.types_dict.items():
            base_dir = self.latex_path / doc_dict.dir_name
            pattern = get_pattern(self.types_dict, doc_type, 'tex').replace('(data|[a-z])', 'data')
        
            for file_name in base_dir.iterdir():
                file_path = base_dir / file_name
        
                if re.findall(pattern, str(file_name)):
                    # print(f'Checking {base_dir / file_name} ...')

                    with open(base_dir / file_name, 'r', encoding='utf8') as texfile:
                        tex_data = texfile.read()
                        nextdata = tex_data

                        for string_test in self.string_check_order:
                            index = nextdata.find(string_test)

                            if index == -1:
                                if string_test in tex_data:
                                    self.warn(f"\n=== Wrong order {string_test} ===\n{file_name}") 
                                else:
                                    self.warn(f"\n=== Missing {string_test} ===\n{file_name}")      
                            else:
                                nextdata = nextdata[index + len(string_test):]

                    pdf_path = file_path.with_suffix('.pdf')
                    if not pdf_path.exists():
                        self.warn(f"\n=== Missing pdf ===\n{pdf_path}.")
                        self.logger(f"Trying to compile the LaTeX file {file_path}.")
                        compile_result = compile_latex(file_path, motor='lualatex', silent=False)
                        if compile_result.returncode != 0:
                            self.warn(f"\n=== Compilation failed ===\n{file_path}\nPlease check the LaTeX file.")
                        else:
                            self.logger(f"Compilation of {file_path} succeeded.")
                            database_errors -=1
                    else:
                        log_path = file_path.with_suffix('.log')
                        if log_path.exists():
                            latex_warnings += self.show_warnings_latex(log_path)
        return database_errors, latex_warnings

if __name__ == "__main__":
    context = create_context(None)
    check_database_service = CheckDatabaseService(context.config.settings, context.paths.latex)
    check_database_service.check_database()
    # show_non_matches(unlink=True)
    