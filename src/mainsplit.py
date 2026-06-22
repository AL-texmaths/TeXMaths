import json
import shutil
import pypdf
from src.tools import YEAR_DIR, LATEX_DIR, DATA_DIR, show

def extract(pdf_in_path, pages_range, pdf_out_path):
    """
    Procedure. Extract pages from a pdf file.
    -----------
    Parameters:
    -----------
    pdf_in_path: string
        The full path of the pdf file to extract.
    pages_range: couple of int (a < b)
    pdf_out_path: string
        The full path of the extracted pdf file.
    """
    pdf_in = pypdf.PdfReader(str(pdf_in_path))
    writer = pypdf.PdfWriter()
    PagesNum = list(range(pages_range[0]-1, pages_range[1]))

    for pageNum in PagesNum:
        writer.add_page(pdf_in.pages[pageNum])

    with open(pdf_out_path, 'wb') as pdf_out:
        print("Opening the writer : " + str(pdf_out_path))
        writer.write(pdf_out)
    show('Pages {} to {} extracted from <{}> to <{}>'.format(PagesNum[0], PagesNum[-1],
        pdf_in_path.name, pdf_out_path.name))

def pages_num(pdf_path):
    pdf = pypdf.PdfReader(str(pdf_path))
    return len(pdf.pages)

mainpath = LATEX_DIR / "main.tex"

structure_path = mainpath.parent / (mainpath.stem + '-structure.txt')
pdf_in_path = mainpath.with_suffix('.pdf')

with open(structure_path, 'r') as structure_file:
    structure_lines = list(map(lambda x: x.split('-'), structure_file.read().split('\n')))[:-1]

for i in range(len(structure_lines)-1):
    structure_lines[i].append(str(int(structure_lines[i+1][0])-1))
structure_lines[-1].append(str(pages_num(pdf_in_path)))

for structure_line in structure_lines:
    beg_page, level, chapter_num, chapter, document, end_page = structure_line
    if document == 'hidden':
        continue
    chapter_name = "Ch" + str(chapter_num) + '_' + chapter
    dirname = YEAR_DIR / level / chapter_name
    dirname.mkdir(parents=True, exist_ok=True)
    filename = '-'.join([level, "Ch" + str(chapter_num), document]) + '.pdf'
    pdf_out_path = dirname / filename
    permission = False
    while not permission:
        try:
            extract(pdf_in_path, (int(beg_page), int(end_page)), pdf_out_path)
            permission = True
        except PermissionError:
            input(f"PermissionError: close {pdf_out_path}")

DOCS = {
    "flash": {
        "foldername": "flash",
        "file prefix": "flash",
        'structure path': mainpath.parent / (mainpath.stem + '-QF.txt')
    },
    "diapo": {
        "foldername": "diapo",
        "file prefix": "diapo",
        'structure path': mainpath.parent / (mainpath.stem + '-diapo.txt')
    }
}
# ADD documents to output
# reading mainsplit.json for metadata
with open(DATA_DIR / "metadata" / "mainsplit.json", 'r', encoding='utf8') as metafile:
    META_DICT = json.load(metafile)
# Read main txt file
for doc_type, doc_dir in DOCS.items():
    with open(doc_dir['structure path'], 'r') as qf_file:
        qf_lines = list(map(lambda x: x.split('-'), qf_file.read().split('\n')))[:-1]
    # copy pdf files
    for qf_line in qf_lines:
        level, chapter_num, chapter, document, doc_num = qf_line
        number, filename = document.split('/')
        filename = filename + '-' + doc_num
        chapter_name = "Ch" + str(chapter_num) + '_' + chapter
        dirname = YEAR_DIR / level / chapter_name
        dirname.mkdir(parents=True, exist_ok=True)
        filepath_out = dirname / ('-'.join([level, "Ch" + str(chapter_num), number]) + '.pdf')
        filepath_in = LATEX_DIR / doc_dir['foldername'] / (doc_dir['file prefix'] + '-' + filename + '.pdf')
        if not filepath_in.exists():
            print(f'Fichier introuvable : {filepath_in}')
        cond1 = not filepath_out.exists() or not filepath_in.stat().st_mtime < filepath_out.stat().st_mtime
        if filepath_out.name in META_DICT.keys():
            cond2 = not (META_DICT[filepath_out.name]['original'] == filepath_in.name)
        else:
            META_DICT[filepath_out.name] = {}
            cond2 = True
        if any([cond1, cond2]):
            META_DICT[filepath_out.name]['original'] = filepath_in.name
            print(f'copying {filepath_in.name} to {filepath_out.name}')
            shutil.copy(filepath_in, filepath_out)

with open(DATA_DIR / "metadata" / "mainsplit.json", 'w', encoding='utf8') as metafile:
    json.dump(META_DICT, metafile, indent=4)