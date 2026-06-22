import sys
from pathlib import Path
from datetime import datetime
from src.tools import LATEX_DIR, compile_latex

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
START_MESSAGE = "Start Compilation Test"
END_MESSAGE = "End Compilation Test"
cmd_args = ["-draftmode", "-interaction=nonstopmode", "-halt-on-error"]

DIRPATH = LATEX_DIR / Path(sys.argv[1])

log_file = DIRPATH / "log.txt"
error_count = 0

# recuperation des chemins du dernier test et de la dernière date
print("Recuperation des chemins du dernier test")
file_path_to_test = []
last_date = datetime(2025, 1, 1)
try:
    with open(log_file, 'r', encoding="utf8") as log:
        data=log.read().split('\n')
        data.reverse()
        startinfile = False
        for dataline in data:
            if START_MESSAGE in dataline:
                last_date_string = dataline.split('/')[-1]
                last_date = datetime.strptime(last_date_string, DATE_FORMAT)
                file_path_to_test.reverse()
                startinfile = True
                break
            if not END_MESSAGE in dataline.split('/') and not dataline=='':
                file_path_to_test.append(dataline)
except(FileNotFoundError):
    with open(log_file, 'w', encoding="utf8"):
        pass
    last_date = datetime.min

# addition des fichiers plus récents
print("Addition des fichiers plus récents ...")
for texfile_path in DIRPATH.glob('*.tex'):
    with open(texfile_path, 'r', encoding='utf8') as texfile:
        content = texfile.read()
    if not r'\documentclass' in content:
        print(f'WARNING : no \\documentclass in {texfile_path}')
    print(texfile_path)
    print(last_date.timestamp())
    if texfile_path.stat().st_mtime > last_date.timestamp() and not texfile_path in file_path_to_test:
        file_path_to_test.append(texfile_path)

# Test
print("Démarrage des tests :")
logfiles = []
for file_path in file_path_to_test:
    with open(file_path, 'r', encoding='utf8') as texfile:
        content = texfile.read()
    if r'\documentclass' in content:
        result = compile_latex(file_path, cmd_args=cmd_args)
with open(log_file, 'a', encoding="utf8") as log:
    log.write(START_MESSAGE + "/" + datetime.now().strftime(DATE_FORMAT)+'\n')
    for logfilename in logfiles:
        log.write(logfilename)
    log.write(END_MESSAGE + "/" + str(error_count)+'\n')
print("Fin des tests : {} erreurs".format(error_count))
