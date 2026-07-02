#main_window.py
from assistant_progression.services.code_service import CodeService
from assistant_progression.services.catalogue_service import CatalogueService
from assistant_progression.services.persistence_service import PersistenceService
from assistant_progression.services.export_service import ExportService
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
from assistant_progression.gui.panels.progression_panel import ProgressionPanel
from assistant_progression.controllers.progression_controller import ProgressionController
from assistant_progression.services.undo_redo_service import UndoRedoService
from assistant_progression.controllers.progression_document_controller import ProgressionDocumentController
from assistant_progression.controllers.code_index_document_controller import CodeIndexDocumentController

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMenuBar,
    QMenu,
    QSplitter,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QFileDialog,
    QWidget,
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
        self.reload_data()

        self.main_layout = QHBoxLayout(self)

        self._preview_theme = None
        self._saved_theme = None
        self._theme_committed = False
        self.theme_service.apply(self)

        self.register_actions()
        self.init_regex_panel()
        self.init_progression_pannel()
        self.init_preview_panel()
        self.init_connect_signals()
        self.init_menu()
        self.init_splitters()

        self.update_search()
        self.regex_panel.search_line.setFocus()

    def init_services(self):

        # Services génériques

        self.export_service = ExportService()

        self.undo_redo_service = UndoRedoService()

        # Thèmes
        theme_name = self.settings.current.theme

        self.theme_service = ThemeService(
            themes=self.settings.themes,
            default_theme=theme_name,
        )

    def init_connect_signals(self):

        self.regex_panel.catalogue_combo.currentTextChanged.connect(
            self.catalogue_changed
        )

        self.regex_panel.view_mode_combo.currentTextChanged.connect(
            self.preview_panel.refresh_view
        )

        self.regex_panel.list_widget.currentRowChanged.connect(
            self.preview_panel.refresh_view
        )

    def set_left_focus(self):
        if self.regex_panel.last_focused is not None:
            self.regex_panel.last_focused.setFocus()
        else:
            self.regex_panel.search_line.setFocus()
    
    def set_right_focus(self):
        self.progression_panel.progression_tree.setFocus()

    def reload_data(self):
        self.code_index_document_controller = CodeIndexDocumentController(
            document_path=self.paths.code_index_file
        )

        self.data = self.code_index_document_controller.get_code_index_data()

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

        self.progression_controller = ProgressionController(
            self.progression_service,
            self.undo_redo_service
        )

        self.document_controller = ProgressionDocumentController(
            progression_service=self.progression_service,
            persistence_service=self.persistence_service,
            export_service=self.export_service,
            undo_redo_service=self.undo_redo_service,
            code_service=self.code_service,
            paths=self.paths,
        )

    def init_window_and_settings(self):
        self.setWindowTitle(self.settings.main_window_title)
        self.resize(*self.settings.init_size.size)

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
            self.progression_panel,
            self.theme_service,
            self.code_service,
            self.analysis_service,
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
        update_menu.addAction(self.action_manager.action("update_code_index_main"))

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
            self.progression_controller,
            self.analysis_service,
            self.regex_panel
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

    # @record_undo
    def add_level(self):
        self.progression_panel.add_level()
    
    # @record_undo
    def add_chapter(self):
        self.progression_panel.add_chapter()
    
    # @record_undo
    def add_seance(self):
        self.progression_panel.add_seance()

    # @record_undo
    def add_selected_item(self):
        self.progression_panel.add_selected_item()
        self.preview_panel.refresh_view()

    # @record_undo
    def delete_selected_item(self):
        self.progression_panel.delete_selected_item()
        self.preview_panel.refresh_view()

    def move_item_up(self):
        self.progression_panel.move_item_up()

    def move_item_down(self):
        self.progression_panel.move_item_down()

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
        self.progression_controller.undo(
            self.progression_panel.progression_tree,
            refresh_callback=self.progression_panel.refresh_ui
        )
    
    def redo(self):
        self.progression_controller.redo(
            self.progression_panel.progression_tree,
            refresh_callback=self.progression_panel.refresh_ui
        )

    def load_progression(self):

        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Charger une progression",
            str(self.paths.progression),
            "JSON (*.json)"
        )

        if not filename:
            return

        if self.document_controller.load(
            self.progression_panel.progression_tree,
            filename,
        ):
            self.preview_panel.refresh_view()

    def save_progression(self):

        if not self.document_controller.has_file:
            return self.save_as_progression()

        self.document_controller.save(
            self.progression_panel.progression_tree
        )

        QMessageBox.information(
            self,
            "Info",
            f"File saved at {self.document_controller.current_file}",
        )

    def save_as_progression(self):

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Sauvegarder la progression",
            str(self.paths.progression),
            "JSON Files (*.json);;All Files (*)",
        )

        if not filename:
            return

        self.document_controller.save_as(
            self.progression_panel.progression_tree,
            filename,
        )

    def export_progression(self):

        if not self.document_controller.has_file:
            QMessageBox.warning(
                self,
                "Warning",
                "Please save the progression before exporting.",
            )
            return

        tex_path = self.document_controller.export(
            self.progression_panel.progression_tree,
            self.regex_panel.selected_catalogue().name,
        )

        QMessageBox.information(
            self,
            "Info",
            f"Progression exported to\n{tex_path}",
        )