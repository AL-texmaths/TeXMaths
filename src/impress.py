import re
import sys
import time
import pypdf
import subprocess
from pathlib import Path
from src.tools import CONFIG, DEFAULT_DATA_LOG_DIR, TMP_DIR, get_cours_file_path, get_exe

log_file_path = DEFAULT_DATA_LOG_DIR / 'impress.log'
PRINTER = CONFIG['parameters']['printers'][2]

GS_CMD = {
    "A5 Portrait": [
    CONFIG["executables"]["ghostscript"],
    "-sDEVICE=pdfwrite",
    "-dCompatibilityLevel=1.4",
    "-dPDFFitPage",
    "-dFIXEDMEDIA",
    "-dDEVICEWIDTHPOINTS=595",
    "-dDEVICEHEIGHTPOINTS=842",
    "-dNOPAUSE",
    "-dBATCH",
    "-sOutputFile={}",
    "{}"
    ],
    "A5 Landscape": [
    CONFIG["executables"]["ghostscript"],
    "-sDEVICE=pdfwrite",
    "-dCompatibilityLevel=1.4",
    "-dPDFFitPage",
    "-dFIXEDMEDIA",
    "-dDEVICEWIDTHPOINTS=842",
    "-dDEVICEHEIGHTPOINTS=595",
    "-dAutoRotatePages=/None",
    "-dNOPAUSE",
    "-dBATCH",
    "-sOutputFile={}",
    "{}"
    ]
}

def get_pdf_size(pdf_path):
    # Ouvre le fichier PDF
    reader = pypdf.PdfReader(str(pdf_path))
    
    # Récupère la première page
    page = reader.pages[0]
    
    # Obtient les dimensions de la page
    width = float(page.mediabox[2] - page.mediabox[0])  # largeur
    height = float(page.mediabox[3] - page.mediabox[1])  # hauteur
    
    return width, height

def get_pdf_format(pdf_path):
    width, height = get_pdf_size(pdf_path)
    # Convertir les dimensions en format standard
    if (abs(width - 595) < 1 and abs(height - 842) < 1):
        return "A4 Portrait"
    elif (abs(width - 842) < 1 and abs(height - 595) < 1):
        return "A4 Landscape"
    elif (abs(width - 420) < 1 and abs(height - 595) < 1):
        return "A5 Portrait"
    elif (abs(width - 595) < 1 and abs(height - 420) < 1):
        return "A5 Landscape"
    return ""

def merge_a5_portrait(pdf_path: Path):
    # Ouverture du fichier PDF d'entrée
    with open(pdf_path, "rb") as input_pdf_file:
        reader = pypdf.PdfReader(input_pdf_file)
        writer = pypdf.PdfWriter()

        num_pages = len(reader.pages)

        # Traiter chaque paire de pages
        width, height = get_pdf_size(pdf_path)

        writer = pypdf.PdfWriter()
        for i in range(0, num_pages//2+1, 2):

            newpage = pypdf.PageObject.create_blank_page(width=width*2, height=height)
            newpage.merge_transformed_page(reader.pages[i], pypdf.Transformation().scale(1).translate(0, 0))
            try:
                newpage.merge_transformed_page(reader.pages[i+1], pypdf.Transformation().scale(1).translate(width, 0))
            except IndexError:
                if num_pages == 1:
                    newpage.merge_transformed_page(reader.pages[i], pypdf.Transformation().scale(1).translate(width, 0))
                pass

            writer.add_page(newpage)

        output_path = pdf_path.parent / "merged" / pdf_path.name
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'wb') as pdf_out:
            writer.write(pdf_out)
        
        return output_path

def merge_a5_landscape(pdf_path: Path):
    # Ouverture du fichier PDF d'entrée
    with open(pdf_path, "rb") as input_pdf_file:
        reader = pypdf.PdfReader(input_pdf_file)
        writer = pypdf.PdfWriter()

        num_pages = len(reader.pages)

        # Traiter chaque paire de pages
        width, height = get_pdf_size(pdf_path)

        writer = pypdf.PdfWriter()
        for i in range(0, num_pages//2+1, 2):

            newpage = pypdf.PageObject.create_blank_page(width=width, height=2*height)
            newpage.merge_transformed_page(reader.pages[i], pypdf.Transformation().scale(1).translate(0, height))
            try:
                newpage.merge_transformed_page(reader.pages[i+1], pypdf.Transformation().scale(1).translate(0, 0))
            except IndexError:
                if num_pages == 1:
                    newpage.merge_transformed_page(reader.pages[i], pypdf.Transformation().scale(1).translate(0, 0))
                pass
            writer.add_page(newpage)

        output_path = pdf_path.parent / "merged" / pdf_path.name
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'wb') as pdf_out:
            writer.write(pdf_out)
        
        return output_path

def merge_a5(pdf_path):
    format = get_pdf_format(pdf_path).lower().replace(" ", "_")
    if not format.startswith('a5'):
        print(f'No merged because A4 format {pdf_path}')
        return pdf_path
    return globals()['merge_' + format](pdf_path)

SUMATRAPDF_SETTINGS = {
    "simple settings": [
        "even",
        "odd",
        "portrait",
        "landscape",
        "noscale",
        "shrink",
        "fit",
        "color",
        "monochrome",
        "duplex",
        "duplexlong",
        "simplex"
        ],
    "trays": [],
    "papers": ["A2", "A3", "A4", "A5", "A6", "letter", "legal", "tabloid", "statement"]
}

def print_settings_ok(print_settings:str):
    settings_list = print_settings.split(',')
    results = []
    for setting in settings_list:
        if re.findall(r'^\d*x\d*$', setting):
            if setting.endswith('x'):
                results.append(setting[:-1].isdigit())
            else:
                print("copy number setting must start with digits and end with 'x'")
                results.append(False)
            continue
        if setting.startswith('bin='):
            tray = setting.split('bin=')[1]
            if tray.isdigit()or tray in SUMATRAPDF_SETTINGS['trays']:
                results.append(True)
            else:
                print(f"tray doesn't exist: {tray}")
                results.append(False)
            continue
        if setting.startswith('paper='):
            paper = setting.split('paper=')[1]
            if paper in SUMATRAPDF_SETTINGS['papers']:
                results.append(True)
            else:
                print(f"paper doesn't exist: {paper}")
                results.append(False)
            continue
        if setting in SUMATRAPDF_SETTINGS['simple settings']:
            results.append(True)
        else:
            print(f"setting doesn't exist: {setting}")
            results.append(False)
    return all(results)

def print_pdf(pdf_path, printer:str, printsettings:str):
    """
    """
    if not print_settings_ok(printsettings):
        return 1
    output_path = merge_a5(pdf_path)
    cmd = '{} -print-settings "{}" -print-to "{}" {}'.format(
    get_exe("sumatrapdf"), printsettings, printer, output_path)
    message = f'printing {pdf_path.name} to {printer}'
    print(cmd)
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )
    # Code retour
    if result.returncode != 0:
        print(f"WARNING : code de sortie {result.returncode} pour la commande " + cmd)
    else:
        print('SUCCESS: ' + message)
    return result.returncode    

def extract_big(pdf_path):
    pdf_format = get_pdf_format(pdf_path)
    if pdf_format is None:
        print('Format non reconnu')
        return
    if pdf_format and not pdf_format in GS_CMD.keys():
        return 0
    cmd = " ".join(GS_CMD[pdf_format]).format(TMP_DIR / pdf_path.name, pdf_path)
    print(cmd)
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print("Erreur")
    else:
        print("Success")

def read_impress_datas():
    try:
        with open(log_file_path, 'r') as impress_log_file:
            impress_datas = impress_log_file.read()

    except(FileNotFoundError):
        print("File not found : ", log_file_path)
        with open(log_file_path, 'w') as impress_log_file:
            impress_datas = 'IMPRESS LOG FILE\n'
            impress_log_file.write(impress_datas)
    return impress_datas

def write_impress_datas(printer, file_name, print_settings):
    current_impress_datas = read_impress_datas()
    current_impress_datas = current_impress_datas + '||'.join([
            time.strftime('%Y-%m-%d-%H:%M:%S'),
            printer, file_name, print_settings
            ])

    with open(log_file_path, 'w') as impress_log_file:
        impress_log_file.write(current_impress_datas+ '\n')

if __name__ == '__main__':

    tmp_files_path = []
    result = None
    fileName = None
    printsettings = None
    for fileName, printsettings in map(lambda string: string.split(';'), sys.argv[1:]):
        if fileName.split('-')[-1] == 'big':
            fileName = fileName[:-4]
            pdf_path = get_cours_file_path(fileName)
            extract_big(pdf_path)
            big_pdf_path = TMP_DIR / pdf_path.name
            tmp_files_path.append(big_pdf_path)
        else:
            pdf_path = get_cours_file_path(fileName)
        message = "Start printing " + fileName + " Settings : " + printsettings
        n = len(message)
        print("="*n)
        print('\n' + message + '\n')
        print("="*n)
        result = print_pdf(pdf_path, PRINTER, printsettings)

    for tmp_file_path in tmp_files_path:
        tmp_file_path.unlink()
    
    if fileName is not None and printsettings is not None and result == 0:
        write_impress_datas(PRINTER, fileName, printsettings)
        
