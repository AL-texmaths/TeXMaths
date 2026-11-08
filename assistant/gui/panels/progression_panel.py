import re

from PySide6.QtGui import QShortcut, QKeySequence, QFontMetrics
from PySide6.QtCore import Qt, QTimer, QSize, QRect
from PySide6.QtWidgets import (
    QMessageBox,
    QPushButton,
    QStyledItemDelegate,
    QTreeWidget,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QLineEdit
)

from assistant.gui.widgets.regex_help import install_regex_help


class _MultilineDelegate(QStyledItemDelegate):
    """Ajuste la hauteur des items contenant des sauts de lignes
    et édite le texte sans numéro/compteur ajoutés à l'affichage."""

    def __init__(self, tree, raw_text):
        super().__init__(tree)
        self.tree = tree
        self.raw_text = raw_text

    def sizeHint(self, option, index):
        size = super().sizeHint(option, index)
        text = index.data(Qt.DisplayRole) or ""
        depth = 0
        parent = index.parent()
        while parent.isValid():
            depth += 1
            parent = parent.parent()

        text_width = max(
            1,
            min(
                self.tree.columnWidth(index.column()),
                self.tree.viewport().width()
            ) - self.tree.indentation() * (depth + 1) - 8
        )
        text_rect = QFontMetrics(option.font).boundingRect(
            QRect(0, 0, text_width, 0),
            Qt.TextFlag.TextWordWrap,
            text
        )
        return QSize(size.width(), max(size.height(), text_rect.height() + 8))

    def setEditorData(self, editor, index):
        super().setEditorData(editor, index)
        if not isinstance(editor, QLineEdit):
            return
        item = self.tree.itemFromIndex(index)
        if item is not None and item.data(0, Qt.UserRole) in (None, "seance"):
            editor.setText(self.raw_text(item))
        editor.selectAll()


class _ProgressionTreeWidget(QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._layout_timer = QTimer(self)
        self._layout_timer.setSingleShot(True)
        self._layout_timer.setInterval(50)
        self._layout_timer.timeout.connect(self.doItemsLayout)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if event.size().width() != event.oldSize().width():
            self._layout_timer.start()


class ProgressionPanel(QWidget):
    def __init__(
            self,
            progression_tree_config,
            action_manager,
            progression_service,
            progression_controller,
            analysis_service,
            regex_panel,
            theme_service
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
            "move_item_down",
            "toggle_detailed_mode"
        ]
        self.action_manager = action_manager
        self.progression_service = progression_service
        self.analysis_service = analysis_service
        self.regex_panel = regex_panel
        self.theme_service = theme_service
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
        self.search_controls = QHBoxLayout()
        self.search_controls.addWidget(self.search_bar)
        self.search_controls.addWidget(self.toggle_progression_buttons_button)
        self.main_layout.addLayout(self.search_controls)
        self.main_layout.addWidget(self.progression_tree)
        self.main_layout.addWidget(self.progression_buttons_widget)
        self.setLayout(self.main_layout)

    def init_progression_buttons(self):
        self.progression_buttons = QVBoxLayout()
        for action_name in self.action_names:
            button = self.action_manager.button(action_name)
            if button:
                self.progression_buttons.addWidget(button)
        collapse_button = QPushButton("Tout replier")
        collapse_button.clicked.connect(self.progression_tree.collapseAll)
        self.progression_buttons.addWidget(collapse_button)
        self.progression_buttons_widget = QWidget()
        self.progression_buttons_widget.setLayout(self.progression_buttons)
        self.toggle_progression_buttons_button = QPushButton("Masquer les boutons")
        self.toggle_progression_buttons_button.setCheckable(True)
        self.toggle_progression_buttons_button.toggled.connect(
            self.set_progression_buttons_hidden
        )

    def set_progression_buttons_hidden(self, hidden: bool):
        self.progression_buttons_widget.setVisible(not hidden)
        self.toggle_progression_buttons_button.setText(
            "Afficher les boutons" if hidden else "Masquer les boutons"
        )

    def init_progression_tree(self):
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Chercher dans la progression (regex)...")
        install_regex_help(self.search_bar, count_provider=self._count_matches)
        
        self.progression_tree = _ProgressionTreeWidget()
        self.progression_tree.setHeaderLabel("Progression annuelle")
        self.progression_tree.setUniformRowHeights(False)
        self.progression_tree.setWordWrap(True)
        self.progression_tree.setItemDelegate(_MultilineDelegate(
            self.progression_tree,
            self.progression_service._get_raw_text
        ))

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
        self.progression_tree.itemChanged.connect(self._on_item_changed)
        self.search_bar.textChanged.connect(
            lambda: self.search_timer.start()
        )

    def _on_item_changed(self, item, column):
        # Après un renommage, réappliquer les numéros et compteurs.
        tree = self.progression_tree
        tree.blockSignals(True)
        try:
            self.progression_service.update_level_displays(tree)
            self.progression_service.update_seance_displays(tree)
            self.progression_service.update_chapter_numbers(tree)
        finally:
            tree.blockSignals(False)

    def filter_tree(self):
        try:
            regex = re.compile(self.search_bar.text(), re.IGNORECASE)
        except re.error:
            return
        self._apply_filter(regex)

    def _apply_filter(self, regex):
        for i in range(self.progression_tree.topLevelItemCount()):
            item = self.progression_tree.topLevelItem(i)
            self._filter_item(item, regex)

    def _count_matches(self, pattern: str) -> int:
        regex = re.compile(pattern, re.IGNORECASE)

        def count(item):
            own = regex.search(self._haystack(item)) is not None
            return int(own) + sum(count(item.child(i)) for i in range(item.childCount()))

        return sum(
            count(self.progression_tree.topLevelItem(i))
            for i in range(self.progression_tree.topLevelItemCount())
        )

    def _haystack(self, item) -> str:
        extended_text = self.progression_service.get_item_extended_text(item)
        return f"{item.text(0)}\n{extended_text}"

    def _filter_item(self, item, regex):
        # Un item est visible si son texte (ou le texte de son entrée catalogue) correspond,
        # ou si l'un de ses enfants correspond
        match = regex.search(self._haystack(item)) is not None
        
        child_match = False
        for i in range(item.childCount()):
            if self._filter_item(item.child(i), regex):
                child_match = True
        
        visible = match or child_match
        item.setHidden(not visible)
        
        # Si on filtre (texte non vide) et qu'il y a un match chez les enfants, on déplie
        if regex.pattern and child_match:
            item.setExpanded(True)
        elif not regex.pattern:
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
        self.progression_tree.blockSignals(True)
        try:
            self.progression_service.update_level_displays(self.progression_tree)
            self.progression_service.update_seance_displays(self.progression_tree)
            self.progression_service.update_chapter_numbers(self.progression_tree)
        finally:
            self.progression_tree.blockSignals(False)
        self.progression_service.refresh_detailed_mode(self.progression_tree)
        self.refresh_theme_colors()
        self.update_buttons_state(self.get_selected_catalogue())
        self.filter_tree()

    def refresh_theme_colors(self):
        level_colors, type_colors = self.theme_service.get_progression_colors(
            len(self.config.level_colors),
            self.config.type_colors
        )
        previous_blocked = self.progression_tree.blockSignals(True)
        try:
            self.progression_service.apply_colors(
                self.progression_tree,
                level_colors,
                type_colors
            )
        finally:
            self.progression_tree.blockSignals(previous_blocked)

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
        current_item = self.progression_tree.currentItem()
        first_chapter_item = None
        
        # Trouver le premier parent de niveau 1
        if current_item:
            item = current_item
            while item.parent() is not None:
                item = item.parent()
            first_chapter_item = item
        
        self.controller.add_chapter(
            self.progression_tree,
            self.get_selected_catalogue(),
            first_chapter_item,
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

    def copy_item(self):
        self.controller.copy_item(
            self.progression_tree,
            refresh_callback=self.refresh_ui
        )

    def cut_item(self):
        self.controller.cut_item(
            self.progression_tree,
            refresh_callback=self.refresh_ui
        )

    def paste_item(self):
        self.controller.paste_item(
            self.progression_tree,
            refresh_callback=self.refresh_ui
        )
    
    def toggle_detailed_mode(self):
        self.progression_service.toggle_detailed_mode(self.progression_tree)
        self.filter_tree()

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