from pathlib import Path
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QGuiApplication
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QSplitter,
    QLineEdit,
    QListWidget,
    QMessageBox,
    QMenu,
    QComboBox,
    )
from src.views.widgets.pdf_viewer import PdfViewerWidget
from src.views.widgets.metadata_view import MetadataView
from src.models.search_filters import SearchFilters
from src_ap.controllers.search_pdf_controller import SearchPDFController

from src_ap.utils.resolve import resolve_executable


class PdfDocumentsController:
    def __init__(self, context):
        self.context = context

    def open_pdf_with_adobe(self, item):
        try:
            adobe_exe_path = resolve_executable("adobe", config=self.context.config)
        except FileNotFoundError:
            QMessageBox.information(self, "Adobe Reader non trouvé", "Adobe Reader n'est pas installé ou le chemin n'est pas configuré.")
            return

        doc_dict = self.context.document_repository.get_doc_by_key(item.text())
        pdf_path = Path(doc_dict['pdf']).resolve()
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

        doc_dict = self.context.document_repository.get_doc_by_key(item.text())
        pdf_path = Path(doc_dict.get("pdf", "")).resolve()

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

        doc_dict = self.context.document_repository.get_doc_by_key(item.text())
        pdf_path = Path(doc_dict.get("pdf", "")).resolve()

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

        doc_dict = self.context.document_repository.get_doc_by_key(item.text())
        tex_path = Path(doc_dict.get("tex", "")).resolve()

        if not tex_path.exists():
            QMessageBox.warning(self, "Fichier introuvable", f"Fichier .tex introuvable\n{tex_path}")
            return

        try:
            self.context.process_service.open_with(code_path_exe, tex_path)
        except OSError as error:
            QMessageBox.critical(self, "Erreur VS Code", str(error))

    def copy_enonce_for_item(self, item):
        doc_dict = self.context.document_repository.get_doc_by_key(item.text())
        enonce = doc_dict.get("enonce", "")

        if not enonce:
            QMessageBox.information(self, "Exemple minimal", "Aucun énoncé LaTeX n'est disponible pour cet item")
            return

        clipboard = QGuiApplication.clipboard()
        clipboard.setText(enonce)
        QMessageBox.information(self, "Exemple minimal", "Exemple minimal copié dans le presse papier")

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
        self.addAction(action)
    


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

        key = item.text()

        doc_dict = self.context.document_repository.get_doc_by_key(key)
        pdf_path = doc_dict.get("preview") or doc_dict.get("pdf")  
        pdf_path = Path(pdf_path).resolve()

        print(f"Loading PDF for key: {key}")
        print(f"PDF path: {pdf_path}")

        if not pdf_path.exists():
            QMessageBox.critical(
                self,
                "Erreur",
                f"Fichier PDF introuvable\n{pdf_path}"
            )
            return

        self.pdf_viewer.document.load(str(pdf_path))

        document = self.context.document_repository.get_doc_by_key(key)

        self.metadata_view.show_document(document)

        self.current_enonce = document.get(
            "enonce",
            ""
        )
    
    def show_results_context_menu(self, position):
        item = self.itemAt(position)
        if item is None:
            return

        self.setCurrentItem(item)
        self.pdf_context_menu.current_item = item

        self.pdf_context_menu.exec_(self.viewport().mapToGlobal(position))


class SearchInput(QLineEdit):
    def __init__(self, callback, results_list=None):
        super().__init__()
        self.setPlaceholderText("Recherche (regex)")
        self.textChanged.connect(self.schedule_search)
        self.callback = callback
        self.results_list = results_list

        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.callback)
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Down:
            if self.results_list and self.results_list.count() > 0:
                self.results_list.setCurrentRow(0)
                self.results_list.setFocus()
                return
        super().keyPressEvent(event)
        
    def schedule_search(self):
        self.search_timer.start(300)


class DocumentTab(QWidget):
    def __init__(self, context, filter_pdf_doc_menu):
        super().__init__()
        self.context = context
        self.filter_pdf_doc_menu = filter_pdf_doc_menu

        self.pdf_viewer = PdfViewerWidget()
        self.pdf_documents_controller = PdfDocumentsController(context)
        layout = QVBoxLayout(self)
        splitter = QSplitter(Qt.Horizontal)

        # search layout
        left_layout = QVBoxLayout()
    
        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        splitter.addWidget(left_widget)

        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        self.inner_splitter = QSplitter(Qt.Vertical)
        self.inner_splitter.addWidget(self.pdf_viewer.view)
        self.inner_splitter.setStretchFactor(0, 3)
        self.inner_splitter.setStretchFactor(1, 1)

        self.metadata_view = MetadataView(self.context)
        self.inner_splitter.addWidget(
            self.metadata_view
        )

        self.results_list = ResultsList(
            self.context,
            self.pdf_viewer,
            self.pdf_documents_controller,
            self.metadata_view
            )
        self.results_list.installEventFilter(self)
        
        self.search_input = SearchInput(self.update_results, self.results_list)
        self.search_input.installEventFilter(self)

        left_layout.addWidget(self.search_input)
        left_layout.addWidget(self.results_list)

        right_layout.addWidget(self.inner_splitter)
        QTimer.singleShot(0, self._set_initial_splitter_sizes)
        QTimer.singleShot(0, self.search_input.setFocus)
        splitter.addWidget(right_widget)

        layout.addWidget(splitter)

        self.key_filter_actions = {}
        self.field_actions = {}
        self.empty_filters = {}

        self.sort_order_combo = QComboBox()
        self.sort_order_combo.addItem("Trier par ordre alphabétique")
        self.sort_order_combo.addItem("Trier par date de modification")
        # Défaut : trier par date de modification
        self.sort_order_combo.setCurrentIndex(1)
        self.sort_order_combo.currentIndexChanged.connect(self.update_results)
        left_layout.addWidget(self.sort_order_combo)

        self.search_pdf_controller = SearchPDFController(self.context.search_pdf_service)
    
    def _set_initial_splitter_sizes(self):
        """Set the inner splitter sizes so the bottom pane is ~1/4 of window height."""
        try:
            total = self.height()
            if not total or total <= 0:
                total = 800
            top = int(total * 0.75)
            bottom = max(120, int(total * 0.25))
            # If the splitter exists, apply sizes [top, bottom]
            if hasattr(self, 'inner_splitter') and self.inner_splitter is not None:
                self.inner_splitter.setSizes([top, bottom])
        except Exception:
            pass
    
    def build_search_filters(self) -> SearchFilters:

        return SearchFilters(
            pattern=self.search_input.text().strip(),
            active_prefixes=self.filter_pdf_doc_menu.get_checked_types(),
            active_fields=self.filter_pdf_doc_menu.get_checked_fields(),
            empty_fields=[
                field
                for field, cb in self.empty_filters.items()
                if cb.isChecked()
            ],
            sort_mode=self.sort_order_combo.currentIndex(),
        )

    def update_results(self):

        filters = self.build_search_filters()

        results = self.search_pdf_controller.search(filters)

        self.results_list.clear()

        for key, _ in results:
            self.results_list.addItem(key)
    
    def load_data(self):
        self.context.document_repository.load()
        types = self.context.document_repository.get_types()
        fields = self.context.document_repository.get_fields()

        self.filter_pdf_doc_menu.rebuild_types_menu(types)
        self.filter_pdf_doc_menu.rebuild_fields_menu(fields)
    