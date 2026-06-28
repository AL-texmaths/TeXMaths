import re
from src.tools import CONFIG, LATEX_DIR, compile_latex, get_pattern
"""
Analyse la base de données et affiche les erreurs.
"""
DOC_TYPES = CONFIG['parameters']['index documents']
STRING_CHECK_ORDER = CONFIG['parameters']['string check order']
IGNORED_EXT = CONFIG['parameters']['ignored extensions']

def show_warnings_latex(log_path, logger=print):
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
        logger(f"\n=== LaTeX Warnings ===\n{log_path}")
        for w in warnings:
            logger(w.strip())
            logger("-" * 60)
            latex_warnings += 1
    return latex_warnings


def check_name(doc_type, doc_type_dict, logger=print):

    result = []
    dir_path = LATEX_DIR / doc_type_dict["folder name"]
    pattern = doc_type + doc_type_dict["name pattern"]
    for file_path in dir_path.glob('*'):
        if file_path.is_file():
            if file_path.suffix in IGNORED_EXT:
                continue
            matches = re.findall(pattern, str(file_path))
            if not matches:
                if file_path.suffix == '.tex':
                    logger('='*len(str(file_path)))
                    logger(str(file_path))
                    logger('='*len(str(file_path)))
                else:
                    logger(str(file_path))
                result.append(file_path)
    return result

def show_non_matches(unlink=False, logger=print):
    path_to_unlink = []
    path_to_unlink_tex = []

    show_uncorrect = False
    for doc_type, doc_type_dict in DOC_TYPES.items():
        for file_path in check_name(doc_type, doc_type_dict, logger=logger):
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

def check_database(logger=print):
    """
    """
    logger('Checking database ...')
    show_non_matches(unlink=False, logger=logger)
    database_errors = 0
    latex_warnings = 0

    def warn(message):
        nonlocal database_errors
        logger(message)
        database_errors += 1
    
    for doc_type, doc_dict in DOC_TYPES.items():
        base_dir = LATEX_DIR / doc_dict['folder name']
        pattern = get_pattern(doc_type, 'tex').replace('(data|[a-z])', 'data')
    
        for file_name in base_dir.iterdir():
            file_path = base_dir / file_name
    
            if re.findall(pattern, str(file_name)):

                with open(base_dir / file_name, 'r', encoding='utf8') as texfile:
                    tex_data = texfile.read()
                    nextdata = tex_data

                    for string_test in STRING_CHECK_ORDER:
                        index = nextdata.find(string_test)

                        if index == -1:
                            if string_test in tex_data:
                                warn(f"\n=== Wrong order {string_test} ===\n{file_name}") 
                            else:
                                warn(f"\n=== Missing {string_test} ===\n{file_name}")      
                        else:
                            nextdata = nextdata[index + len(string_test):]

                pdf_path = file_path.with_suffix('.pdf')
                if not pdf_path.exists():
                    warn(f"\n=== Missing pdf ===\n{pdf_path}.")
                    logger(f"Trying to compile the LaTeX file {file_path}.")
                    compile_result = compile_latex(file_path, motor='lualatex', silent=False)
                    if compile_result.returncode != 0:
                        warn(f"\n=== Compilation failed ===\n{file_path}\nPlease check the LaTeX file.")
                    else:
                        logger(f"Compilation of {file_path} succeeded.")
                        database_errors -=1
                else:
                    log_path = file_path.with_suffix('.log')
                    if log_path.exists():
                        latex_warnings += show_warnings_latex(log_path, logger=logger)
    return database_errors, latex_warnings

if __name__ == "__main__":
    check_database()
    # show_non_matches(unlink=True)
    