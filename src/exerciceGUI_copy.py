import re
import sys
import json
import subprocess
from pathlib import Path
from src.tools import CONFIG, LATEX_DIR, camel_to_sentence, get_exe_path
from src.qss import soothing
from src.update_data_index import update_json
from src.check_database import check_database
from src.extract_preview import update_previews

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QListWidget, QLabel, QMessageBox,
    QSplitter, QFrame, QPushButton, QPlainTextEdit,
    QTabWidget, QCheckBox
)
from PySide6.QtCore import Qt, QObject, QThread, Signal, QTimer
from PySide6.QtPdf import QPdfDocument
from PySide6.QtPdfWidgets import QPdfView
from PySide6.QtGui import QWheelEvent, QGuiApplication, QAction

def open_pdf_default(pdf_path):
    subprocess.Popen(["cmd", "/c", "start", "", pdf_path])

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

        # self.smart_regex_checkbox = QCheckBox("Recherche multi-mots (AND automatique)")
        # self.smart_regex_checkbox.setChecked(False)
        # self.smart_regex_checkbox.stateChanged.connect(self.update_results)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Recherche (regex)")
        self.search_input.textChanged.connect(self.schedule_search)

        self.results_list = QListWidget()
        self.results_list.itemClicked.connect(self.load_pdf)
        self.results_list.itemDoubleClicked.connect(self.on_item_double_clicked)

        # self.field_button = QToolButton()
        # self.field_button.setText("Champs recherchés")
        # self.field_button.setPopupMode(QToolButton.InstantPopup)

        # self.field_menu = QMenu(self)
        # self.field_button.setMenu(self.field_menu)

        # self.key_filter_button = QToolButton()
        # self.key_filter_button.setText("Types recherchés")
        # self.key_filter_button.setPopupMode(QToolButton.InstantPopup)

        # self.key_filter_menu = QMenu(self)

        # self.key_filter_button.setMenu(self.key_filter_menu)

        # left_layout.addWidget(self.smart_regex_checkbox)
        left_layout.addWidget(self.search_input)
        left_layout.addWidget(self.results_list)
        # left_layout.addWidget(self.field_button)
        # left_layout.addWidget(self.key_filter_button)

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

        right_layout.addWidget(self.pdf_view)

        info_frame = QFrame()
        info_layout = QVBoxLayout(info_frame)

        self.copy_button = QPushButton("Copier l'exemple minimal LaTeX")
        self.copy_button.clicked.connect(self.copy_enonce)

        info_layout.addWidget(self.copy_button)
        self.info_layout = info_layout

        right_layout.addWidget(info_frame)
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

        tab2_layout.addLayout(button_layout)
        tab2_layout.addWidget(self.console_output)
        tab2_layout.addStretch()

        self.tabs.addTab(tab2, "Paramètres")

        # =========================
        # TYPES DE DOCUMENT
        # =========================

        types_frame = QFrame()
        self.types_layout = QHBoxLayout(types_frame)

        self.key_filter_actions = {}
    
        tab2_layout.addWidget(types_frame)


        # =========================
        # CHAMPS RECHERCHÉS
        # =========================

        fields_frame = QFrame()
        self.fields_layout = QHBoxLayout(fields_frame)

        self.field_actions = {}

        tab2_layout.addWidget(fields_frame)


        # =========================
        # FILTRES CHAMPS VIDES
        # =========================

        filters_frame = QFrame()
        self.empty_keys_layout = QHBoxLayout(filters_frame)

        self.empty_filters = {}

        tab2_layout.addWidget(filters_frame)

    def schedule_search(self):
        self.search_timer.start(300)  # délai en millisecondes

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
        label = QLabel("Types recherchés")
        self.types_layout.addWidget(label)

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
        
        self.types_layout.addStretch()

    def rebuild_fields_menu(self):
        self.clear_layout(self.fields_layout)
        label = QLabel("Champs utilisés pour la recherche")
        self.fields_layout.addWidget(label)

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
        
        self.fields_layout.addStretch()

    def rebuild_empty_keys_menu(self):

        self.clear_layout(self.empty_keys_layout)
        label = QLabel("Afficher seulement les documents avec champs vides")
        self.empty_keys_layout.addWidget(label)

        self.empty_filters = {}

        keys = CONFIG['parameters']['tex non optionnal keys']

        for key in keys:
            cb = QCheckBox(camel_to_sentence(key))
            cb.setChecked(False)
            cb.stateChanged.connect(self.update_results)

            self.empty_keys_layout.addWidget(cb)
            self.empty_filters[key] = cb

        self.empty_keys_layout.addStretch()

    def on_item_double_clicked(self, item):
        doc_dict = self.data[item.text()]
        pdf_path = doc_dict['pdf']
        if doc_dict['type'] in CONFIG['parameters']['open with adobe']:
            try:
                adobe = get_exe_path('adobe')
                cmd = f"{adobe} /F {pdf_path}"
                subprocess.Popen(cmd)
            except FileNotFoundError:
                open_pdf_default(pdf_path)
        else:
            open_pdf_default(pdf_path)

    def update_results(self):
        pattern = self.search_input.text().strip()
        self.results_list.clear()

        if not pattern:
            return

        # =========================
        # Transformation multi-mots
        # =========================
        # if self.smart_regex_checkbox.isChecked():

        #     words = pattern.split()

        #     try:
        #         pattern = "".join(f"(?=.*{re.escape(w)})" for w in words)
        #         regex = re.compile(pattern, re.IGNORECASE)
        #     except re.error:
        #         return

        # else:
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

        for key, infos in self.data.items():
            prefix = key.split()[0]

            if prefix not in active_prefixes:
                continue

            # =========================
            # Filtre champs vides
            # =========================

            skip = False

            for field, checkbox in self.empty_filters.items():
                if checkbox.isChecked():
                    value = infos.get(field, "")
                    if value not in ["", None, []]:
                        skip = True
                        break

            if skip:
                continue

            searchable_parts = []
            for field in active_fields:
                value = infos.get(field, "")
                if isinstance(value, list):
                    searchable_parts.extend(str(v) for v in value)
                else:
                    searchable_parts.append(str(value))

            if regex.search(" ".join(searchable_parts)):
                self.results_list.addItem(f"{key}")

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

        # 🔥 Nettoyer anciens labels (tout sauf le bouton copy)
        while self.info_layout.count() > 1:
            widget = self.info_layout.takeAt(1).widget() # pyright: ignore[reportOptionalMemberAccess]
            if widget:
                widget.deleteLater()

        # 🔥 Recréer les labels
        for label_key, label_value in datas.items():
            if label_key in ['type', 'id', 'pdf', 'enonce', 'tex', 'preview']:
                continue

            label = QLabel()
            label.setWordWrap(True)

            if isinstance(label_value, str):
                label_text = f"<b>{camel_to_sentence(label_key)} :</b> {label_value}"
            elif isinstance(label_value, list):
                label_text = "<br>".join(
                    [f"<b>{camel_to_sentence(label_key)} :</b>"] + [f"- {v}" for v in label_value]
                )
            else:
                label_text = f"<b>{camel_to_sentence(label_key)} :</b> {label_value}"

            label.setText(label_text)
            self.info_layout.addWidget(label)

        self.current_enonce = datas.get("enonce", "")

    def copy_enonce(self):
        if hasattr(self, "current_enonce") and self.current_enonce:
            clipboard = QGuiApplication.clipboard()
            clipboard.setText(self.current_enonce)
            QMessageBox.information(self, "Exemple minimal", "Exemple minimal copié")
    
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

        update_previews(logger=log)
        errors, warnings = check_database(logger=log)
        if errors == 0:
            update_json(logger=log)

        self.finished.emit(errors, warnings)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(soothing)
    window = RegexPDFSearchApp(LATEX_DIR / "catalogues" / "data_index.json")
    window.show()
    window.load_json_only()
    sys.exit(app.exec())
    