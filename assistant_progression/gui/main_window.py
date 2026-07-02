from assistant_progression.services.code_service import CodeService
from assistant_progression.services.catalogue_service import CatalogueService
from assistant_progression.services.persistence_service import PersistenceService
from assistant_progression.services.export_service import ExportService
from assistant_progression.services.undo_redo_service import UndoRedoService, record_undo
from assistant_progression.services.theme_service import ThemeService
from assistant_progression.services.progression_analysis_service import ProgressionAnalysisService 
from assistant_progression.services.progression_service import ProgressionService
from assistant_progression.services.search_service import SearchService
from assistant_progression.utils.textools import update_code_index
from assistant_progression.models.paths import Paths
from assistant_progression.gui.action import ActionDefinition
from assistant_progression.gui.actions_manager import ActionManager
from assistant_progression.gui.menus.theme_menu_builder import ThemeMenuBuilder
from assistant_progression.gui.menus.catalogue_menu_builder import CatalogueMenuBuilder
from assistant_progression.gui.panels.regex_panel import RegexPanel
from assistant_progression.gui.panels.preview_panel import PreviewPanel
from assistant_progression.gui.panels.progresion_panel import ProgressionPanel

import json
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QMenuBar,
    QMenu,
    QSplitter,
    QTreeWidget,
    QFileDialog,
    QMessageBox,
    QDialog,
)

class MainWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.currentFile = None

        self.persistence_service = PersistenceService()
        self.config = self.persistence_service.load_config()
        self.paths = Paths(self.config)
        self.settings = self.config.settings
        self.action_manager = ActionManager(self)
        self.init_window_and_settings()
        self.init_services()

        self.main_layout = QHBoxLayout(self)

        self._preview_theme = None
        self._saved_theme = None
        self._theme_committed = False
        self.theme_service.apply(self)

        self.register_actions()
        self.init_regex_panel()
        self.init_preview_panel()
        self.init_progression_pannel()
        self.init_connect_signals()
        self.init_menu()
        self.init_splitters()

        self.update_search()
        self.regex_panel.search_line.setFocus()

    def init_services(self):

        # Services génériques

        self.export_service = ExportService()

        self.undo_redo = UndoRedoService()

        # Thèmes
        theme_name = self.settings.current.theme

        self.theme_service = ThemeService(
            themes=self.settings.themes,
            default_theme=theme_name,
        )

    def init_connect_signals(self):

        self.regex_panel.list_widget.itemClicked.connect(
            self.show_usage
        )

        self.regex_panel.catalogue_combo.currentTextChanged.connect(
            self.catalogue_changed
        )

        self.regex_panel.view_mode_combo.currentTextChanged.connect(
            self.preview_panel.refresh_view
        )

        self.regex_panel.list_widget.currentRowChanged.connect(
            self.preview_panel.refresh_view
        )

        self.addAction(self.action_manager.action("set_left_focus"))
        self.addAction(self.action_manager.action("set_right_focus"))
        self.addAction(self.action_manager.action("close"))
        self.addAction(self.action_manager.action("undo"))
        self.addAction(self.action_manager.action("redo"))
        self.addAction(self.action_manager.action("move_item_up"))
        self.addAction(self.action_manager.action("move_item_down"))

    def set_left_focus(self):
        if self.regex_panel.last_focused is not None:
            self.regex_panel.last_focused.setFocus()
        else:
            self.regex_panel.search_line.setFocus()
    
    def set_right_focus(self):
        self.progression_panel.progression_tree.setFocus()

    def reload_data(self):
        code_index_file_path = self.paths.code_index_file
        if not code_index_file_path.exists():
            self.data = {}
        else:
            with open(code_index_file_path, encoding="utf-8") as f:
                self.data = json.load(f)
        
        self.code_service = CodeService(self.config.codes)

        self.catalogue_service = CatalogueService(
            self.data,
            self.config.catalogues
        )

        self.search_service = SearchService(
            self.code_service,
            self.catalogue_service
        )

        self.analysis_service = ProgressionAnalysisService(
            self.catalogue_service
        )

        self.progression_service = ProgressionService(
            self.code_service,
            self.catalogue_service,
            self.analysis_service,
            self.config
        )

    def init_window_and_settings(self):
        self.setWindowTitle(self.settings.main_window_title)
        self.resize(*self.settings.init_size.size)

        self.reload_data()

    def init_splitters(self):
        self.splitter = QSplitter(Qt.Horizontal)

        self.splitter.addWidget(self.regex_panel)
        self.splitter.addWidget(self.preview_panel)
        self.splitter.addWidget(self.progression_panel)
        self.tabs = [self.regex_panel, self.preview_panel, self.progression_panel]

        self.splitter.setSizes([400, 800, 300])

        
        self.main_layout.addWidget(self.splitter)

    def init_regex_panel(self):

        default_code = self.settings.current.code
        default_label =self.code_service.display_name(default_code)
        self.regex_panel = RegexPanel(
            self.search_service,
            default_label=default_label
        )
    
    def init_preview_panel(self):
        self.preview_panel = PreviewPanel(
            self.regex_panel,
            self.theme_service,
            self.code_service,
            self.paths.katex
        )

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
            self.preview_panel.refresh_view()

    def preview_theme(self, name):
        self.theme_service.set_theme(name)
        self.theme_service.apply(self)
        self.preview_panel.refresh_view()

    def commit_theme(self, name):
        self._theme_committed = True

        self.theme_service.set_theme(name)

        self.theme_service.apply(self)
        self.preview_panel.refresh_view()

        self.config.settings.current.theme = name
        self.persistence_service.save_config(self.config)

    def apply_current_theme(self):
        self.theme_service.apply(self)
        self.preview_panel.refresh_view()

    def init_menu(self):

        menu_bar = QMenuBar(self)

        edit_menu = QMenu("Édition", self)

        theme_menu = QMenu("Thème", self)
        theme_menu.aboutToShow.connect(self.begin_theme_preview)
        theme_menu.aboutToHide.connect(self.end_theme_preview)

        open_catalogue_menu = QMenu("Ouvrir un catalogue", self)
        self.catalogue_menu_builder = CatalogueMenuBuilder(
            self.catalogue_service,
            self.paths.texmf,
            self.config
        )
        self.catalogue_menu_builder.populate(open_catalogue_menu)

        progression_menu = QMenu("Progression", self)
        progression_menu.addAction(self.action_manager.action("add_selected_item"))
        progression_menu.addAction(self.action_manager.action("delete_selected_item"))
        progression_menu.addAction(self.action_manager.action("show_unused_items"))

        file_menu = QMenu("Fichier", self)
        update_menu = QMenu("Mise à jour", self)

        file_menu.addAction(self.action_manager.action("load_progression"))
        file_menu.addSeparator()
        file_menu.addAction(self.action_manager.action("save_progression"))
        file_menu.addAction(self.action_manager.action("save_as_progression"))
        file_menu.addSeparator()
        file_menu.addAction(self.action_manager.action("export_progression"))

        self.theme_menu_builder = ThemeMenuBuilder(
            self.theme_service,
            self.commit_theme,
            self.preview_theme
        )
        self.theme_menu_builder.populate(theme_menu)

        edit_menu.addMenu(theme_menu)
        edit_menu.addMenu(open_catalogue_menu)
        menu_bar.addMenu(file_menu)
        menu_bar.addMenu(edit_menu)
        menu_bar.addMenu(progression_menu)
        menu_bar.addMenu(update_menu)
        self.main_layout.setMenuBar(menu_bar)

    def register_actions(self):
        actions = self.config.actions
        for id in actions.model_dump().keys():
            action = getattr(actions, id)
            self.action_manager.register(
                ActionDefinition(
                    id=id,
                    text=action.text,
                    shortcut=action.shortcut,
                    button=action.button,
                    slot=getattr(self, id),
                )
            )

    def open_config_file(self):
        self.persistence_service.open_config_file()

    def init_progression_pannel(self):

        self.progression_panel = ProgressionPanel(
            self.action_manager,
            self.progression_service,
            self.analysis_service
        )
        self.progression_panel.update_buttons_state(self.regex_panel.selected_catalogue())
        self.progression_visible = True
        self.addAction(self.action_manager.action("toggle_progression_panel"))

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

    def update_code_index_main(self):
        update_code_index(
            self.paths.code_labels,
            self.paths.code_index,
            self.paths.texmf,
            config=self.config
        )
        self.reload_data()

        self.update_search()

        QMessageBox.information(
            self,
            "Info",
            f"Updated code index at {self.paths.code_index_file}"
        )
    
    def open_catalogue(self, name):
        catalogue = self.catalogue_service.get_catalogue_from_name(name)
        if catalogue:
            self.catalogue_service.open_catalogue(catalogue.name)
        else:
            QMessageBox.warning(
                self,
                "Warning",
                f"Catalogue '{name}' not found."
            )

    @record_undo
    def add_chapter(self):

        selected_catalogue = self.regex_panel.selected_catalogue()
        item = self.progression_service.add_chapter(
            self.progression_panel.progression_tree,
            selected_catalogue,
            self.progression_panel.progression_tree.currentItem()
        )

        if item:
            self.progression_panel.progression_tree.editItem(item, 0)
        
        self.progression_panel.update_buttons_state(selected_catalogue)

    @record_undo
    def add_level(self):

        item = self.progression_service.add_level(
            self.progression_panel.progression_tree
        )

        if item:
            self.progression_panel.progression_tree.editItem(item, 0)
        
        self.progression_panel.update_buttons_state(self.regex_panel.selected_catalogue())

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
            self.progression_panel.progression_tree,
            self.regex_panel.selected_catalogue()
        )

    def show_usage(self, item):

        code = item.data(Qt.UserRole).code
        print(code)
        locations = self.analysis_service.find_usage_locations(self.progression_panel.progression_tree, code)
        print(locations)

    @record_undo
    def add_selected_item(self):

        entry = self.regex_panel.get_selected_entry()
        if not entry:
            return

        item = self.progression_service.add_selected_item(
            self.progression_panel.progression_tree,
            entry,
        )

        if item is None:
            QMessageBox.warning(self, "Warning", "Please select a chapter to add the item.")
        
        else:
            QMessageBox.information(self, "Info", f"Item {entry.code} added to the progression.")
    
    @record_undo
    def add_seance(self):

        item = self.progression_service.add_seance(
            self.progression_panel.progression_tree
        )

        if item:
            self.progression_panel.progression_tree.editItem(item, 0)
        
        self.progression_panel.update_buttons_state(self.regex_panel.selected_catalogue())

    def _move_current_item(self, delta):
        self.progression_service.move_item(self.progression_panel.progression_tree, delta)

    @record_undo
    def move_item_up(self):
        self._move_current_item(-1)

    @record_undo
    def move_item_down(self):
        self._move_current_item(1)

    @record_undo
    def delete_selected_item(self):
        self.progression_service.delete_item(self.progression_panel.progression_tree)
        self.progression_panel.update_buttons_state(self.regex_panel.selected_catalogue())

    def set_theme(self, name):
        self.theme_service.set_theme(name)
        self.apply_current_theme()

    def catalogue_changed(self):
        self.update_search()
        self.progression_panel.update_buttons_state(self.regex_panel.selected_catalogue())

    def update_search(self):
        self.regex_panel.update_type_filter()
        self.regex_panel.update_search()
        self.preview_panel.refresh_view()

    def undo(self):
        state = self.undo_redo.undo(self.progression_service.snapshot(
                self.progression_panel.progression_tree
                ))
        if state is None:
            return

        self.progression_service.restore(
            self.progression_panel.progression_tree,
            state
        )
        self.progression_panel.update_buttons_state(self.regex_panel.selected_catalogue())

    def redo(self):
        state = self.undo_redo.redo(self.progression_service.snapshot(
                self.progression_panel.progression_tree
            ))
        if state is None:
            return

        self.progression_service.restore(
           self.progression_panel.progression_tree,
            state
        )
        self.progression_panel.update_buttons_state(self.regex_panel.selected_catalogue())

    def load_progression(self):

        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Charger une progression",
            str(self.paths.progression),
            "JSON (*.json)"
        )

        if not filename:
            return

        with open(filename, encoding="utf8") as f:
            data = json.load(f)

        self.progression_service.restore(
            self.progression_panel.progression_tree,
            data
        )
        self.currentFile = Path(filename)

        self.undo_redo.clear()

    def save_progression(self):

        if self.currentFile is None:
            return self.save_as_progression()

        data=self.progression_service.snapshot(
            self.progression_panel.progression_tree
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

    def save_as_progression(self):
        # Open a file dialog to select the save location and name
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Sauvegarder la progression",
            str(self.paths.progression),
            "JSON Files (*.json);;All Files (*)",
            options=options)
        
        if not filename:
            return  # User cancelled the dialog

        data = self.progression_service.snapshot(
            self.progression_panel.progression_tree
        )

        self.persistence_service.save_progression(
            filename,
            data
        )
        self.currentFile = Path(filename)

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

        tex_path = self.paths.sequencages

        tex_path = (
            tex_path
            / f"sequencage-{self.catalogue_combo.currentText().replace(' ', '_')}-{self.currentFile.stem}-structure.tex"
        )

        self.export_service.export_progression(
            tex_path,
            data,
            self.code_service.labels
        )

        QMessageBox.information(
            self,
            "Info",
            f"Progression exported {tex_path}"
        )