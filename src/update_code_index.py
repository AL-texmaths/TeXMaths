"""
Ce script est activé lors de la compilation pdflatex
 du fichier data/latex/catalogues/update_code_index.tex.
Ce script permet de rendre plus lisible le fichier en remplacant
le fichier initialement code_index_tmp.json écrit lors de la compilation par
un fichier plus lisible code_index.json.
"""
import json
from src.tools import LATEX_DIR, compile_latex

print('BONJOUR')

TEX_FILE_NAME = LATEX_DIR / "catalogues" / 'update_code_index.tex'
TEX_FILE_DIR_PATH = TEX_FILE_NAME.parent
BO_2026_TEX_PATH = LATEX_DIR / "codes_cnscmpsrc" / 'BO_2026.tex'
BO_2026_FILE_NAMES = ["BO_2026-cycle4", "BO_2026-cycle3"]

SEP = '|:|'
BO_KEY = ["cycle 4 BO 2026", "cycle 3 BO 2026"]

def update_code_index(logger=print):
    logger('Looking for data.txt files ...')

    result = compile_latex(TEX_FILE_NAME, motor='lualatex')
    print(result)
    # remplacement du fichier json pour une meilleur lisibilité
    input_path = TEX_FILE_DIR_PATH / 'code_index_tmp.json'
    output_path = TEX_FILE_DIR_PATH / 'code_index.json'
    with open(input_path, 'r', encoding='utf-8') as infile:
        data = json.load(infile)
    with open(output_path, 'w', encoding='utf-8') as outfile:
        json.dump(data, outfile, indent=4, ensure_ascii=False)
    input_path.unlink()
    # extracting data from the BO_2026-cycle4-data.txt file
    for Bo_Key, Bo_file_name in zip(BO_KEY, BO_2026_FILE_NAMES):
        Data = {Bo_Key :
                {
                    "aut": {},
                    "obj": {},
                    "pro": {}
                }
        }
        file_path = LATEX_DIR / "codes_cnscmpsrc" / (Bo_file_name + '-data.txt')
        if not file_path.exists():
            print(f"File {file_path} does not exist. Trying to compile the LaTeX file {BO_2026_TEX_PATH}.")
            result = compile_latex(BO_2026_TEX_PATH, motor='lualatex')
            if result.returncode != 0:
                print(f"File {file_path} does not exist. Please check the path.")
                continue

        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                item_type, key, value = line.strip().split(SEP)
                Data[Bo_Key][item_type][key] = value
        # updating the code index json file with the new data
        with open(LATEX_DIR / "catalogues" / "code_index.json", "r", encoding="utf-8") as f:
            code_index_data = json.load(f)

        code_index_data[Bo_Key] = Data[Bo_Key]
        with open(LATEX_DIR / "catalogues" / "code_index.json", "w", encoding="utf-8") as f:
            json.dump(code_index_data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    update_code_index()
    print(f'module {__file__} ok')