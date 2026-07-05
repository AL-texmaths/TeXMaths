from PySide6.QtGui import QShortcut, QKeySequence
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QMessageBox,
    QTreeWidget,
    QVBoxLayout,
    QWidget,
    QLineEdit
    )


class ProgressionPanel(QWidget):
    def __init__(
            self,
            progression_tree_config,
            action_manager,
            progression_service,
            progression_controller,
            analysis_service,
            regex_panel
            ):
        super().__init__()
        self.action_names = [
            "add_custom_item",
            "add_level",
            "add_chapter",
            "add_seance",
            "add_selected_item",
            "delete_selected_branch",
            "show_unused_items",
            "move_item_up",
            "move_item_down"
        ]
        self.action_manager = action_manager
        self.progression_service = progression_service
        self.analysis_service = analysis_service
        self.regex_panel = regex_panel
        self.controller = progression_controller
        self.config = progression_tree_config
        self.search_timer = QTimer(self)
        self.search_timer.setSingleShot(True)
        self.search_timer.setInterval(300) # 300ms debounce
        self.search_timer.timeout.connect(self.filter_tree)

        self.init_progression_tree()
        self.init_progression_buttons()
        self.init_signals()
        self.init_main_layout()        

    def init_main_layout(self):
        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.search_bar)
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
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Chercher dans la progression...")
        
        self.progression_tree = QTreeWidget()
        self.progression_tree.setHeaderLabel("Progression annuelle")

        rename_shortcut = QShortcut(
            QKeySequence(Qt.CTRL | Qt.Key_Return),
            self)
        rename_shortcut.activated.connect(self.rename_current_item)

        scroll_up_shortcut = QShortcut(QKeySequence(Qt.CTRL | Qt.Key_Up), self)
        scroll_up_shortcut.activated.connect(self.move_tree_up)

        scroll_down_shortcut = QShortcut(QKeySequence(Qt.CTRL | Qt.Key_Down), self)
        scroll_down_shortcut.activated.connect(self.move_tree_down)

    def init_signals(self):
        
        self.progression_tree.currentItemChanged.connect(
            self.update_buttons_state
        )
        self.search_bar.textChanged.connect(
            lambda: self.search_timer.start()
        )

    def filter_tree(self):
        search_text = self.search_bar.text().lower()
        
        for i in range(self.progression_tree.topLevelItemCount()):
            item = self.progression_tree.topLevelItem(i)
            self._filter_item(item, search_text)

    def _filter_item(self, item, search_text):
        # Un item est visible si son texte correspond ou si l'un de ses enfants correspond
        item_text = item.text(0).lower()
        match = search_text in item_text
        
        child_match = False
        for i in range(item.childCount()):
            if self._filter_item(item.child(i), search_text):
                child_match = True
        
        visible = match or child_match
        item.setHidden(not visible)
        
        # Si on filtre (texte non vide) et qu'il y a un match chez les enfants, on déplie
        if search_text and child_match:
            item.setExpanded(True)
        elif not search_text:
            # Si recherche vidée, on ne touche pas forcément à l'expansion 
            # ou on peut décider de tout replier/laisser tel quel.
            # Ici on laisse tel quel pour ne pas perdre le focus de l'utilisateur.
            pass
            
        return visible

    def rename_current_item(self):
        item = self.progression_tree.currentItem()
        if item is not None:
            self.progression_tree.editItem(item, 0)  # Édite la colonne 0

    def is_chapter(self, item):

        if item is None:
            return False

        return (
            item.parent() is not None
            and item.data(0, Qt.UserRole) is None
        )
    
    def refresh_ui(self):
        self.update_buttons_state(self.get_selected_catalogue())
        self.filter_tree()

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

        add_item_enabled = self.progression_service.can_add_item(tree)
        self.action_manager.button("add_selected_item").setEnabled(add_item_enabled)
        self.action_manager.action("add_selected_item").setEnabled(add_item_enabled)
    
    def get_selected_catalogue(self):
        return self.regex_panel.selected_catalogue()
    
    def add_custom_item(self):
        self.controller.add_custom_item(
            self.progression_tree,
            text="Nouvel élément",
            refresh_callback=self.refresh_ui
        )

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

    def delete_selected_branch(self):
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

    def move_tree_up(self):
        scrollbar = self.progression_tree.verticalScrollBar()
        scrollbar.setValue(
            scrollbar.value() - scrollbar.singleStep() * self.config.scrolling_step)

    def move_tree_down(self):
        scrollbar = self.progression_tree.verticalScrollBar()
        scrollbar.setValue(
            scrollbar.value() + scrollbar.singleStep() * self.config.scrolling_step)