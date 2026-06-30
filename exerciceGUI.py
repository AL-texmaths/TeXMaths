import sys
from pathlib import Path
from src.tools import camel_to_sentence
from src.qss import THEMES

from src.services.katex_service import KatexService
from src.app.startup import create_context
from src.views.widgets.pdf_viewer import PdfViewerWidget
from src.views.widgets.metadata_view import MetadataView
from src.models.search_filters import SearchFilters
from src.controllers.search_controller import SearchController

from assistant_progression.utils.textools import update_code_index
from src.update_data_index import update_json
from src.check_database import check_database
from src.extract_preview import update_previews

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QListWidget, QLabel, QMessageBox,
    QSplitter, QFrame, QPushButton, QPlainTextEdit,
    QTabWidget, QCheckBox, QComboBox, QMenu, QLayout
)
from PySide6.QtCore import (
    Qt, QObject, QThread, Signal, QTimer,
    QEvent, QSize, QRect, QPoint
)
from PySide6.QtGui import (
    QGuiApplication, QAction,
    QShortcut, QKeySequence
)

class FlowLayout(QLayout):
    """A wrapping flow layout for PySide6: places widgets horizontally and wraps to new lines."""
    def __init__(self, parent=None, margin=0, spacing=-1):
        super().__init__(parent)
        self._items = []
        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)
        self.setSpacing(spacing)

    def addItem(self, item):
        self._items.append(item)

    def count(self):
        return len(self._items)

    def itemAt(self, index):
        if 0 <= index < len(self._items):
            return self._items[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self._items):
            return self._items.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientations(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self.doLayout(QRect(0, 0, width, 0), True)

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        margins = self.contentsMargins()
        size += QSize(margins.left() + margins.right(), margins.top() + margins.bottom())
        return size

    def doLayout(self, rect, testOnly):
        x = rect.x()
        y = rect.y()
        lineHeight = 0

        effectiveSpacing = self.spacing() if self.spacing() >= 0 else 6
        for item in self._items:
            itemSize = item.sizeHint()
            nextX = x + itemSize.width() + effectiveSpacing
            if nextX - effectiveSpacing > rect.right() and lineHeight > 0:
                x = rect.x()
                y = y + lineHeight + effectiveSpacing
                nextX = x + itemSize.width() + effectiveSpacing
                lineHeight = 0
            if not testOnly:
                item.setGeometry(QRect(QPoint(x, y), itemSize))
            x = nextX
            lineHeight = max(lineHeight, itemSize.height())
        return y + lineHeight - rect.y()

class RegexPDFSearchApp(QWidget):
    def __init__(self, context):
        super().__init__()

        self.context = context
        self.pdf_viewer = PdfViewerWidget()

        self.katex_service = KatexService(self.context.config.get_path_by_key("katex"))
        self.metadata_view = MetadataView(self.context)
        self.search_controller = SearchController(self.context.search_service)

        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.update_results)

        self.setWindowTitle("Assistant de navigation")
        self.resize(1200, 700)

        # Gestion file d'attente scripts
        self.script_queue = []
        self.current_process = None

        main_layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # =========================
        # ONGLET 1 : Recherche PDF
        # =========================

        tab1 = QWidget()
        tab1_layout = QVBoxLayout(tab1)
        splitter = QSplitter(Qt.Horizontal) # pyright: ignore[reportAttributeAccessIssue]
        tab1_layout.addWidget(splitter)

        # Partie gauche
        left_layout = QVBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Recherche (regex)")
        self.search_input.textChanged.connect(self.schedule_search)

        self.results_list = QListWidget()
        self.results_list.itemClicked.connect(self.load_pdf)
        self.results_list.setContextMenuPolicy(Qt.CustomContextMenu)# type:ignore
        self.results_list.customContextMenuRequested.connect(self.show_results_context_menu)
        # Intercept keyboard navigation (flèches) to load l'item courant
        self.results_list.installEventFilter(self)
        self.search_input.installEventFilter(self)

        left_layout.addWidget(self.search_input)
        left_layout.addWidget(self.results_list)


        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        splitter.addWidget(left_widget)

        # Partie droite
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # Use a vertical splitter so the PDF (top) and HTML info (bottom)
        # are separated by a draggable splitter the user can resize.
        self.inner_splitter = QSplitter(Qt.Vertical)#type:ignore
        self.inner_splitter.addWidget(self.pdf_viewer.view)

        # Give PDF more initial space than the info panel (stretch factors)
        self.inner_splitter.setStretchFactor(0, 3)
        self.inner_splitter.setStretchFactor(1, 1)

        self.inner_splitter.addWidget(
            self.metadata_view
        )

        right_layout.addWidget(self.inner_splitter)
        # Apply initial sizes once the event loop runs so the window size is known
        QTimer.singleShot(0, self._set_initial_splitter_sizes)
        QTimer.singleShot(0, self.search_input.setFocus)
        splitter.addWidget(right_widget)

        self.tabs.addTab(tab1, "Recherche PDF")

        # =========================
        # ONGLET 2 : Paramètres
        # =========================

        tab2 = QWidget()
        tab2_layout = QVBoxLayout(tab2)

        self.clear_output_button = QPushButton("Clear output")
        self.reload_database_button = QPushButton("Reload database")
        self.console_output = QPlainTextEdit()
        self.console_output.setReadOnly(True)


        self.clear_output_button.clicked.connect(self.console_output.clear)
        self.reload_database_button.clicked.connect(self.reload_check_database)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.clear_output_button)
        button_layout.addWidget(self.reload_database_button)

        # Sélecteur de thème
        self.initial_theme = self.context.config.get("settings", "theme")
        theme_layout = QHBoxLayout()
        theme_label = QLabel("Thème :")
        self.theme_combo = QComboBox()
        for name in THEMES:
            self.theme_combo.addItem(name)

        self.theme_combo.setCurrentText(self.initial_theme)
        self.apply_theme(self.initial_theme)
        self.theme_combo.currentTextChanged.connect(self.apply_theme)
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()

        tab2_layout.addLayout(theme_layout)
        tab2_layout.addLayout(button_layout)
        tab2_layout.addWidget(self.console_output)
        tab2_layout.addStretch()

        self.tabs.addTab(tab2, "Paramètres")

        # =========================
        # TYPES DE DOCUMENT
        # =========================

        types_frame = QFrame()
        types_vbox = QVBoxLayout(types_frame)
        lbl_types = QLabel("Types recherchés")
        types_vbox.addWidget(lbl_types)

        types_flow_widget = QWidget()
        types_flow_layout = FlowLayout()
        types_flow_widget.setLayout(types_flow_layout)
        types_vbox.addWidget(types_flow_widget)

        self.types_layout = types_flow_layout

        self.key_filter_actions = {}

        tab2_layout.addWidget(types_frame)


        # =========================
        # CHAMPS RECHERCHÉS
        # =========================

        fields_frame = QFrame()
        fields_vbox = QVBoxLayout(fields_frame)
        lbl_fields = QLabel("Champs utilisés pour la recherche")
        fields_vbox.addWidget(lbl_fields)

        flow_widget = QWidget()
        flow_layout = FlowLayout()
        flow_widget.setLayout(flow_layout)
        fields_vbox.addWidget(flow_widget)

        self.fields_layout = flow_layout

        self.field_actions = {}

        tab2_layout.addWidget(fields_frame)


        # =========================
        # FILTRES CHAMPS VIDES
        # =========================

        filters_frame = QFrame()
        filters_vbox = QVBoxLayout(filters_frame)
        lbl_filters = QLabel("Afficher seulement les documents avec champs vides")
        filters_vbox.addWidget(lbl_filters)

        filters_flow_widget = QWidget()
        filters_flow_layout = FlowLayout()
        filters_flow_widget.setLayout(filters_flow_layout)
        filters_vbox.addWidget(filters_flow_widget)

        self.empty_keys_layout = filters_flow_layout

        self.empty_filters = {}

        tab2_layout.addWidget(filters_frame)

        self.sort_order_combo = QComboBox()
        self.sort_order_combo.addItem("Trier par ordre alphabétique")
        self.sort_order_combo.addItem("Trier par date de modification")
        # Défaut : trier par date de modification
        self.sort_order_combo.setCurrentIndex(1)
        self.sort_order_combo.currentIndexChanged.connect(self.update_results)
        left_layout.addWidget(self.sort_order_combo)

        # =========================
        # SHORTCUTS ONGLETS
        # =========================

        self.shortcut_tab_1 = QShortcut(QKeySequence("Ctrl+&"), self)
        self.shortcut_tab_1.activated.connect(self.go_tab_1)

        self.shortcut_tab_2 = QShortcut(QKeySequence("Ctrl+é"), self)
        self.shortcut_tab_2.activated.connect(self.go_tab_2)


    def go_tab_1(self):
        self.tabs.setCurrentIndex(0)
        QTimer.singleShot(0, self.search_input.setFocus)
    
    def go_tab_2(self):
        self.tabs.setCurrentIndex(1)

    def apply_theme(self, name: str):
        
        stylesheet = THEMES.get(name, "")
        app = QApplication.instance()
        if app is not None:
            app.setStyleSheet(stylesheet)
        # Régénérer le HTML après que Qt ait appliqué la nouvelle palette
        QTimer.singleShot(50, self.metadata_view.refresh_theme)

        self.context.config.set("settings", "theme", value=name)

    def schedule_search(self):
        self.search_timer.start(300)  # délai en millisecondes

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

    def eventFilter(self, obj, event):
        """Intercept key presses on the results list so that Up/Down
        act like a click (chargent l'item courant).
        """
        try:
            if obj is self.search_input and event.type() == QEvent.KeyPress:#type:ignore[reportAttributeAccessIssue]
                if event.key() == Qt.Key_Down:#type:ignore[reportAttributeAccessIssue]
                    if self.results_list.count() > 0:
                        self.results_list.setFocus()
                        self.results_list.setCurrentRow(0)
                        self._load_current_item_if_any()
                    return True
            if obj is self.results_list and event.type() == QEvent.KeyPress:#type:ignore[reportAttributeAccessIssue]
                key = event.key()
                if key in (Qt.Key_Up, Qt.Key_Down):#type:ignore[reportAttributeAccessIssue]
                    # Schedule loading after the key event is processed
                    QTimer.singleShot(0, self._load_current_item_if_any)
                elif key in (Qt.Key_Return, Qt.Key_Enter):#type:ignore[reportAttributeAccessIssue]
                    item = self.results_list.currentItem()
                    if item is not None:
                        self.open_pdf_with_pdfxchange(item)
                    return True
        except Exception:
            pass
        return super().eventFilter(obj, event)

    def _load_current_item_if_any(self):
        item = getattr(self.results_list, 'currentItem')()
        if item is not None:
            try:
                self.load_pdf(item)
            except Exception:
                pass

    def load_json_only(self):
        try:
            data = self.context.repository.load()
        except Exception as e:
            QMessageBox.critical(self, "Erreur JSON", str(e))
            data = {}

        self.rebuild_types_menu(data)
        self.rebuild_fields_menu(data)
        self.rebuild_empty_keys_menu()

    def check_all_fields(self):
        for action in self.field_actions.values():
            action.setChecked(True)
        self.update_results()


    def uncheck_all_fields(self):
        for action in self.field_actions.values():
            action.setChecked(False)
        self.update_results()

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def rebuild_types_menu(self, data):
        self.clear_layout(self.types_layout)
        self.key_filter_actions = {}

        prefixes = set()
        for key in data.keys():
            prefix = key.split()[0]
            prefixes.add(prefix)

        for prefix in sorted(prefixes):
            cb = QCheckBox(prefix)
            cb.setChecked(True)
            cb.stateChanged.connect(self.update_results)
            self.types_layout.addWidget(cb)
            self.key_filter_actions[prefix] = cb

    def rebuild_fields_menu(self, data):
        self.clear_layout(self.fields_layout)
        self.field_actions = {}

        all_keys = set()
        for infos in data.values():
            all_keys.update(infos.keys())

        for key in sorted(all_keys):
            cb = QCheckBox(camel_to_sentence(key))
            cb.setChecked(True)
            cb.stateChanged.connect(self.update_results)
            self.fields_layout.addWidget(cb)
            self.field_actions[key] = cb

    def rebuild_empty_keys_menu(self):
        self.clear_layout(self.empty_keys_layout)
        self.empty_filters = {}

        keys = self.context.config.get("settings", "tex non optionnal keys")
        for key in keys:
            cb = QCheckBox(camel_to_sentence(key))
            cb.setChecked(False)
            cb.stateChanged.connect(self.update_results)
            self.empty_keys_layout.addWidget(cb)
            self.empty_filters[key] = cb

    def add_menu_action(
            self,
            menu: QMenu,
            text: str,
            callback,
            item,
            enabled: bool = True,
        ):
            action = QAction(text, self)
            action.setEnabled(enabled)
            action.triggered.connect(
                lambda checked=False, cb=callback, it=item: cb(it)
            )
            menu.addAction(action)
            return action

    def show_results_context_menu(self, position):
        item = self.results_list.itemAt(position)
        if item is None:
            return

        self.results_list.setCurrentItem(item)

        menu = QMenu(self)

        copy_enonce_action = self.add_menu_action(
            menu,
            "Copier l'exemple minimal LaTeX",
            self.copy_enonce_for_item,
            item,
            True
        )

        open_tex_action = self.add_menu_action(
            menu,
            "Ouvrir le fichier .tex dans VS Code",
            self.open_tex_in_vscode,
            item,
            self.context.config.get_exe_by_key('code') is not Path()
        )

        open_pdf_adobe_action = self.add_menu_action(
            menu,
            "Ouvrir le fichier PDF dans Adobe Reader",
            self.open_pdf_with_adobe,
            item,
            self.context.config.get_exe_by_key('adobe') is not None
        )

        open_pdf_xchange_action = self.add_menu_action(
            menu,
            "Ouvrir le fichier PDF dans PDF XChange",
            self.open_pdf_with_pdfxchange,
            item,
            self.context.config.get_exe_by_key('pdf_xchange') is not None
        )

        open_pdf_okular_action = self.add_menu_action(
            menu,
            "Ouvrir le fichier PDF dans Okular",
            self.open_pdf_with_okular,
            item,
            self.context.config.get_exe_by_key('okular') is not None
        )

        menu.addAction(copy_enonce_action)
        menu.addAction(open_tex_action)
        menu.addAction(open_pdf_xchange_action)
        menu.addAction(open_pdf_adobe_action)
        menu.addAction(open_pdf_okular_action)
        menu.exec(self.results_list.viewport().mapToGlobal(position))

    def open_pdf_with_adobe(self, item):
        adobe_exe_path = self.context.config.get_exe_by_key("adobe")
        doc_dict = self.context.repository.get_doc_by_key(item.text())
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
        pdf_xchange_exe_path = self.context.config.get_exe_by_key('pdf_xchange'),
        doc_dict = self.context.repository.get_doc_by_key(item.text())
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
        okular_exe_path = self.context.config.get_exe_by_key('okular')
        doc_dict = self.context.repository.get_doc_by_key(item.text())
        pdf_path = Path(doc_dict.get("pdf", "")).resolve()

        if not pdf_path.exists():
            QMessageBox.warning(self, "Fichier introuvable", f"Fichier PDF introuvable\n{pdf_path}")
            return

        try:
            self.context.process_service.open_with(okular_exe_path, pdf_path)
        except OSError as error:
            QMessageBox.critical(self, "Erreur Okular", str(error))

    def open_tex_in_vscode(self, item):
        code_path_exe = self.context.config.get_exe_by_key("code")
        doc_dict = self.context.repository.get_doc_by_key(item.text())
        tex_path = Path(doc_dict.get("tex", "")).resolve()

        if not tex_path.exists():
            QMessageBox.warning(self, "Fichier introuvable", f"Fichier .tex introuvable\n{tex_path}")
            return

        try:
            self.context.process_service.open_with(code_path_exe, tex_path)
        except OSError as error:
            QMessageBox.critical(self, "Erreur VS Code", str(error))

    def build_search_filters(self) -> SearchFilters:

        return SearchFilters(
            pattern=self.search_input.text().strip(),
            active_prefixes=[
                prefix
                for prefix, cb in self.key_filter_actions.items()
                if cb.isChecked()
            ],
            active_fields=[
                field
                for field, cb in self.field_actions.items()
                if cb.isChecked()
            ],
            empty_fields=[
                field
                for field, cb in self.empty_filters.items()
                if cb.isChecked()
            ],
            sort_mode=self.sort_order_combo.currentIndex(),
        )

    def update_results(self):

        filters = self.build_search_filters()

        results = self.search_controller.search(filters)

        self.results_list.clear()

        for key, _ in results:
            self.results_list.addItem(key)
    # ======================================
    # PDF
    # ======================================
    def load_pdf(self, item):

        key = item.text()

        pdf_path = Path(
            self.context.repository
            .get_doc_by_key(key)
            .get("preview", "")
        )

        if not pdf_path.exists():
            QMessageBox.critical(
                self,
                "Erreur",
                f"Fichier PDF introuvable\n{pdf_path}"
            )
            return

        self.pdf_viewer.document.load(str(pdf_path))

        document = self.context.repository.get_doc_by_key(key)

        self.metadata_view.show_document(document)

        self.current_enonce = document.get(
            "enonce",
            ""
        )

    def copy_enonce_for_item(self, item):
        doc_dict = self.context.repository.get_doc_by_key(item.text())
        enonce = doc_dict.get("enonce", "")

        if not enonce:
            QMessageBox.information(self, "Exemple minimal", "Aucun énoncé LaTeX n'est disponible pour cet item")
            return

        clipboard = QGuiApplication.clipboard()
        clipboard.setText(enonce)
        QMessageBox.information(self, "Exemple minimal", "Exemple minimal copié dans le presse papier")
    
    def reload_check_database(self):

        self.thread = QThread() # pyright: ignore[reportAttributeAccessIssue]
        self.worker = DatabaseWorker()

        self.worker.moveToThread(self.thread) # pyright: ignore[reportArgumentType]

        self.thread.started.connect(self.worker.run) # pyright: ignore[reportAttributeAccessIssue]
        self.worker.message.connect(self.console_output.appendPlainText)
        self.worker.finished.connect(self.database_finished)

        self.worker.finished.connect(self.thread.quit) # pyright: ignore[reportAttributeAccessIssue]
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater) # pyright: ignore[reportAttributeAccessIssue]

        self.thread.start() # pyright: ignore[reportAttributeAccessIssue]
    
    def database_finished(self, errors, warnings):
        self.console_output.appendPlainText(f"\nFinished\nErrors: {errors}\nWarnings: {warnings}")
        self.load_json_only()
        QMessageBox.information(
            self, "Chargement de la base de donée",
            f"Base de données chargée avec {errors} erreurs et {warnings} warnings LaTeX"
            )

class DatabaseWorker(QObject):
    message = Signal(str)
    finished = Signal(int, int)

    def run(self):
        def log(msg):
            self.message.emit(msg)

        update_code_index(logger=log)
        update_previews(logger=log)
        errors, warnings = check_database(logger=log)
        errors_sup, warnings_sup = 0, 0
        if errors == 0:
            errors_sup, warnings_sup = update_json(logger=log)
        errors += errors_sup
        warnings += warnings_sup

        self.finished.emit(errors, warnings)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(THEMES["Fusion Modern Dark Red"])  # thème par défaut

    context = create_context()
    window = RegexPDFSearchApp(context)
    window.show()
    window.load_json_only()
    sys.exit(app.exec())
