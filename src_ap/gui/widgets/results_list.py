from PySide6.QtCore import Qt
from PySide6.QtWidgets import QListWidget, QMessageBox
from src_ap.gui.widgets.metadata_view import MetadataView
from src_ap.controllers.pdf_documents_controller import PdfDocumentsController
from src_ap.gui.menus.pdf_contextual_menu import PdfContextualMenu


class ResultsList(QListWidget):
    def __init__(
            self,
            context,
            pdf_viewer,
            pdf_documents_controller: PdfDocumentsController,
            metadata_view: MetadataView
            ):
        super().__init__()
        self.context = context
        self.pdf_viewer = pdf_viewer
        self.pdf_documents_controller = pdf_documents_controller
        self.metadata_view = metadata_view
        self.itemClicked.connect(self.load_pdf)
        self.itemSelectionChanged.connect(self.on_selection_changed)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(
            self.show_results_context_menu
            )
    
        self.pdf_context_menu = PdfContextualMenu(self.context, self, self.pdf_documents_controller)
    
    def on_selection_changed(self):
        """Appelé quand la sélection change (par clic, flèches, focus)"""
        current_item = self.currentItem()
        if current_item is not None:
            self.load_pdf(current_item)
    
    def load_pdf(self, item):

        pedago_data =  self.context.pedago_data_service.data
        key = item.text()
        document = pedago_data.get(key)

        pdf_path = document.preview or document.pdf

        if not pdf_path.exists():
            QMessageBox.critical(
                self,
                "Erreur",
                f"Fichier PDF introuvable\n{pdf_path}"
            )
            return

        self.pdf_viewer.document.load(str(pdf_path))

        self.metadata_view.show_document(document)

        self.current_enonce = document.enonce
    
    def show_results_context_menu(self, position):
        item = self.itemAt(position)
        if item is None:
            return

        self.setCurrentItem(item)
        self.pdf_context_menu.current_item = item

        self.pdf_context_menu.exec_(self.viewport().mapToGlobal(position))
