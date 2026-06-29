import csv
import sys
from src.tools import (
    get_config, DATA_DIR, LATEX_DIR, OUTPUT_DIR, TMP_DIR,
    del_files_by_ext, getmodtime, compile_latex)

LOGICIEL = get_config()["settings"]["logiciel"]
LISTPATH = DATA_DIR / "student_lists"
TEMPLATES = LATEX_DIR / "templates"
YEAR = get_config()["settings"]["year"]
OUTPUT_LIST_DIR = OUTPUT_DIR / YEAR / "suivi"

classes = sys.argv[1:]
if len(classes) == 1 and classes[0] == 'All':
    classes = []
    for file in LISTPATH.glob('*.csv'):
        classes.append(file.name.split('-')[-1])

def get_student_list_csv_ent(classe):
    """
    Function. Get the student list from csv file.
    -----------
    Parameters:
    -----------
    classe: string
        (6eme, 5eme, 4eme, ...)
    --------
    Returns:
    --------
    student_list: list of string
        The student list.
    """
    csvpath = LISTPATH / f'list-{classe}.csv'
    student_list = []
    
    with open(csvpath, newline='') as csvfile:
        file = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in file:
            name = ''.join(row)
            student_list.append(name[:-1])
    
    student_list = student_list[1:]
    student_list.sort()
    return student_list

def get_student_list_csv_pronote(classe):
    """
    Function. Get the student list from csv file.
    -----------
    Parameters:
    -----------
    classe: string
        (6eme, 5eme, 4eme, ...)
    --------
    Returns:
    --------
    student_list: list of string
        The student list.
    """
    csvpath = LISTPATH / f'liste-{classe}.csv'
    student_list = []
    
    with open(csvpath, newline='') as csvfile:
        file = csv.reader(csvfile, delimiter=',', quotechar='"')
        print(file)
        k=0
        for row in file:
            if k>0:
                name = row[0].split(";")[0]
                student_list.append(name)
            k = k+1
    student_list.sort()

    return student_list

def write_list_txt(classe):
    txtpath = LISTPATH / f'liste-{classe}.txt'
    csvpath = LISTPATH / f'liste-{classe}.csv'
    txtmodtime = getmodtime(txtpath)
    csvmodtime = getmodtime(csvpath)
    if txtmodtime > csvmodtime:
        print("No need to change list : " + f'liste-{classe}.txt')
        return
    with open(txtpath, 'w') as list_file:
        list_file.write('\n'.join(globals()["get_student_list_csv_" + LOGICIEL](classe)))

def isallupper(string):
    answer = []
    for letter in string[1:]:
        answer.append(letter.isupper())
    return all(answer)

def nametofirstlast(string):
    new_string = string.replace("-", " ")
    string_list = new_string.split(" ")
    print(string_list)
    last_name = " ".join(filter(isallupper,string_list))
    first_name = " ".join(filter(lambda string: not isallupper(string),string_list))
    return ";".join([last_name, first_name])

def student_name_line(firstname,lastname):
    return "{}&{}&&&&&&&\\\\".format(firstname,lastname)

def macro(param):
    return "\\def\\suivi@" + param

suivi_type = input('type ? (suivi/vierge) ')
periode = input('periode ? ')
PARAM = {
    "periode" : periode,
    "type"    : suivi_type
}

for classe in classes:
    PARAM["classe"] = classe
    write_list_txt(classe)
    with open(TEMPLATES / f"liste-{suivi_type}-template.tex", 'r', encoding='utf-8') as tex_file:
        tex_file_data_lines = tex_file.read().split('\n')

    with open(LISTPATH / f"liste-{classe}.txt", 'r', encoding='utf-8') as txt_file:
        txt_file_data_lines = txt_file.read().split('\n')

    tex_file_last_line = tex_file_data_lines[-1]
    tex_file_data_lines = tex_file_data_lines[:-1]

    studentsnumber = 0
    for student_names in txt_file_data_lines:
        student_names = nametofirstlast(student_names)
        print(student_names)
        studentsnumber += 1
        tex_file_data_lines.append(student_name_line(*student_names.split(';')))

    PARAM["studentsnumber"] = str(studentsnumber)

    tex_file_data_lines.append(tex_file_last_line)

    with open(TMP_DIR / f"liste-{classe}.tex", 'w', encoding='utf-8') as tex_file:
        tex_file.write('\n'.join(tex_file_data_lines))

    with open(TEMPLATES / "suivi-template.tex", 'r', encoding='utf-8') as suivi_file:
        suivi_file_lines = suivi_file.read().split('\n')

    for line_index in range(len(suivi_file_lines)):
        line = suivi_file_lines[line_index]
        for param in PARAM.keys():
            if macro(param) in line:
                suivi_file_lines[line_index] = macro(param) + "{" + PARAM[param] + "}"

    texfilename = f"suivi-{classe}-{periode}.tex"
    texfiletocomp = TMP_DIR / texfilename
    with open(texfiletocomp, 'w', encoding='utf-8') as suivi_file:
        suivi_file.write('\n'.join(suivi_file_lines))

    
    if not OUTPUT_LIST_DIR.exists():
        OUTPUT_LIST_DIR.mkdir(parents=True, exist_ok=True)
    cmdargs = [
        "-interaction=nonstopmode",
        "-file-line-error",
        "-output-directory=" + str(OUTPUT_LIST_DIR)
        ]
    result = compile_latex(texfilename, cmd_args=cmdargs, cwd=TMP_DIR, silent=False)

if result.returncode != 0:
    print(f"Erreur lors de la compilation du fichier {texfilename}.")
    print(result.stderr)
else:
    del_files_by_ext(TMP_DIR, ['.tex'])
    del_files_by_ext(OUTPUT_LIST_DIR, ['.log','.aux'])
    