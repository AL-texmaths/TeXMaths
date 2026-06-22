import pypdf
from src.tools import (
    LATEX_DIR, get_cours_file_path,
    get_last_run_date, update_last_run_date,
    compile_latex
    )

last_run_date = get_last_run_date(__file__)

EXEMPLES_DIR = LATEX_DIR / "exemples"

CMD ='{} -silent -interaction=nonstopmode {}'
A4_PORTRAIT_HEIGHT = 841
A4_PORTRAIT_WIDTH = 595
A5_PORTRAIT_WIDTH = 419

def export_a4_portrait(pdf_path, scale, lmargin, hmargins, outputPath):
    """
    """
    print(str(pdf_path))
    reader = pypdf.PdfReader(str(pdf_path))
    page = reader.pages[0]

    height = float(page.mediabox[3] - page.mediabox[1])  # hauteur
    outpdf_height = scale*float(height)
    copyNumber = int(A4_PORTRAIT_HEIGHT//(outpdf_height + 2*hmargins))
    if copyNumber == 0:
        print('WARNING: scale too big, no copy exported')
        return

    newpage = pypdf.PageObject.create_blank_page(
        None, A4_PORTRAIT_WIDTH, A4_PORTRAIT_HEIGHT
        )
    n1 = (A4_PORTRAIT_HEIGHT-copyNumber*outpdf_height)/(2*copyNumber)
    n2 = 2*n1 + outpdf_height

    for i in range(copyNumber):
        newpage.merge_transformed_page(
            page,
            pypdf.Transformation().scale(scale).translate(lmargin,  n2*i + n1)
            )

    writer = pypdf.PdfWriter()
    writer.add_page(newpage)

    permissionBoolean = False
    while not permissionBoolean:
        try:
            with open(outputPath, 'wb') as pdf_out:
                writer.write(pdf_out)
            permissionBoolean = True
        except PermissionError:
            input(f"PermissionError: close {outputPath} and press enter to continue")

for texFileName in EXEMPLES_DIR.glob('*.tex'):

    output_path = get_cours_file_path(texFileName.stem)
    output_cours_name = '-'.join(output_path.stem.split('-')[:2] + ['cours.pdf'])
    output_cours_path = output_path.parent / output_cours_name

    if output_path.exists() and output_cours_path.stat().st_mtime < last_run_date.timestamp():
        print(f'Example {output_path.name} already exported')
        continue

    scale, lmargin, vmargins = 1, 0, 0
    with open(EXEMPLES_DIR / texFileName, 'r', encoding='utf8') as texFile:
        for texFileLine in texFile.readlines():
            if '%scale' in texFileLine:
                scale = float(texFileLine.split('[')[1].split(']')[0])
            if '%lmargin' in texFileLine:
                lmargin = float(texFileLine.split('[')[1].split(']')[0])
            if '%vmargins' in texFileLine:
                vmargins = float(texFileLine.split('[')[1].split(']')[0])

    result = compile_latex(EXEMPLES_DIR / texFileName)

    pdf_path = ""
    try :
        pdf_path =  EXEMPLES_DIR / texFileName.with_suffix(".pdf")
        export_a4_portrait(pdf_path, scale, lmargin, vmargins, output_path)
    except(FileNotFoundError):
        print(f"{pdf_path}\n! No pdf file exported !")

update_last_run_date(__file__)
