from assistant_progression.services.html_service import HtmlService
from assistant_progression.services.catalogue_service import CatalogueService
from assistant_progression.services.persistence_service import PersistenceService
from assistant_progression.services.export_service import ExportService
from assistant_progression.services.undo_redo_service import UndoRedoService, record_undo
from assistant_progression.services.theme_service import ThemeService
from assistant_progression.services.progression_analysis_service import ProgressionAnalysisService 
from assistant_progression.services.progression_service import ProgressionService
from assistant_progression.services.search_service import SearchService
from assistant_progression.services.regex_service import SearchLineEdit
from assistant_progression.utils.textools import update_code_index
from assistant_progression.utils.resolve import (
    KATEX_DIR, CODE_INDEX_DIR,
    DEFAULT_PROG_DIR, PROGRESSION_EXPORT_DIR,
    CODE_INDEX_FILE_PATH, CONFIG_PATH,
    resolve_executable
)

import re
import json
import subprocess
from pathlib import Path

from PySide6.QtCore import (
    Qt,
    QUrl
)
from PySide6.QtGui import (
    QAction,
    QKeySequence,
    QShortcut
)
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QComboBox,
    QMenuBar,
    QMenu,
    QSplitter,
    QTreeWidget,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QDialog,
)
from PySide6.QtWebEngineWidgets import QWebEngineView

class MainWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.currentFile = None

        self.persistence_service = PersistenceService()
        self.config = self.persistence_service.load_config()
        self.settings = self.config.get("settings", {})
        self.init_window_and_settings()
        self.init_services()

        self.main_layout = QHBoxLayout(self)

        self._preview_theme = None
        self._saved_theme = None
        self._theme_committed = False
        self.theme_service.apply(self)

        self.init_regex_pannel()
        self.init_preview_pannel()
        self.init_progression_pannel()
        self.init_menu()
        self.init_splitters()
        self.init_connect_signals()
        self.init_undo_redo()

        self.update_type_filter()
        self.update_search()
        self.search.setFocus()

    def init_services(self):

        # Services génériques

        self.html_service = HtmlService()

        self.export_service = ExportService()

        self.undo_redo = UndoRedoService()

        # Catalogue

        self.catalogue_service = CatalogueService(
            self.data,
            self.config["catalogues"]["codes"]
        )

        # Recherche

        self.search_service = SearchService(
            self.catalogue_service
        )

        # Analyse progression

        self.analysis_service = ProgressionAnalysisService(
            self.catalogue_service
        )

        # Progression

        self.progression_service = ProgressionService(
            self.catalogue_service,
            self.analysis_service,
            self.config
        )

        # Thèmes
        theme_name = (
            self.settings
            .get("current", {})
            .get("theme", "Fusion Crimson")
        )

        self.theme_service = ThemeService(
            themes=self.settings["themes"],
            default_theme=theme_name,
        )

        self.theme_service.apply(self)
    def init_connect_signals(self):

        self.search.textChanged.connect(
            lambda _: self.update_search()
        )

        self.catalogue_combo.currentTextChanged.connect(
            self.catalogue_changed
        )

        self.type_combo.currentTextChanged.connect(
            lambda _: self.update_search()
        )

        self.view_mode_combo.currentTextChanged.connect(
            lambda _: self.refresh_view()
        )

        self.list_widget.currentRowChanged.connect(
            self.show_entry
        )

        self.progression.itemClicked.connect(
            self.show_usage
        )


        self.add_button.clicked.connect(
            self.add_selected_item
        )
        add_button_action = QAction(self)
        add_button_action.setShortcut("Ctrl+i")
        add_button_action.triggered.connect(
            self.add_selected_item
        )
        self.addAction(add_button_action)

        self.delete_button.clicked.connect(
            self.delete_progression_item
        )
        delete_button_action = QAction(self)
        delete_button_action.setShortcut("Ctrl+D")
        delete_button_action.triggered.connect(
            self.delete_progression_item
        )
        self.addAction(delete_button_action)

        self.unused_button.clicked.connect(
            self.show_unused_items
        )
        unused_button_action = QAction(self)
        unused_button_action.setShortcut("Ctrl+U")
        unused_button_action.triggered.connect(
            self.show_unused_items
        )
        self.addAction(unused_button_action)

        self.add_level_button.clicked.connect(
            self.add_level
        )

        self.add_chapter_button.clicked.connect(
            self.add_chapter
        )

        self.add_seance_button.clicked.connect(
            self.add_seance
        )

        self.progression.currentItemChanged.connect(
            self.update_buttons_state
        )

        self.update_buttons_state()

        set_left_focus_action = QAction(self)
        set_left_focus_action.setShortcut("Ctrl+Left")
        set_left_focus_action.triggered.connect(
            lambda: self.set_focus('left')
        )
        self.addAction(set_left_focus_action)

        set_right_focus_action = QAction(self)
        set_right_focus_action.setShortcut("Ctrl+Right")
        set_right_focus_action.triggered.connect(
            lambda: self.set_focus('right')
        )
        self.addAction(set_right_focus_action)

    def set_focus(self, side):
        if side == 'left':
            self.list_widget.setFocus()
        if side == 'right':
            self.progression.setFocus()

    def init_undo_redo(self): 
        QShortcut(QKeySequence("Alt+Up"), self,
          activated=lambda: self.move_current_item(-1))

        QShortcut(QKeySequence("Alt+Down"), self,
                activated=lambda: self.move_current_item(+1))
    
        QShortcut(
            QKeySequence.Undo,
            self,
            activated=self.undo
        )

        QShortcut(
            QKeySequence.Redo,
            self,
            activated=self.redo
        )

    def reload_data(self):
        if CODE_INDEX_FILE_PATH == Path():
            self.data = {}
        else:
            with open(CODE_INDEX_FILE_PATH, encoding="utf-8") as f:
                self.data = json.load(f)
        
        self.catalogue_service = CatalogueService(
            self.data,
            self.config["catalogues"]["codes"]
        )

        self.search_service = SearchService(
            self.catalogue_service
        )

        self.analysis_service = ProgressionAnalysisService(
            self.catalogue_service
        )

        self.progression_service = ProgressionService(
            self.catalogue_service,
            self.analysis_service,
            self.config
        )

    def init_window_and_settings(self):
        self.setWindowTitle(self.settings.get("main window title", "Assistant de progression"))
        self.resize(1400, 800)

        self.reload_data()

        shortcut = QShortcut(QKeySequence("Ctrl+Q"), self)
        shortcut.activated.connect(self.close)

    def init_splitters(self):
        self.splitter = QSplitter(Qt.Horizontal)

        self.splitter.addWidget(self.left_widget)
        self.splitter.addWidget(self.preview_widget)
        self.splitter.addWidget(self.right_widget)
        self.tabs = [self.left_widget, self.preview_widget, self.right_widget]

        self.splitter.setSizes([400, 800, 300])

        
        self.main_layout.addWidget(self.splitter)

    def init_regex_pannel(self):

        self.catalogue_combo = QComboBox()
        self.type_combo = QComboBox()

        self.view_mode_combo = QComboBox()
        self.view_mode_combo.addItems([
            "Afichage unique",
            "Liste complète filtrée"
        ])

        self.list_widget = QListWidget()
        self.search = SearchLineEdit(self.list_widget)

        self.search.setPlaceholderText("Regex sur code ou contenu")

        self.search_service.populate_filters(
            self.catalogue_combo
        )

        default_code = self.settings["current"]["code"]
        default_label =self.catalogue_service.display_name(default_code)

        index = self.catalogue_combo.findText(default_label)
        if index >= 0:
            self.catalogue_combo.setCurrentIndex(index)

        left = QVBoxLayout()

        left.addWidget(self.catalogue_combo)
        left.addWidget(self.type_combo)
        left.addWidget(self.view_mode_combo)
        left.addWidget(self.search)
        left.addWidget(self.list_widget)

        left_widget = QWidget()
        left_widget.setLayout(left)
        self.left_widget = left_widget

    def init_preview_pannel(self):
        self.preview = QWebEngineView()
        self.preview_widget = self.preview

    def begin_theme_preview(self):
        self._saved_theme = self.theme_service.get_current_theme_name()
        self._theme_committed = False
        self._preview_theme = None
    
    def end_theme_preview(self):
        if self._theme_committed:
            return

        if self._saved_theme:
            self.theme_service.set_theme(self._saved_theme)
            self.theme_service.apply(self)
            self.refresh_view()

    def preview_theme(self, name):
        self.theme_service.set_theme(name)
        self.theme_service.apply(self)
        self.refresh_view()

    def commit_theme(self, name):
        self._theme_committed = True

        # 1. runtime state
        self.theme_service.set_theme(name)

        # 2. apply immédiatement (IMPORTANT)
        self.theme_service.apply(self)
        self.refresh_view()

        # 3. persist config.json
        self.persistence_service.save_config_value(
            "settings",
            "current",
            "theme",
            value=name
        )

        # 4. sync local config memory
        self.settings.setdefault("current", {})
        self.settings["current"]["theme"] = name
        print("THEME LOADED =", name)
        print("SETTINGS =", self.settings)

    def apply_current_theme(self):
        self.theme_service.apply(self)
        self.refresh_view()

    def init_menu(self):

        menu_bar = QMenuBar(self)

        edit_menu = QMenu("Édition", self)

        theme_menu = QMenu("Thème", self)
        theme_menu.aboutToShow.connect(self.begin_theme_preview)
        theme_menu.aboutToHide.connect(self.end_theme_preview)

        param_menu_action = QAction("Paramètres", self)
        edit_menu.addAction(param_menu_action)
        param_menu_action.triggered.connect(
            self.open_config_file
        )
        
        file_menu = QMenu("Fichier", self)
        update_menu = QMenu("Mise à jour", self)

        load_action = QAction("Charger une progression", self)
        save_action = QAction("Sauvegarder", self)
        save_under_action = QAction("Sauvegarder sous", self)
        export_progression_action = QAction("Exporter la progression", self)

        update_code_index_action = QAction("Mettre à jour l'index des codes", self)
        update_menu.addAction(update_code_index_action)
        update_code_index_action.triggered.connect(self.update_code_labels)

        load_action.setShortcut(QKeySequence.Open)
        save_action.setShortcut(QKeySequence.Save)
        save_under_action.setShortcut(QKeySequence.SaveAs)
        export_progression_action.setShortcut("Ctrl+E")

        load_action.triggered.connect(self.load_progression)
        save_action.triggered.connect(self.save_progression)
        save_under_action.triggered.connect(self.save_on_progression)
        export_progression_action.triggered.connect(self.export_progression)

        file_menu.addAction(load_action)
        file_menu.addSeparator()
        file_menu.addAction(save_action)
        file_menu.addAction(save_under_action)
        file_menu.addSeparator()
        file_menu.addAction(export_progression_action)

        for theme_name in self.theme_service.get_theme_names():
            action = QAction(theme_name, self)
            action.triggered.connect(
                lambda checked=False, name=theme_name:
                self.commit_theme(name)
            )
            theme_menu.addAction(action)

            action.hovered.connect(
                lambda name=theme_name:
                    self.preview_theme(name)
            )

        edit_menu.addMenu(theme_menu)
        menu_bar.addMenu(file_menu)
        menu_bar.addMenu(edit_menu)
        menu_bar.addMenu(update_menu)
        self.main_layout.setMenuBar(menu_bar)

    def open_config_file(self):

        subprocess.run([str(resolve_executable("blocnote")), str(CONFIG_PATH)], check=False)

    def init_progression_pannel(self):

        self.progression = QTreeWidget()

        self.progression.setHeaderLabel("Progression annuelle")
        self.add_level_button = QPushButton("Ajouter un niveau")

        add_level_action = QAction(self)
        add_level_action.setShortcut("Ctrl+L")
        add_level_action.triggered.connect(
            self.add_level
        )

        self.addAction(add_level_action)

        self.add_chapter_button = QPushButton("Ajouter un chapitre")

        add_chapter_action = QAction(self)
        add_chapter_action.setShortcut("Ctrl+K")
        add_chapter_action.triggered.connect(self.add_chapter)

        self.add_seance_button = QPushButton("Ajouter une séance")

        add_seance_action = QAction(self)
        add_seance_action.setShortcut("Ctrl+M")
        add_seance_action.triggered.connect(self.add_seance)

        self.add_level_button.setToolTip("Ajouter un niveau (Ctrl+L)")
        self.add_chapter_button.setToolTip("Ajouter un chapitre (Ctrl+K)")
        self.add_seance_button.setToolTip("Ajouter une séance (Ctrl+M)")

        self.addAction(add_chapter_action)
        self.addAction(add_seance_action)

        self.add_button = QPushButton("Ajouter l'item sélectionné")
        self.add_button.setToolTip("Ajouter un item (Ctrl+I)")

        self.delete_button = QPushButton("Supprimer")
        self.delete_button.setToolTip("Supprimer l'item sélectionné (Ctrl+D)")

        self.unused_button = QPushButton("Afficher les items non utilisés")
        self.unused_button.setToolTip("Afficher les items non utilisés (Ctrl+U)")

        right = QVBoxLayout()

        right.addWidget(self.progression)
        right.addWidget(self.add_level_button)
        right.addWidget(self.add_chapter_button)
        right.addWidget(self.add_seance_button)
        right.addWidget(self.add_button)
        right.addWidget(self.delete_button)
        right.addWidget(self.unused_button)

        right_widget = QWidget()
        right_widget.setLayout(right)
        self.right_widget = right_widget

        self.progression_visible = True

        toggle_action = QAction(self)
        toggle_action.setShortcut("Ctrl+B")
        toggle_action.triggered.connect(self.toggle_progression_panel)

        self.addAction(toggle_action)

    # ---------------- VIEW SWITCH ----------------

    def toggle_progression_panel(self):
        if self.progression_visible:
            # mémorise la taille actuelle du splitter
            self._saved_sizes = self.splitter.sizes()

            # cache panneau droit
            self.right_widget.setVisible(False)

            # redistribue l'espace vers centre + gauche
            self.splitter.setSizes([400, 1000, 0])

            self.progression_visible = False

        else:
            self.right_widget.setVisible(True)

            # restaure tailles si possible
            if hasattr(self, "_saved_sizes"):
                self.splitter.setSizes(self._saved_sizes)
            else:
                self.splitter.setSizes([400, 800, 300])

            self.progression_visible = True

    def selected_catalogue(self):
        return self.search_service.selected_catalogue(
            self.catalogue_combo
        )

    def is_selected_catalogue_aut_obj_pro(self):
        selected_catalogue = self.selected_catalogue()
        return selected_catalogue in self.config["catalogues"].get(
            "aut obj pro catalogues"
            )

    def update_code_labels(self):
        update_code_index()
        self.reload_data()

        self.update_type_filter()
        self.update_search()

        QMessageBox.information(
            self,
            "Info",
            f"Updated code index at {CODE_INDEX_DIR / 'code_index.json'}"
        )

    @record_undo
    def add_chapter(self):

        item = self.progression_service.add_chapter(
            self.progression,
            self.selected_catalogue(),
            self.progression.currentItem()
        )

        if item:
            self.progression.editItem(item, 0)
        
        self.update_buttons_state()

    @record_undo
    def add_level(self):

        item = self.progression_service.add_level(
            self.progression
        )

        if item:
            self.progression.editItem(item, 0)
        
        self.update_buttons_state()

    def show_unused_items(self):

        unused = self.get_unused_entries()


        dialog = QDialog()

        dialog.setWindowTitle(
            "Items non utilisés"
        )

        dialog.resize(
            700,
            800
        )

        dialog_layout = QVBoxLayout()


        liste = QListWidget()


        for entry in unused:

            texte = (
                f'{entry.code} '
                f'[{entry.type}] '
                f'- {entry.text}'
            )

            liste.addItem(texte)


        dialog_layout.addWidget(liste)

        dialog.setLayout(dialog_layout)


        dialog.exec()


        # indispensable sinon Qt détruit la fenêtre
        self.unused_window = dialog

    def get_unused_entries(self):
        return self.analysis_service.get_unused_entries(
            self.progression,
            self.selected_catalogue()
        )

    def get_selected_code(self):
        row = self.list_widget.currentRow()

        if row < 0:
            return

        return self.current_matches[row]

    @record_undo
    def add_selected_item(self):

        entry = self.get_selected_code()
        if not entry:
            return

        item = self.progression_service.add_selected_item(
            self.progression,
            entry,
        )

        if item is None:
            QMessageBox.warning(self, "Warning", "Please select a chapter to add the item.")
        
        else:
            QMessageBox.information(self, "Info", f"Item {entry.code} added to the progression.")
    
    @record_undo
    def add_seance(self):

        item = self.progression_service.add_seance(
            self.progression
        )

        if item:
            self.progression.editItem(item, 0)
        
        self.update_buttons_state()

    @record_undo
    def move_current_item(self, delta):
        self.progression_service.move_item(self.progression, delta)

    def is_chapter(self, item):

        if item is None:
            return False

        # un chapitre possède un parent racine
        return (
            item.parent() is not None
            and item.data(0, Qt.UserRole) is None
        )
    
    def update_buttons_state(self):

        tree = self.progression

        self.add_level_button.setEnabled(
            self.progression_service.can_add_level(tree)
        )

        self.add_chapter_button.setEnabled(
            self.progression_service.can_add_chapter(
                tree,
                self.selected_catalogue()
            )
        )

        self.add_seance_button.setEnabled(
            self.progression_service.can_add_seance(tree)
        )

        item = tree.currentItem()

        self.add_button.setEnabled(
            self.is_chapter(item)
        )

    @record_undo
    def delete_progression_item(self):
        self.progression_service.delete_item(self.progression)
        self.update_buttons_state()
    def show_usage(self, item):

        code = item.data(0, Qt.UserRole)
        if not code:
            return

        locations = self.analysis_service.find_usage_locations(
            self.progression,
            code
        )

    def refresh_view(self):
        mode = self.view_mode_combo.currentText()

        if mode == "Liste complète filtrée":
            self.show_list_view()
        else:
            self.show_entry(self.list_widget.currentRow())

    def show_list_view(self):

        html_items = []

        for entry in self.current_matches:

            html_items.append(
                (
                    f"<b>{entry.code}</b> "
                    f"(<i>{self.catalogue_service.display_name(entry.catalogue)}</i>) "
                    f"{entry.text}"
                )
            )

        html = "<br>".join(html_items)

        self.preview.setHtml(
            self.html_service.render_list(html, self.theme_service.get_current_theme()),
            QUrl.fromLocalFile(str(KATEX_DIR.resolve()) + "/")
        )

    def set_theme(self, name):
        self.theme_service.set_theme(name)
        self.apply_current_theme()

    def update_type_filter(self):

        self.search_service.update_type_filter(
            self.catalogue_combo,
            self.type_combo
        )

    def catalogue_changed(self):
        self.update_type_filter()
        self.update_search()
        self.update_buttons_state()

    def update_search(self):

        regex_text = self.search.text()

        try:
            entries = self.search_service.search(
                self.catalogue_combo,
                self.type_combo,
                regex_text
            )

        except re.error:

            return

        self.current_matches = entries

        self.list_widget.clear()

        for entry in entries:

            self.list_widget.addItem(
                f"{entry.code} [{entry.type}]"
            )

        if entries:

            self.list_widget.setCurrentRow(0)

            self.refresh_view()

        else:

            self.preview.setHtml("")

    def show_entry(self, row):

        if self.view_mode_combo.currentText() == "Liste complète filtrée":
            return

        if row < 0 or row >= len(self.current_matches):
            return

        entry = self.current_matches[row]

        html = self.html_service.render_entry(
            code=entry.code,
            content=entry.text,
            catalogue=self.catalogue_service.display_name(entry.catalogue),
            source_type=self.catalogue_service.display_name(entry.type),
            theme=self.theme_service.get_current_theme(),
        )
        base_path = QUrl.fromLocalFile(str(KATEX_DIR.resolve()) + "/")

        with open('assistant_progression/log.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print(base_path)
        self.preview.setHtml(html, base_path)

    def load_progression(self):

        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Charger une progression",
            str(DEFAULT_PROG_DIR.resolve()),
            "JSON (*.json)"
        )

        if not filename:
            return

        with open(filename, encoding="utf8") as f:
            data = json.load(f)

        self.progression_service.restore(
            self.progression,
            data
        )
        self.currentFile = Path(filename)

        self.undo_redo.clear()

    def save_progression(self):

        if self.currentFile is None:
            return self.save_on_progression()

        data=self.progression_service.snapshot(
            self.progression
        )

        with open(
            self.currentFile,
            "w",
            encoding="utf8"
        ) as f:

            json.dump(
                data,
                f,
                indent=4,
                ensure_ascii=False
            )
        
        QMessageBox.information(self, "Info", f"File save at {str(self.currentFile)}")

    def save_on_progression(self):
        # Open a file dialog to select the save location and name
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Sauvegarder la progression",
            str(DEFAULT_PROG_DIR.resolve()),
            "JSON Files (*.json);;All Files (*)",
            options=options)
        
        if not filename:
            return  # User cancelled the dialog

        data = self.progression_service.snapshot(
            self.progression
        )

        self.persistence_service.save_progression(
            filename,
            data
        )
        self.currentFile = Path(filename)

    def undo(self):
        state = self.undo_redo.undo(self.progression_service.snapshot(
                self.progression
                ))
        if state is None:
            return

        self.progression_service.restore(
            self.progression,
            state
        )
        self.update_buttons_state()

    def redo(self):
        state = self.undo_redo.redo(self.progression_service.snapshot(
                self.progression
            ))
        if state is None:
            return

        self.progression_service.restore(
           self.progression,
            state
        )
        self.update_buttons_state()

    def export_progression(self):

        if self.currentFile is None:
            QMessageBox.warning(
                self,
                "Warning",
                "Please save the progression before exporting."
            )
            return

        data = self.persistence_service.load_progression(
            self.currentFile
        )

        if data is None:
            return

        tex_path = PROGRESSION_EXPORT_DIR

        tex_path = (
            tex_path
            / f"sequencage-{self.catalogue_combo.currentText().replace(' ', '_')}-{self.currentFile.stem}-structure.tex"
        )

        self.export_service.export_progression(
            tex_path,
            data,
            self.catalogue_service.labels
        )

        QMessageBox.information(
            self,
            "Info",
            f"Progression exported {tex_path}"
        )