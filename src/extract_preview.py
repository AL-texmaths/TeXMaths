import re
from pypdf import PdfReader, PdfWriter
from src.tools import LATEX_DIR, CONFIG, get_pattern

DOC_TYPE = "flash"
FLASH_DICT = CONFIG["parameters"]["index documents"][DOC_TYPE]

FLASH_DIR = LATEX_DIR / FLASH_DICT['folder name']
PREVIEW_DIR = FLASH_DIR / "previews"
if not PREVIEW_DIR.exists():
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
PATTERN = get_pattern(DOC_TYPE, 'pdf')

FLASH_PATHES = []
for file_path in FLASH_DIR.iterdir():
    matches = re.findall(PATTERN, str(file_path))
    if matches:
        FLASH_PATHES.append(file_path)

def del_old_previews(logger=print):
    Flash_names = list(map(lambda path: path.name, FLASH_PATHES))
    for preview_file_path in PREVIEW_DIR.glob('*.pdf'):
        flash_name = '-'.join(preview_file_path.stem.split('-')[1:]) + '.pdf'
        if not flash_name in Flash_names:
            logger(f'Deleting preview {preview_file_path.name}')
            preview_file_path.unlink()

def extract_preview(pdf_path, outdir_path=None, logger=print):
    """
    pdfpath_in : Path object
    """
    if outdir_path == None:
        outdir_path = pdf_path.parent
    output_path = outdir_path / ('preview-' + pdf_path.name)

    if not output_path.exists() or pdf_path.stat().st_mtime > output_path.stat().st_mtime:
        logger(f'extracting preview : {pdf_path.name}')
        reader = PdfReader(str(pdf_path))

        if len(reader.pages) == 0:
            raise ValueError("Le PDF ne contient aucune page.")

        first_page = reader.pages[0]
        last_page = reader.pages[-1]

        writer = PdfWriter()

        # Ordre demandé : dernière page puis première
        writer.add_page(last_page)
        writer.add_page(first_page)

        with open(output_path, "wb") as f:
            writer.write(f)

def update_previews(logger=print):
    del_old_previews()
    for file_path in FLASH_PATHES:
        extract_preview(file_path, PREVIEW_DIR, logger=logger)

if __name__ == '__main__':
    print(f'module {__file__} ok')