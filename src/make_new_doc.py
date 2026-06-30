import re
import subprocess
from src.tools import LATEX_DIR, get_config, get_pattern
from assistant_progression.utils.resolve import resolve_executable

TEMPLATE_DIR = LATEX_DIR / "templates"
EXERCICES_DIR = LATEX_DIR / "exercices"
DNBQCM_DIR = LATEX_DIR / "dnbqcm"

CODE_EXE_PATH = resolve_executable('code')

DOC_TYPE = get_config()["settings"]['index documents']

def make_new_exercice():

    with open(TEMPLATE_DIR / "template-exercice-data.tex", 'r', encoding='utf8') as ex_datafile:
        new_ex_data = ex_datafile.read()

    with open(TEMPLATE_DIR / "template-exercice-c.tex", 'r', encoding='utf8') as ex_cfile:
        ex_c = ex_cfile.read()

    Exercice_ids = []
    for file_path in EXERCICES_DIR.glob('*.tex'):
        matches = re.findall('exercice-(.*?)-data.tex$', str(file_path))
        if matches:
            Exercice_ids.append(int(matches[0]))
    new_dnbqcm_id = 0
    Exercice_ids.sort()
    for i in range(len(Exercice_ids)-1):
        if not Exercice_ids[i+1] == Exercice_ids[i]+1:
            new_dnbqcm_id = Exercice_ids[i]+1
            break
        new_dnbqcm_id = Exercice_ids[i]+2

    new_exercice_data_path = EXERCICES_DIR / f'exercice-{new_dnbqcm_id:04d}-data.tex'
    new_exercice_path = EXERCICES_DIR / f'exercice-{new_dnbqcm_id:04d}-c.tex'

    new_exc = ex_c.replace('\\enonce{}', '\\enonce{' + f'{new_dnbqcm_id:04d}' + '}')

    with open(new_exercice_data_path, 'w', encoding='utf8') as new_ex_data_file:
        new_ex_data_file.write(new_ex_data)
    
    with open(new_exercice_path, 'w', encoding='utf8') as new_ex_file:
        new_ex_file.write(new_exc)
    
    return new_exercice_data_path, new_exercice_path

def make_new_dnbqcm():

    with open(TEMPLATE_DIR / "template-dnbqcm.tex", 'r', encoding='utf8') as qcm_datafile:
        new_ex_data = qcm_datafile.read()

    Dnbqcm_ids = []
    for file_path in DNBQCM_DIR.glob('*.tex'):
        matches = re.findall('dnbqcm-(.*?).tex$', str(file_path))
        if matches:
            Dnbqcm_ids.append(int(matches[0]))
    new_dnbqcm_id = 0
    Dnbqcm_ids.sort()
    for i in range(len(Dnbqcm_ids)-1):
        if not Dnbqcm_ids[i+1] == Dnbqcm_ids[i]+1:
            new_dnbqcm_id = Dnbqcm_ids[i]+1
            break
        new_dnbqcm_id = Dnbqcm_ids[i]+2

    new_dnbqcm_path = DNBQCM_DIR / f'dnbqcm-{new_dnbqcm_id:04d}.tex'

    with open(new_dnbqcm_path, 'w', encoding='utf8') as new_dnbqcm_file:
        new_dnbqcm_file.write(new_ex_data)
    
    return new_dnbqcm_path

def make_exercice_and_open():
    new_exercice_data_path, new_exercice_path = make_new_exercice()
    if CODE_EXE_PATH is not None:
        subprocess.run([
            str(CODE_EXE_PATH),
            "-r",
            str(new_exercice_data_path),
            str(new_exercice_path)
        ])

def make_new(doc_type, new_doc_path):

    with open(TEMPLATE_DIR / f"template-{doc_type}.tex", 'r', encoding='utf8') as doc_datafile:
        new_doc_data = doc_datafile.read()

    with open(new_doc_path, 'w', encoding='utf8') as new_doc_data_file:
        new_doc_data_file.write(new_doc_data)

def make_new_and_open():

    keys = DOC_TYPE.keys()
    while True:
        doc_type = input('Entrez le type de document ({}) '.format('/'.join(keys)))
        if doc_type in keys:
            break
        print(f'Type de document inconnu : {doc_type}')

    DIR = LATEX_DIR / DOC_TYPE[doc_type]['folder name']

    if doc_type == 'exercice':
        make_exercice_and_open()
        return

    if doc_type == 'dnbqcm':
        new_dnbqcm_path = make_new_dnbqcm()
        print(f'Le fichier {new_dnbqcm_path} a été créé {new_dnbqcm_path.exists()}.')
        if CODE_EXE_PATH is not None:
            subprocess.run(
                [
                    str(CODE_EXE_PATH),
                    "-r",
                    str(new_dnbqcm_path)
                ]
            )
        return

    while True:
        name = input('Entrez le nom du document ')
        if re.findall(r'^[A-Za-z_\\d]+$', name):
            break
        print(f'Le nom ne convient pas : {name}')
    path_pattern = get_pattern(doc_type, extension='tex').replace('([A-Za-z_\\d]+)', name)

    new_document_id = 1
    Document_ids = []
    for file_path in DIR.glob('*.tex'):
        matches = re.findall(path_pattern, str(file_path))
        if matches:
            Document_ids.append(int(matches[0]))
    
    Document_ids.sort()
    if len(Document_ids) == 1:
        if Document_ids[0] == 1:
            new_document_id = 2
        else:
            new_document_id = Document_ids[0]+1
    else:
        for i in range(len(Document_ids)-1):
            if not Document_ids[i+1] == Document_ids[i]+1:
                new_document_id = Document_ids[i]+1
                break
            new_document_id = Document_ids[i]+2

    new_doc_path = DIR / ('-'.join([doc_type, name, str(new_document_id)]) + '.tex')

    if new_doc_path.exists():
        print(f'Le fichier {new_doc_path} existe déjà !')
    else:
        make_new(doc_type, new_doc_path)
    if CODE_EXE_PATH is not None:
        subprocess.run(
            [
                str(CODE_EXE_PATH),
                "-r",
                str(new_doc_path)
            ]
        )

if __name__ == '__main__':
    make_new_and_open()
