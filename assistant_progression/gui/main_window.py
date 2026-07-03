#main_window.py
from assistant_progression.app.logger import logger, logger_wraper
from assistant_progression.app.application_context import create_context
from assistant_progression.gui.action import ActionDefinition
from assistant_progression.gui.actions_manager import ActionManager
from assistant_progression.gui.menus.theme_menu_builder import ThemeMenuBuilder
from assistant_progression.gui.menus.catalogue_menu_builder import CatalogueMenuBuilder
from assistant_progression.gui.panels.regex_panel import RegexPanel
from assistant_progression.gui.panels.preview_panel import PreviewPanel
from assistant_progression.gui.panels.progression_panel import ProgressionPanel
from assistant_progression.controllers.theme_controller import ThemeController
from assistant_progression.gui.dialogs.unused_items_dialog import UnusedItemsDialog


from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMenuBar,
    QMenu,
    QSplitter,
    QHBoxLayout,
    QFileDialog,
    QWidget,
    QMessageBox,
)


class MainWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.context = create_context(self)
        logger.info("app context created")
        self.settings = self.context.config.settings
        self.action_manager = ActionManager(self)
        self.current_file_path = self.context.session_controller.get_current_file()
        self.init_window_and_settings()
        self.init_services()

        self.register_actions()
        self.init_regex_panel()
        self.init_progression_pannel()
        self.init_preview_panel()
        self.init_connect_signals()
        self.main_layout = QHBoxLayout(self)
        self.init_menu()
        self.init_splitter()
    
        self.context.theme_service.apply(self)
        self.update_search()
        self.regex_panel.search_line.setFocus()

    def init_services(self):

        self.theme_controller = ThemeController(
            theme_service=self.context.theme_service,
            persistence_service=self.context.persistence_service,
            config=self.context.config,
            on_theme_changed=self.apply_current_theme
        )

    def init_connect_signals(self):

        self.regex_panel.catalogue_combo.currentTextChanged.connect(
            self.catalogue_changed
        )
        self.regex_panel.type_combo.currentTextChanged.connect(
            self.type_changed
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

    @logger_wraper
    def init_window_and_settings(self):
        self.setWindowTitle(self.settings.gui.main_window.title + " - " + self.current_file_path)
        self.resize(
            self.settings.gui.main_window.width,
            self.settings.gui.main_window.height
            )
        self.unused_items_dialog = None

    def init_splitter(self):
        
        self.splitter = QSplitter(Qt.Horizontal)

        self.splitter.addWidget(self.regex_panel)
        self.splitter.addWidget(self.preview_panel)
        self.splitter.addWidget(self.progression_panel)
        self.tabs = [self.regex_panel, self.preview_panel, self.progression_panel]

        splitter_size = self.settings.gui.splitter.size
        self.splitter.setSizes(splitter_size)

        
        self.main_layout.addWidget(self.splitter)

    def init_regex_panel(self):

        default_code = self.settings.current.catalogue
        if default_code is None:
            default_code = self.context.catalogue_service.get_catalogue_names()[0]
        default_catalogue_label =self.context.code_service.display_name(default_code)
    
        self.regex_panel = RegexPanel(
            self.context.search_service,
            default_catalogue_label=default_catalogue_label,
            default_type_label=self.context.session_controller.get_type()
        )

    def init_progression_pannel(self):

        self.progression_panel = ProgressionPanel(
            self.action_manager,
            self.context.progression_service,
            self.context.progression_controller,
            self.context.progression_analysis_service,
            self.regex_panel
        )
        self.progression_panel.update_buttons_state(self.regex_panel.selected_catalogue())
        self.progression_visible = True
        self.addAction(self.action_manager.action("toggle_progression_panel"))

        if self.current_file_path:
            self.context.document_controller.load(
                self.progression_panel.progression_tree,
                self.current_file_path
            )
    
    def init_preview_panel(self):
        self.preview_panel = PreviewPanel(
            self.regex_panel,
            self.progression_panel,
            self.context.theme_service,
            self.context.code_service,
            self.context.progression_analysis_service,
            self.context.paths.katex
        )
    
    def apply_current_theme(self):
        self.context.theme_service.apply(self)
        self.preview_panel.refresh_view()

    def begin_theme_preview(self):
        self.theme_controller.begin_preview()

    def cancel_theme_preview(self):
        self.theme_controller.cancel_preview()

    def commit_theme(self, name):
        self.theme_controller.commit_theme(name)

    def set_theme(self, name):
        self.theme_controller.set_theme(name)

    def init_menu(self):

        menu_bar = QMenuBar(self)

        edit_menu = QMenu("Édition", self)

        theme_menu = QMenu("Thème", self)
        theme_menu.aboutToShow.connect(self.begin_theme_preview)
        theme_menu.aboutToHide.connect(self.cancel_theme_preview)

        open_catalogue_menu = QMenu("Ouvrir un catalogue", self)
        self.catalogue_menu_builder = CatalogueMenuBuilder(
            self.context.catalogue_service,
            self.context.paths.texmf,
            self.context.config
        )
        self.catalogue_menu_builder.populate(open_catalogue_menu)

        progression_menu = QMenu("Progression", self)
        for action_id in [
            "add_level",
            "add_chapter",
            "add_seance",
            "move_item_up",
            "move_item_down",
            "show_unused_items"
        ]:
            action = self.action_manager.action(action_id)
            progression_menu.addAction(action)

        update_menu = QMenu("Mise à jour", self)
        update_menu.addAction(self.action_manager.action("update_code_index_main"))

        file_menu = QMenu("Fichier", self)
        file_menu.addAction(self.action_manager.action("load_progression"))
        file_menu.addSeparator()
        file_menu.addAction(self.action_manager.action("save_progression"))
        file_menu.addAction(self.action_manager.action("save_as_progression"))
        file_menu.addSeparator()
        file_menu.addAction(self.action_manager.action("export_progression"))

        self.theme_menu_builder = ThemeMenuBuilder(
            self.context.theme_service,
            self.commit_theme,
            self.set_theme
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
        actions = self.context.config.actions
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
        self.context.persistence_service.open_config_file()

    def toggle_progression_panel(self):
        if self.progression_visible:
            self._saved_sizes = self.splitter.sizes()

            self.progression_panel.setVisible(False)

            self.splitter.setSizes([400, 1000, 0])

            self.progression_visible = False

        else:
            self.progression_panel.setVisible(True)

            if hasattr(self, "_saved_sizes"):
                self.splitter.setSizes(self._saved_sizes)
            else:
                self.splitter.setSizes([400, 800, 300])

            self.progression_visible = True


    def update_code_index_main(self):

        result = self.context.code_index_controller.refresh_code_index()

        if result!=0:
            QMessageBox.warning(
                self,
                "Warning",
                f"La compilation a échouchée, check log console."
            )

        self.update_search()

        QMessageBox.information(
            self,
            "Info",
            f"Updated code index at {self.context.paths.code_index_file}"
        )

    
    def open_catalogue(self, name):
        catalogue = self.context.catalogue_service.get_catalogue_from_name(name)
        if catalogue:
            self.context.catalogue_service.open_catalogue(catalogue.name)
        else:
            QMessageBox.warning(
                self,
                "Warning",
                f"Catalogue '{name}' not found."
            )

    def add_level(self):
        self.progression_panel.add_level()
    
    def add_chapter(self):
        self.progression_panel.add_chapter()
    
    def add_seance(self):
        self.progression_panel.add_seance()

    def add_selected_item(self):
        self.progression_panel.add_selected_item()
        self.preview_panel.refresh_view()

    def delete_selected_branch(self):
        self.progression_panel.delete_selected_branch()
        self.preview_panel.refresh_view()

    def move_item_up(self):
        self.progression_panel.move_item_up()

    def move_item_down(self):
        self.progression_panel.move_item_down()

    def show_unused_items(self):
        unused = self.get_unused_entries()
        self.unused_items_dialog = UnusedItemsDialog(unused, self.context.config)
        self.unused_items_dialog.exec()
        self.context.session_controller.init_save_unused_items_dialog_settings()

    def get_unused_entries(self):
        return self.context.progression_analysis_service.get_unused_entries(
            self.progression_panel.progression_tree,
            self.regex_panel.selected_catalogue()
        )

    def catalogue_changed(self):
        self.update_search()
        catalogue_ = self.regex_panel.selected_catalogue()
        self.progression_panel.update_buttons_state(catalogue_)
        self.context.session_controller.set_catalogue(catalogue_.name)

    def type_changed(self):
        self.regex_panel.update_search()
        type_text = self.regex_panel.type_combo.currentText()
        self.context.session_controller.set_type(type_text)

    def update_search(self):

        restore = True
        list_widget = self.regex_panel.list_widget
        item = list_widget.currentItem()
        if item is None:
            restore = False
        else:
            entry = item.data(Qt.UserRole)

        self.regex_panel.update_type_filter()
        self.regex_panel.update_search()
        list_widget = self.regex_panel.list_widget

        if restore:
            for i in range(list_widget .count()):
                item = list_widget.item(i)
                if item.data(Qt.UserRole) == entry:
                    list_widget.setCurrentItem(item)
                    break
        
        self.preview_panel.refresh_view()

    def undo(self):
        self.context.progression_controller.undo(
            self.progression_panel.progression_tree,
            refresh_callback=self.progression_panel.refresh_ui
        )
    
    def redo(self):
        self.context.progression_controller.redo(
            self.progression_panel.progression_tree,
            refresh_callback=self.progression_panel.refresh_ui
        )

    def load_progression(self):

        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Charger une progression",
            str(self.context.paths.progression),
            "JSON (*.json)"
        )

        if not filename:
            return

        if self.context.document_controller.load(
            self.progression_panel.progression_tree,
            filename,
        ):
            self.preview_panel.refresh_view()
            self.context.session_controller.set_current_file(filename)

    def save_progression(self):

        if not self.context.document_controller.has_file:
            return self.save_as_progression()

        self.context.document_controller.save(
            self.progression_panel.progression_tree
        )
        self.context.session_controller.commit_gui_settings()

        QMessageBox.information(
            self,
            "Info",
            f"File saved at {self.context.document_controller.current_file}",
        )

    def save_as_progression(self):

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Sauvegarder la progression",
            str(self.context.paths.progression),
            "JSON Files (*.json);;All Files (*)",
        )

        if not filename:
            return

        self.context.document_controller.save_as(
            self.progression_panel.progression_tree,
            filename,
        )

    def export_progression(self):

        if not self.context.document_controller.has_file:
            QMessageBox.warning(
                self,
                "Warning",
                "Please save the progression before exporting.",
            )
            return

        tex_path = self.context.document_controller.export(
            self.progression_panel.progression_tree,
            self.regex_panel.selected_catalogue().name,
        )

        QMessageBox.information(
            self,
            "Info",
            f"Progression exported to\n{tex_path}",
        )