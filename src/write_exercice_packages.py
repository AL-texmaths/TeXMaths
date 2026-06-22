"""
Ce script est activée au moment de la compilation d'un fichier
exercice-****-data.tex, il permet de copier les lignes
\\usepackage du data vers les fichiers exercice-****-a.tex, etc...
Il copie également la macro \\nodata après les packages.
"""
import re
import sys
from src.tools import LATEX_DIR

EX_DIR = LATEX_DIR / "exercices"

ex_data_file_path = EX_DIR / f"{sys.argv[1]}.tex"
pattern = '-'.join(sys.argv[1].split('-')[:2]) + '-[A-Za-z].tex'

used_packages_lines = []

with open(ex_data_file_path, 'r', encoding='utf8') as ex_data_file:
    ex_data_file_first_line = next(ex_data_file)
    while True:
        line = next(ex_data_file)
        if line.startswith('\\startdatakeys'):
            break
        matches = re.findall(r'\\usepackage(?:\[[^\]]*\])?\{(.*?)\}', line)
        if matches:
            used_packages_lines.append(line)

for ex_c_file_path in EX_DIR.glob('*.tex'):
    ex_c_file_lines = []
    if re.findall(pattern, str(ex_c_file_path)):
        with open(ex_c_file_path, 'r', encoding='utf8') as ex_c_file:
            for line in ex_c_file.readlines():
                if not line.startswith('\\usepackage') and not line.startswith('\\nodata'):
                    ex_c_file_lines.append(line)

        new_ex_c_file_lines = [ex_data_file_first_line] + used_packages_lines + ['\\nodata\n'] + ex_c_file_lines[1:]
        with open(ex_c_file_path, 'w', encoding='utf8') as ex_c_file:
            ex_c_file.writelines(new_ex_c_file_lines)

if __name__ == '__main__':
    print('\n' + ' '.join([__file__, sys.argv[1]]))
