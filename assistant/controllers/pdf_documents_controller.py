from pathlib import Path
from assistant.utils.resolve import resolve_executable
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QMessageBox


class PdfDocumentsController:
    def __init__(self, context):
        self.context = context

    def open_pdf_with_adobe(self, item):
        try:
            adobe_exe_path = resolve_executable("adobe", config=self.context.config)
        except FileNotFoundError:
            QMessageBox.information(self, "Adobe Reader non trouvé", "Adobe Reader n'est pas installé ou le chemin n'est pas configuré.")
            return

        document = self.context.pedago_data_service.data.get(item.text())
        pdf_path = document.pdf
        try:
            self.context.process_service.open_with(adobe_exe_path, pdf_path)
        except FileNotFoundError:
            QMessageBox.critical(
                self,
                "Erreur ouverture PDF",
                f"Impossible d'ouvrir le PDF avec Adobe Reader.\nChemin attendu: {adobe_exe_path}\nFichier: {pdf_path}"
            )

    def open_pdf_with_pdfxchange(self, item):
        try:
            pdf_xchange_exe_path = resolve_executable("pdf_xchange", config=self.context.config)
        except FileNotFoundError:
            QMessageBox.information(self, "PDF XChange non trouvé", "PDF XChange n'est pas installé ou le chemin n'est pas configuré.")
            return

        document = self.context.pedago_data_service.data.get(item.text())
        pdf_path = Path(document.pdf).resolve()

        if not pdf_path.exists():
            QMessageBox.warning(self, "Fichier introuvable", f"Fichier PDF introuvable\n{pdf_path}")
            return

        try:
            self.context.process_service.open_with(
                str(pdf_xchange_exe_path),
                str(pdf_path),
                '/A',
                "page=1&fullscreen=yes=OpenParameters"
                )
        except OSError as error:
            QMessageBox.critical(self, "Erreur PDF XChange", str(error))

    def open_pdf_with_okular(self, item):
        try:
            okular_exe_path = resolve_executable("okular", config=self.context.config)
        except FileNotFoundError:
            QMessageBox.information(self, "Okular non trouvé", "Okular n'est pas installé ou le chemin n'est pas configuré.")
            return

        document = self.context.pedago_data_service.data.get(item.text())
        pdf_path = Path(document.pdf).resolve()

        if not pdf_path.exists():
            QMessageBox.warning(self, "Fichier introuvable", f"Fichier PDF introuvable\n{pdf_path}")
            return

        try:
            self.context.process_service.open_with(okular_exe_path, pdf_path)
        except OSError as error:
            QMessageBox.critical(self, "Erreur Okular", str(error))

    def open_tex_in_vscode(self, item):
        try:
            code_path_exe = resolve_executable("code", config=self.context.config)
        except FileNotFoundError:
            QMessageBox.information(self, "VS Code non trouvé", "VS Code n'est pas installé ou le chemin n'est pas configuré.")
            return

        document = self.context.pedago_data_service.data.get(item.text())
        tex_path = document.tex

        if not tex_path.exists():
            QMessageBox.warning(self, "Fichier introuvable", f"Fichier .tex introuvable\n{tex_path}")
            return

        try:
            self.context.process_service.open_with(code_path_exe, tex_path)
        except OSError as error:
            QMessageBox.critical(self, "Erreur VS Code", str(error))

    def copy_enonce_for_item(self, item):
        document = self.context.pedago_data_service.data.get(item.text())
        enonce = document.enonce

        if not enonce:
            QMessageBox.information(self, "Exemple minimal", "Aucun énoncé LaTeX n'est disponible pour cet item")
            return

        clipboard = QGuiApplication.clipboard()
        clipboard.setText(enonce)
        QMessageBox.information(self, "Exemple minimal", "Exemple minimal copié dans le presse papier")