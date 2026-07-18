import re
from pypdf import PdfReader, PdfWriter
from assistant.utils.textools import get_pattern

class FlashPreviewService:
    def __init__(self, context, logger=print):
        self.logger = logger
        self.context = context
        self.doc_type = "flash"
        self.latex_path = context.paths.latex
        self.types_dict = context.config.settings.pedago_service.pedago_doc_types
        self.flash_dir = self.latex_path / self.types_dict[self.doc_type].dir_name
        self.preview_dir = self.flash_dir / "previews"
        if not self.preview_dir.exists():
            self.preview_dir.mkdir(parents=True, exist_ok=True)
        self.name_pattern = get_pattern(self.types_dict, self.doc_type, 'pdf')

        self.build_flash_pathes()

    def build_flash_pathes(self):
        self.pathes = []
        for file_path in self.flash_dir.iterdir():
            matches = re.findall(self.name_pattern, str(file_path))
            if matches:
                self.pathes.append(file_path)

    def del_old_previews(self):
        Flash_names = list(map(lambda path: path.name, self.pathes))
        for preview_file_path in self.preview_dir.glob('*.pdf'):
            flash_name = '-'.join(preview_file_path.stem.split('-')[1:]) + '.pdf'
            if not flash_name in Flash_names:
                self.logger(f'Deleting preview {preview_file_path.name}')
                preview_file_path.unlink()

    def extract_preview(self, pdf_path, outdir_path=None):
        """
        pdfpath_in : Path object
        """
        if outdir_path == None:
            outdir_path = pdf_path.parent
        output_path = outdir_path / ('preview-' + pdf_path.name)

        if not output_path.exists() or pdf_path.stat().st_mtime > output_path.stat().st_mtime:
            self.logger(f'extracting preview : {pdf_path}')
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

    def update_previews(self):
        self.del_old_previews()
        for file_path in self.pathes:
            self.extract_preview(file_path)
