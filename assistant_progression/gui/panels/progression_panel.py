from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMessageBox,
    QTreeWidget,
    QVBoxLayout,
    QWidget
    )


class ProgressionPanel(QWidget):
    def __init__(self, action_manager, progression_service, progression_controller, analysis_service, regex_panel):
        super().__init__()
        self.action_names = [
            "add_level",
            "add_chapter",
            "add_seance",
            "add_selected_item",
            "delete_selected_item",
            "show_unused_items",
            "move_item_up",
            "move_item_down"
        ]
        self.action_manager = action_manager
        self.progression_service = progression_service
        self.analysis_service = analysis_service
        self.regex_panel = regex_panel
        self.controller = progression_controller

        self.init_progression_tree()
        self.init_progression_buttons()
        self.init_signals()
        self.init_main_layout()        

    def init_main_layout(self):
        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.progression_tree)
        self.main_layout.addLayout(self.progression_buttons)
        self.setLayout(self.main_layout)

    def init_progression_buttons(self):
        self.progression_buttons = QVBoxLayout()
        for action_name in self.action_names:
            button = self.action_manager.button(action_name)
            if button:
                self.progression_buttons.addWidget(button)

    def init_progression_tree(self):
        self.progression_tree = QTreeWidget()
        self.progression_tree.setHeaderLabel("Progression annuelle")

    def init_signals(self):
        
        self.progression_tree.currentItemChanged.connect(
            self.update_buttons_state
        )
    
    def is_chapter(self, item):

        if item is None:
            return False

        return (
            item.parent() is not None
            and item.data(0, Qt.UserRole) is None
        )
    
    def refresh_ui(self):
        self.update_buttons_state(self.get_selected_catalogue())

    def update_buttons_state(self, selected_catalogue):

        tree = self.progression_tree

        add_level_enabled = self.progression_service.can_add_level(tree)
        self.action_manager.button("add_level").setEnabled(add_level_enabled)
        self.action_manager.action("add_level").setEnabled(add_level_enabled)

        add_chapter_enabled = self.progression_service.can_add_chapter(
                tree,
                selected_catalogue
            )
        self.action_manager.button("add_chapter").setEnabled(add_chapter_enabled)
        self.action_manager.action("add_chapter").setEnabled(add_chapter_enabled)

        add_seance_enabled = self.progression_service.can_add_seance(tree)
        self.action_manager.button("add_seance").setEnabled(add_seance_enabled)
        self.action_manager.action("add_seance").setEnabled(add_seance_enabled)

        item = tree.currentItem()

        add_item_enabled = self.is_chapter(item)
        self.action_manager.button("add_selected_item").setEnabled(add_item_enabled)
        self.action_manager.action("add_selected_item").setEnabled(add_item_enabled)
    
    def get_selected_catalogue(self):
        return self.regex_panel.selected_catalogue()
    
    def add_level(self):
        self.controller.add_level(
            self.progression_tree,
            refresh_callback=self.refresh_ui
        )

    def add_chapter(self):
        self.controller.add_chapter(
            self.progression_tree,
            self.get_selected_catalogue(),
            self.progression_tree.currentItem(),
            refresh_callback=self.refresh_ui
        )
    
    def add_seance(self):
        self.controller.add_seance(
            self.progression_tree,
            refresh_callback=self.refresh_ui
        )
    
    def add_selected_item(self):
        entry = self.regex_panel.get_selected_entry()
        if not entry:
            return

        self.controller.add_selected_item(
            self.progression_tree,
            entry,
            on_warning=lambda msg: QMessageBox.warning(self, "Warning", msg),
            on_success=lambda msg: QMessageBox.information(self, "Info", msg),
            refresh_callback=self.refresh_ui
        )

    def delete_selected_item(self):
        self.controller.delete_item(
            self.progression_tree,
            refresh_callback=self.refresh_ui
        )
    
    def move_item_up(self):
        self.controller.move_item_up(
            self.progression_tree,
            refresh_callback=self.refresh_ui
        )

    def move_item_down(self):
        self.controller.move_item_down(
            self.progression_tree,
            refresh_callback=self.refresh_ui
        )