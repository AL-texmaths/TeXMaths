import re
import subprocess
from src.tools import (
    LATEX_DIR, CONFIG, DATA_DIR, TMP_DIR,
    compile_latex, analyse_log_pdflatex)

EXERCICE_PATH = LATEX_DIR / "exercices"
ALLEXERCICES_PATH = EXERCICE_PATH / "allexercices.tex"
VSCODE_EXE = CONFIG['executables']['code']

tex_datalines = ['\\documentclass[exercice]{thedocument}', '\\begin{document}']
for filename in EXERCICE_PATH.iterdir():
    matches = re.findall(r'exercice-(\d*?)-data.tex', str(filename))
    if matches :
        tex_datalines.append('\\enonce{' + matches[0] + '}')
tex_datalines.append('\\end{document}')
with open(ALLEXERCICES_PATH, 'w', encoding='utf8') as outputfile:
    outputfile.write('\n'.join(tex_datalines))

result = compile_latex(
    ALLEXERCICES_PATH,
    cmd_args=['-draftmode', f'-output-directory={TMP_DIR}'],
    motor='pdflatex'
    )

log_name = (ALLEXERCICES_PATH.stem + '.log')
log_path_in = TMP_DIR / log_name
log_path_out = DATA_DIR / "logs" / log_name
analyse_log_pdflatex(log_path_in, log_path_out)

for file_path in TMP_DIR.glob('*'):
    pattern = ALLEXERCICES_PATH.stem + r'\.([A-za-z\.]+)$'
    matches = re.findall(pattern, str(file_path))
    if matches:
        file_path.unlink()

ALLEXERCICES_PATH.unlink()

cmd_args = [VSCODE_EXE, ' -r', str(log_path_out)]
subprocess.run(' '.join(cmd_args))