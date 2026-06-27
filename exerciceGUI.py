import re
import sys
import json
import subprocess
import os
import html
from pathlib import Path
from src.tools import (
    CONFIG, LATEX_DIR, ADOBE_PATH, KATEX_DIR, PDF_XCHANGE_PATH,
    camel_to_sentence, get_exe
    )
from src.qss import soothing, vscode_dark

THEMES = {
    "VS Code Dark": vscode_dark,
    "Soothing": soothing,
}
# from src.update_code_index import update_code_index
from assistant_progression.utils.textools import update_code_index
from src.update_data_index import update_json
from src.check_database import check_database
from src.extract_preview import update_previews

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QListWidget, QLabel, QMessageBox,
    QSplitter, QFrame, QPushButton, QPlainTextEdit,
    QTabWidget, QCheckBox, QComboBox, QMenu, QLayout, QSizePolicy
)
from PySide6.QtCore import Qt, QObject, QThread, Signal, QTimer, QUrl, QEvent, QSize, QRect, QPoint
from PySide6.QtPdf import QPdfDocument
from PySide6.QtPdfWidgets import QPdfView
from PySide6.QtGui import QWheelEvent, QGuiApplication, QAction, QPalette
from PySide6.QtWebEngineWidgets import QWebEngineView


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
        return Qt.Orientations(0)#type:ignore[reportAttributeAccessIssue]

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


VSCODE_EXE = get_exe('code')
WORKSPACE_PATH = Path(__file__).resolve().parent / "texmaths.code-workspace"

def _path_to_uri(p):
    p = Path(p)
    try:
        return p.as_uri()
    except Exception:
        try:
            p = p.resolve()
            s = str(p)
        except Exception:
            s = str(p)
        if os.name == 'nt':
            s = s.replace('\\', '/')
            if not s.startswith('/'):
                s = '/' + s
            return 'file://' + s


def _wrap_with_katex_html(body_html: str, bg_color=None, fg_color=None) -> str:
    katex_dir = Path(KATEX_DIR)
    css_local = katex_dir / "katex.min.css"
    js_local = katex_dir / "katex.min.js"

    if css_local.exists():
        css_uri = _path_to_uri(css_local)
    else:
        css_uri = "https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css"

    if js_local.exists():
        js_uri = _path_to_uri(js_local)
    else:
        js_uri = "https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js"

    bg_css = f"background-color: {bg_color};" if bg_color else ""
    fg_css = f"color: {fg_color};" if fg_color else ""

    return f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<link rel="stylesheet" href="{css_uri}">
<style>
/* Prefer Latin Modern if available, otherwise fall back to common serif fonts */
@font-face {{
  font-family: 'Latin Modern';
  src: local('Latin Modern Roman'), local('Latin Modern'), local('LM Roman');
  font-style: normal;
}}
body {{ font-family: 'Latin Modern', 'Times New Roman', Times, serif; font-size:13px; line-height:1.25; margin:8px; {bg_css} {fg_css} }}
b {{ color: {fg_color or 'inherit'}; }}
.katex-raw {{ display: inline-block; vertical-align: middle; }}
/* Make KaTeX rendered math follow surrounding font sizing */
.katex {{ font-size: 1em; font-family: inherit !important; }}
.katex * {{ font-family: inherit !important; }}
</style>
</head>
<body>
{body_html}
<script src="{js_uri}"></script>
<script>
(function(){{
    function renderAll(){{
        document.querySelectorAll('.katex-raw').forEach(function(el){{
            var expr = el.getAttribute('data-expr') || '';
            var display = el.getAttribute('data-display') === '1';
            try {{
                el.innerHTML = katex.renderToString(expr, {{throwOnError:false, displayMode:display}});
            }} catch(e) {{
                el.textContent = expr;
            }}
        }});
    }}
    if (typeof katex !== 'undefined') {{
        renderAll();
    }} else {{
        window.addEventListener('load', renderAll);
    }}
}})();
</script>
</body>
</html>"""


def _escape_and_replace_latex(text: str) -> str:
    # Replace $$...$$ and $...$ with spans carrying data-expr and data-display
    parts = re.split(r'(\$\$.*?\$\$|\$.+?\$)', text, flags=re.DOTALL)
    out = []
    for part in parts:
        if not part:
            continue
        if part.startswith('$$') and part.endswith('$$') and len(part) >= 4:
            expr = part[2:-2]
            out.append(f'<span class="katex-raw" data-expr="{html.escape(expr, quote=True)}" data-display="1"></span>')
        elif part.startswith('$') and part.endswith('$') and len(part) >= 2:
            expr = part[1:-1]
            out.append(f'<span class="katex-raw" data-expr="{html.escape(expr, quote=True)}" data-display="0"></span>')
        else:
            out.append(html.escape(part).replace('\n', '<br/>'))
    return ''.join(out)

class ZoomablePdfView(QPdfView):
    def wheelEvent(self, event: QWheelEvent):
        if event.modifiers() == Qt.ControlModifier: # pyright: ignore[reportAttributeAccessIssue]
            delta = event.angleDelta().y()
            zoom_factor = self.zoomFactor()

            zoom_factor = zoom_factor * 1.1 if delta > 0 else zoom_factor / 1.1
            zoom_factor = max(0.2, min(zoom_factor, 5.0))

            self.setZoomMode(QPdfView.ZoomMode.Custom)
            self.setZoomFactor(zoom_factor)
            event.accept()
        else:
            super().wheelEvent(event)

class RegexPDFSearchApp(QWidget):
    def __init__(self, json_path):
        super().__init__()

        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.update_results)

        self.setWindowTitle("Recherche Regex PDF")
        self.resize(1200, 700)

        self.json_path = json_path
        self.data = {}

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

        self.pdf_document = QPdfDocument(self)
        self.pdf_view = ZoomablePdfView(self)
        self.pdf_view.setDocument(self.pdf_document)
        # self.pdf_view.setZoomMode(QPdfView.ZoomMode.FitInView)
        self.pdf_view.setPageMode(QPdfView.PageMode.MultiPage)
        self.pdf_view.setZoomMode(QPdfView.ZoomMode.FitToWidth)

        # Use a vertical splitter so the PDF (top) and HTML info (bottom)
        # are separated by a draggable splitter the user can resize.
        self.inner_splitter = QSplitter(Qt.Vertical)#type:ignore
        self.inner_splitter.addWidget(self.pdf_view)

        info_frame = QFrame()
        info_layout = QVBoxLayout(info_frame)
        self.info_layout = info_layout
        self.inner_splitter.addWidget(info_frame)

        # Persistent QWebEngineView for the info panel (avoid recreating it)
        try:
            self.info_view = QWebEngineView()
            self.last_info_html = None
            self.info_view.loadFinished.connect(self._on_info_loaded)
            self.info_layout.addWidget(self.info_view)
        except Exception:
            # Fallback: create a QLabel and a small wrapper that exposes `setHtml`
            lbl = QLabel()
            lbl.setWordWrap(True)
            lbl.setText("(Aperçu HTML indisponible — affichage texte)")
            self.info_layout.addWidget(lbl)

            class _LabelWrapper:
                def __init__(self, widget):
                    self._widget = widget

                def setHtml(self, html, base_url=None):
                    # QLabel supports basic rich text; if that fails, strip tags
                    try:
                        self._widget.setText(html)
                    except Exception:
                        import re as _re
                        self._widget.setText(_re.sub(r'<[^>]+>', '', html))

            self.info_view = _LabelWrapper(lbl)

        # Give PDF more initial space than the info panel (stretch factors)
        self.inner_splitter.setStretchFactor(0, 3)
        self.inner_splitter.setStretchFactor(1, 1)

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
        theme_layout = QHBoxLayout()
        theme_label = QLabel("Thème :")
        self.theme_combo = QComboBox()
        for name in THEMES:
            self.theme_combo.addItem(name)
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

    def _refresh_info_view(self):
        """Re-génère le HTML de la zone info avec les couleurs courantes de la palette."""
        if not getattr(self, '_last_body_html', None):
            return
        info_widget = self.info_layout.parentWidget()
        pal = info_widget.palette() if info_widget is not None else self.palette()
        try:
            bg_color = pal.color(QPalette.Window).name()  # type:ignore
            fg_color = pal.color(QPalette.WindowText).name()  # type:ignore
        except Exception:
            bg_color = None
            fg_color = None
        full_html = _wrap_with_katex_html(self._last_body_html, bg_color, fg_color)
        base = Path(KATEX_DIR)
        try:
            base_url = QUrl.fromLocalFile(str(base.resolve()))
        except Exception:
            base_url = QUrl()
        self.last_info_html = full_html
        try:
            self.info_view.setHtml(full_html, base_url)
        except Exception:
            pass

    def apply_theme(self, name: str):
        stylesheet = THEMES.get(name, "")
        app = QApplication.instance()
        if app is not None:
            app.setStyleSheet(stylesheet)
        # Régénérer le HTML après que Qt ait appliqué la nouvelle palette
        QTimer.singleShot(50, self._refresh_info_view)

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

    def _on_info_loaded(self, ok: bool):
        if not ok:
            print("[exerciceGUI] QWebEngineView failed to load HTML. Snippet:")
            if self.last_info_html:
                print(self.last_info_html[:2000])

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

    # ======================================
    # JSON
    # ======================================

    def load_json_only(self):
        try:
            with open(self.json_path, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        except Exception as e:
            QMessageBox.critical(self, "Erreur JSON", str(e))
            self.data = {}
            return

        self.rebuild_types_menu()
        self.rebuild_fields_menu()
        self.rebuild_empty_keys_menu()

    # ======================================
    # RECHERCHE
    # ======================================

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

    def rebuild_types_menu(self):
        self.clear_layout(self.types_layout)
        self.key_filter_actions = {}

        prefixes = set()
        for key in self.data.keys():
            prefix = key.split()[0]
            prefixes.add(prefix)

        for prefix in sorted(prefixes):
            cb = QCheckBox(prefix)
            cb.setChecked(True)
            cb.stateChanged.connect(self.update_results)
            self.types_layout.addWidget(cb)
            self.key_filter_actions[prefix] = cb

    def rebuild_fields_menu(self):
        self.clear_layout(self.fields_layout)
        self.field_actions = {}

        all_keys = set()
        for infos in self.data.values():
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

        keys = CONFIG['parameters']['tex non optionnal keys']
        for key in keys:
            cb = QCheckBox(camel_to_sentence(key))
            cb.setChecked(False)
            cb.stateChanged.connect(self.update_results)
            self.empty_keys_layout.addWidget(cb)
            self.empty_filters[key] = cb

    def show_results_context_menu(self, position):
        item = self.results_list.itemAt(position)
        if item is None:
            return

        self.results_list.setCurrentItem(item)

        menu = QMenu(self)
        menu.setStyleSheet(
            "QMenu::item:selected {"
            "background-color: rgba(0, 0, 0, 0.18);"
            "}"
        )

        copy_enonce_action = QAction("Copier l'exemple minimal LaTeX", self)
        copy_enonce_action.triggered.connect(lambda checked=False, selected_item=item: self.copy_enonce_for_item(selected_item))

        open_tex_action = QAction("Ouvrir le fichier .tex dans VS Code", self)
        open_tex_action.triggered.connect(lambda checked=False, selected_item=item: self.open_tex_in_vscode(selected_item))

        open_pdf_xchange_action = QAction("Ouvrir le fichier PDF dans PDF XChange", self)
        open_pdf_xchange_action.triggered.connect(lambda checked=False, selected_item=item: self.open_pdf_with_pdfxchange(selected_item))

        open_pdf_adobe_action = QAction("Ouvrir le fichier PDF dans Adobe Reader", self)
        open_pdf_adobe_action.triggered.connect(lambda checked=False, selected_item=item: self.open_pdf_with_adobe(selected_item))

        open_pdf_okular_action = QAction("Ouvrir le fichier PDF dans Okular", self)
        open_pdf_okular_action.triggered.connect(lambda checked=False, selected_item=item: self.open_pdf_with_okular(selected_item))

        menu.addAction(copy_enonce_action)
        menu.addAction(open_tex_action)
        menu.addAction(open_pdf_xchange_action)
        menu.addAction(open_pdf_adobe_action)
        menu.addAction(open_pdf_okular_action)
        menu.exec(self.results_list.viewport().mapToGlobal(position))

    def open_pdf_with_adobe(self, item):
        doc_dict = self.data[item.text()]
        pdf_path = Path(doc_dict['pdf']).resolve()
        cmd = 'cmd /c start "" "{}" "{}"'
        try:
            subprocess.Popen(cmd.format(ADOBE_PATH, pdf_path), shell=True)
            return
        except FileNotFoundError:
            QMessageBox.critical(
                self,
                "Erreur ouverture PDF",
                f"Impossible d'ouvrir le PDF avec Adobe Reader.\nChemin attendu: {ADOBE_PATH}\nFichier: {pdf_path}"
            )
            return

    def open_pdf_with_pdfxchange(self, item):
        doc_dict = self.data.get(item.text(), {})
        pdf_path = Path(doc_dict.get("pdf", "")).resolve()

        if not pdf_path.exists():
            QMessageBox.warning(self, "Fichier introuvable", f"Fichier PDF introuvable\n{pdf_path}")
            return

        try:
            subprocess.Popen([
                PDF_XCHANGE_PATH,
                '/A', "page=1&fullscreen=yes=OpenParameters",
                str(pdf_path)
                ])
        except OSError as error:
            QMessageBox.critical(self, "Erreur PDF XChange", str(error))

    def open_pdf_with_okular(self, item):
        doc_dict = self.data.get(item.text(), {})
        pdf_path = Path(doc_dict.get("pdf", "")).resolve()

        if not pdf_path.exists():
            QMessageBox.warning(self, "Fichier introuvable", f"Fichier PDF introuvable\n{pdf_path}")
            return

        try:
            subprocess.Popen([get_exe("okular"), str(pdf_path)])
        except OSError as error:
            QMessageBox.critical(self, "Erreur Okular", str(error))

    def open_tex_in_vscode(self, item):
        doc_dict = self.data.get(item.text(), {})
        tex_path = Path(doc_dict.get("tex", "")).resolve()

        if not tex_path.exists():
            QMessageBox.warning(self, "Fichier introuvable", f"Fichier .tex introuvable\n{tex_path}")
            return

        try:
            subprocess.Popen([str(VSCODE_EXE), "-r", str(WORKSPACE_PATH), str(tex_path)])
        except OSError as error:
            QMessageBox.critical(self, "Erreur VS Code", str(error))

    def update_results(self):
        pattern = self.search_input.text().strip()
        self.results_list.clear()

        if not pattern:
            return

        try:
            regex = re.compile(pattern, re.IGNORECASE)
        except re.error:
            return

        active_prefixes = [
            prefix for prefix, cb in self.key_filter_actions.items()
            if cb.isChecked()
        ]

        if not active_prefixes:
            return

        active_fields = [
            key for key, cb in self.field_actions.items()
            if cb.isChecked()
        ]

        matching_items = []

        for key, infos in self.data.items():
            prefix = key.split()[0]

            if prefix not in active_prefixes:
                continue

            # Filtre champs vides
            skip = False
            for field, checkbox in self.empty_filters.items():
                if checkbox.isChecked():
                    value = infos.get(field, "")
                    if value not in ["", None, []]:
                        skip = True
                        break
            if skip:
                continue

            # Rassembler les parties recherchables selon les champs actifs
            searchable_parts = []
            for field in active_fields:
                value = infos.get(field, "")
                if isinstance(value, list):
                    searchable_parts.extend(str(v) for v in value)
                else:
                    searchable_parts.append(str(value))

            if regex.search(" ".join(searchable_parts)):
                matching_items.append((key, infos))

        # Trier les éléments selon l'ordre choisi
        sort_index = self.sort_order_combo.currentIndex()

        if sort_index == 0:
            # Tri par ordre alphabétique
            matching_items.sort(key=lambda x: x[0].lower())  # Tri par nom
        elif sort_index == 1:
            # Tri par date de modification du fichier PDF
            matching_items.sort(key=lambda x: Path(x[1]["pdf"]).stat().st_mtime, reverse=True)

        # Ajouter les résultats triés dans la liste
        for item, _ in matching_items:
            self.results_list.addItem(item)

    # ======================================
    # PDF
    # ======================================

    def load_pdf(self, item):
        key = item.text()
        pdf_path = Path(self.data[key]["preview"])

        if not pdf_path.exists():
            QMessageBox.critical(self, f"Erreur", "Fichier PDF introuvable\n{pdf_path}")
            return

        self.pdf_document.load(str(pdf_path))
        # self.pdf_view.pageNavigator().jump(0)

        datas = self.data[key]

        # Préparer le contenu HTML + KaTeX (le widget `self.info_view` est persistant)
        html_parts = []
        for label_key, label_value in datas.items():
            if label_key in ['type', 'id', 'pdf', 'enonce', 'tex', 'preview']:
                continue
            title = f"<b>{camel_to_sentence(label_key)} :</b>"
            if isinstance(label_value, str):
                content = _escape_and_replace_latex(label_value)
                html_parts.append(f"<p>{title} {content}</p>")
            elif isinstance(label_value, list):
                items = "".join(f"<li>{_escape_and_replace_latex(str(v))}</li>" for v in label_value)
                html_parts.append(f"<p>{title}</p><ul>{items}</ul>")
            else:
                html_parts.append(f"<p>{title} {html.escape(str(label_value))}</p>")

        body_html = "\n".join(html_parts) if html_parts else "<p><i>Aucune information</i></p>"
        self._last_body_html = body_html
        # récupérer la couleur de fond du widget info (ou palette par défaut)
        info_widget = self.info_layout.parentWidget()
        if info_widget is not None:
            pal = info_widget.palette()
        else:
            pal = self.palette()
        try:
            bg_color = pal.color(QPalette.Window).name()#type:ignore
            fg_color = pal.color(QPalette.WindowText).name()#type:ignore
        except Exception:
            bg_color = None
            fg_color = None

        full_html = _wrap_with_katex_html(body_html, bg_color, fg_color)

        # setHtml on persistent info_view to avoid re-creating the engine
        base = Path(KATEX_DIR)
        try:
            base_url = QUrl.fromLocalFile(str(base.resolve()))
        except Exception:
            base_url = QUrl()

        self.last_info_html = full_html
        if getattr(self, 'info_view', None):
            try:
                self.info_view.setHtml(full_html, base_url)
            except Exception:
                print("[exerciceGUI] failed to setHtml on info_view")
        else:
            # Fallback: show plain text in a QLabel if QWebEngineView is unavailable
            fallback_label = QLabel()
            fallback_label.setWordWrap(True)
            # strip tags for a simple textual fallback
            text_only = re.sub(r'<[^>]+>', '', body_html)
            fallback_label.setText(text_only)
            self.info_layout.addWidget(fallback_label)

        self.current_enonce = datas.get("enonce", "")

    def copy_enonce_for_item(self, item):
        doc_dict = self.data.get(item.text(), {})
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
        if errors == 0:
            update_json(logger=log)

        self.finished.emit(errors, warnings)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(vscode_dark)  # thème par défaut
    window = RegexPDFSearchApp(LATEX_DIR / "catalogues" / "data_index.json")
    window.show()
    window.load_json_only()
    sys.exit(app.exec())
    