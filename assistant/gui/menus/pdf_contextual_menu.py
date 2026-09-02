from assistant.utils.resolve import resolve_executable
from PySide6.QtWidgets import QMenu
from PySide6.QtGui import QAction
from assistant.controllers.pdf_documents_controller import PdfDocumentsController


class PdfContextualMenu(QMenu):
    def __init__(self, context, results_list, pdf_documents_controller: PdfDocumentsController):
        super().__init__()
        self.context = context
        self.results_list = results_list
        self.pdf_documents_controller = pdf_documents_controller
        self.current_item = None

        copy_enonce_action = self.add_action(
            "Copier l'exemple minimal LaTeX",
            self.pdf_documents_controller.copy_enonce_for_item,
        )

        open_tex_action = self.add_action(
            "Ouvrir le fichier .tex dans VS Code",
            self.pdf_documents_controller.open_tex_in_vscode,
            resolve_executable("code", config=self.context.config) is not None
        )

        open_pdf_adobe_action = self.add_action(
            "Ouvrir le fichier PDF dans Adobe Reader",
            self.pdf_documents_controller.open_pdf_with_adobe,
            resolve_executable("adobe", config=self.context.config) is not None
        )

        open_pdf_xchange_action = self.add_action(
            "Ouvrir le fichier PDF dans PDF XChange",
            self.pdf_documents_controller.open_pdf_with_pdfxchange,
            resolve_executable("pdf_xchange", config=self.context.config) is not None
        )

        open_pdf_okular_action = self.add_action(
            "Ouvrir le fichier PDF dans Okular",
            self.pdf_documents_controller.open_pdf_with_okular,
            resolve_executable("okular", config=self.context.config) is not None
        )

        self.addAction(copy_enonce_action)
        self.addAction(open_tex_action)
        self.addAction(open_pdf_xchange_action)
        self.addAction(open_pdf_adobe_action)
        self.addAction(open_pdf_okular_action)

    def add_action(self, text, callback, enabled: bool = True):
        action = QAction(text, self)
        action.setEnabled(enabled)
        action.triggered.connect(
            lambda checked=False, cb=callback: cb(self.current_item)
        )
        return action
