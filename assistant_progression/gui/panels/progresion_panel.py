from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTreeWidget, QVBoxLayout, QWidget


class ProgressionPanel(QWidget):
    def __init__(self, action_manager, progression_service, analysis_service):
        super().__init__()
        self.action_names = [
            "add_level",
            "add_chapter",
            "add_seance",
            "add_selected_item",
            "delete_selected_item",
            "show_unused_items"
        ]
        self.action_manager = action_manager
        self.progression_service = progression_service
        self.analysis_service = analysis_service
        self.progression_tree = QTreeWidget()
        self.progression_tree.setHeaderLabel("Progression annuelle")

        self.progression_buttons = QVBoxLayout()

        self.init_signals()

        for action_name in self.action_names:
            button = self.action_manager.button(action_name)
            self.progression_buttons.addWidget(button)
        
        layout = QVBoxLayout()
        layout.addWidget(self.progression_tree)
        layout.addLayout(self.progression_buttons)
        self.setLayout(layout)

    def init_signals(self):
        self.progression_tree.itemClicked.connect(
            self.show_usage
        )
        self.progression_tree.currentItemChanged.connect(
            self.update_buttons_state
        )

    def show_usage(self, item):

        code = item.data(0, Qt.UserRole)
        if not code:
            return

        locations = self.analysis_service.find_usage_locations(
            self,
            code
        )
    
    def is_chapter(self, item):

        if item is None:
            return False

        return (
            item.parent() is not None
            and item.data(0, Qt.UserRole) is None
        )
    
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