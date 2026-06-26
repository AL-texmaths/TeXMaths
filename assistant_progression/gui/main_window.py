from assistant_progression.services.html_service import HtmlService
from assistant_progression.services.catalogue_service import CatalogueService
from assistant_progression.services.persistence_service import PersistenceService
from assistant_progression.services.export_service import ExportService
from assistant_progression.services.undo_redo_service import UndoRedoService
from assistant_progression.services.theme_service import ThemeService

def record_undo(method):
    def wrapper(self, *args, **kwargs):
        self.undo_redo.record(self.snapshot_progression())
        return method(self, *args, **kwargs)
    return wrapper

import re
import sys
import json
import copy
from html import escape
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
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QListWidget,
    QComboBox,
    QMenuBar,
    QMenu,
    QSplitter,
    QTreeWidget,
    QTreeWidgetItem,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QDialog
)

from PySide6.QtWebEngineWidgets import QWebEngineView

from src.tools import CONFIG, get_path

title = "Assistant de progression"

KATEX_DIR = get_path('katex')
CODE_INDEX_DIR = get_path('code index')


class SearchLineEdit(QLineEdit):

    def __init__(self, list_widget):
        super().__init__()
        self.list_widget = list_widget

    def keyPressEvent(self, event):

        row = self.list_widget.currentRow()

        if event.key() == Qt.Key_Down:
            if self.list_widget.count():
                self.list_widget.setFocus()
                if row < self.list_widget.count() - 1:
                    self.list_widget.setCurrentRow(row + 1)
            return

        if event.key() == Qt.Key_Up:
            if self.list_widget.count():
                self.list_widget.setFocus()
                if row > 0:
                    self.list_widget.setCurrentRow(row - 1)
            return

        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.list_widget.setFocus()
            return

        super().keyPressEvent(event)

class MainWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.html_service = HtmlService()
        self.persistence_service = PersistenceService()
        self.export_service = ExportService()
        self.undo_redo = UndoRedoService()

        self.main_layout = QHBoxLayout(self)

        self.init_window_and_settings()
        self.theme_service = ThemeService(
        themes=self.settings["themes"],
            default_theme=self.config.get("default", {"theme": next(iter(self.settings["themes"]))})["theme"]
        )

        self.theme_service.apply(self)
        self.init_menu()
        self.init_regex_pannel()
        self.init_preview_pannel()
        self.init_progression_pannel()
        self.init_splitters()
        self.init_connect_signals()
        self.init_undo_redo()
        self.update_type_filter()
        self.update_search()
        self.search.setFocus()


        self.currentFile = None

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
        QShortcut(QKeySequence("Ctrl+Up"), self,
          activated=lambda: self.move_current_item(-1))

        QShortcut(QKeySequence("Ctrl+Down"), self,
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

    def init_window_and_settings(self):
        self.setWindowTitle(title)
        self.resize(1400, 800)

        with open(CODE_INDEX_DIR, encoding="utf-8") as f:
            self.data = json.load(f)

        self.config = CONFIG[title]
        self.settings = self.config.get("settings")

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

        self.catalogue_service = CatalogueService(
            self.data,
            self.config["codes"]
        )

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

        self.populate_filters()

        default_code = self.settings["default"]["code"]
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

    def init_menu(self):

        menu_bar = QMenuBar(self)

        edit_menu = QMenu("Édition", self)
        theme_menu = QMenu("Thème", self)
        file_menu = QMenu("Fichier", self)

        load_action = QAction("Charger une progression", self)
        save_action = QAction("Sauvegarder", self)
        save_under_action = QAction("Sauvegarder sous", self)
        export_progression_action = QAction("Exporter la progression", self)

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
                self.set_theme(name)
            )
            theme_menu.addAction(action)

        edit_menu.addMenu(theme_menu)
        menu_bar.addMenu(file_menu)
        menu_bar.addMenu(edit_menu)
        self.main_layout.setMenuBar(menu_bar)

    def init_progression_pannel(self):

        self.progression = QTreeWidget()

        self.progression.setStyleSheet("""
            QTreeWidget::item {
                height: 28px;
            }
            """)

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

        return self.catalogue_service.internal_name(
            self.catalogue_combo.currentText()
        )

    def is_selected_catalogue_aut_obj_pro(self):
        selected_catalogue = self.selected_catalogue()
        return selected_catalogue in self.config.get("aut obj pro catalogues")

    @record_undo
    def add_chapter(self):

        parent = self.progression.currentItem()

        if parent is None:
            return

        if parent.parent() is not None:
            parent = parent.parent()
        # on ajoute au niveau supérieur

        item = QTreeWidgetItem(["Nouveau chapitre"])
        
        if self.is_selected_catalogue_aut_obj_pro():
            for titre in (
                self.catalogue_service.code_label('aut'),
                self.catalogue_service.code_label('obj'),
                self.catalogue_service.code_label('pro'),
                self.catalogue_service.code_label('sea')
            ):
                item.addChild(QTreeWidgetItem([titre]))

        parent.addChild(item)

        self.progression.setCurrentItem(item)

        item.setFlags(
            item.flags() | Qt.ItemIsEditable
        )

        self.progression.editItem(item, 0)

    @record_undo
    def add_level(self):

        item = QTreeWidgetItem([
            "Nouveau niveau"
        ])

        self.progression.addTopLevelItem(item)

        self.progression.setCurrentItem(item)

        item.setFlags(
            item.flags() |
            Qt.ItemIsEditable
        )

        self.progression.editItem(
            item,
            0
        )

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

        used = self.get_used_codes()


        selected_catalogue = self.selected_catalogue()

        unused = []


        for entry in self.catalogue_service.entries:

            # filtre catalogue
            if selected_catalogue != "Tous":
                if entry.catalogue != selected_catalogue:
                    continue


            # filtre utilisation
            if entry.code not in used:
                unused.append(entry)


        return unused

    def get_used_codes(self):

        used = set()

        def scan(item):

            for i in range(item.childCount()):

                child = item.child(i)

                code = child.data(
                    0,
                    Qt.UserRole
                )

                if code:
                    used.add(code)

                scan(child)


        for i in range(self.progression.topLevelItemCount()):

            root = self.progression.topLevelItem(i)

            scan(root)

        return used

    def get_selected_code(self):
        row = self.list_widget.currentRow()

        if row < 0:
            return

        return self.current_matches[row]

    @record_undo
    def add_selected_item(self):

        selected = self.progression.currentItem()

        if not self.is_chapter(selected):
            return

        entry = self.get_selected_code()

        if self.is_selected_catalogue_aut_obj_pro():
            item_type = entry.type

        parent = self.progression.currentItem()

        target = None
        for i in range(parent.childCount()):
            child = parent.child(i)
            if child.text(0) == self.catalogue_service.code_label(item_type):
                target = child
                break

        if target is None:
            return

        item = QTreeWidgetItem([entry.code])
        item.setData(0, Qt.UserRole, entry.code)

        target.addChild(item)
    
    @record_undo
    def add_seance(self):
        
        parent = self.progression.currentItem()
        if parent is None or parent.text(0) != 'Séances':
            return

        item = QTreeWidgetItem(["Nouvelle séance"])
        
        parent.addChild(item)

        self.progression.setCurrentItem(item)

        item.setFlags(
            item.flags() | Qt.ItemIsEditable
        )

        self.progression.editItem(item, 0)

    @record_undo
    def move_current_item(self, delta):

        item = self.progression.currentItem()
        if item is None:
            return

        parent = item.parent()

        if parent is None:
            count = self.progression.topLevelItemCount()
            index = self.progression.indexOfTopLevelItem(item)
            new = index + delta

            if not (0 <= new < count):
                return

            item = self.progression.takeTopLevelItem(index)
            self.progression.insertTopLevelItem(new, item)

        else:
            count = parent.childCount()
            index = parent.indexOfChild(item)
            new = index + delta

            if not (0 <= new < count):
                return

            item = parent.takeChild(index)
            parent.insertChild(new, item)

        self.progression.setCurrentItem(item)

    def is_chapter(self, item):

        if item is None:
            return False

        # un chapitre possède un parent racine
        return (
            item.parent() is not None
            and item.data(0, Qt.UserRole) is None
        )

    def update_buttons_state(self):

        item = self.progression.currentItem()

        self.add_button.setEnabled(
            self.is_chapter(item)
        )
    
    def update_buttons_state(self):

        item = self.progression.currentItem()

        self.add_button.setEnabled(
            self.is_chapter(item)
        )

    @record_undo
    def delete_progression_item(self):

        item = self.progression.currentItem()

        if item is None:
            return


        parent = item.parent()

        if parent:
            parent.removeChild(item)

        else:
            index = self.progression.indexOfTopLevelItem(item)
            self.progression.takeTopLevelItem(index)

    def show_usage(self,item):

        code = item.data(
            0,
            Qt.UserRole
        )

        if not code:
            return


        locations=[]

        def scan(node,path):

            for i in range(node.childCount()):

                child=node.child(i)

                if child.data(0,Qt.UserRole)==code:
                    locations.append(path)

                scan(
                    child,
                    path+"/"+child.text(0)
                )


        for i in range(self.progression.topLevelItemCount()):

            root=self.progression.topLevelItem(i)

            scan(
                root,
                root.text(0)
            )


        html="""

    <h3>Utilisé dans :</h3>

    <ul>
    """

        for x in locations:
            html+=f"<li>{x}</li>"


        html+="</ul>"


        self.preview.page().runJavaScript(
            ...
        )

    def refresh_view(self):
        mode = self.view_mode_combo.currentText()

        if mode == "Liste complète filtrée":
            self.show_list_view()
        else:
            self.show_entry(self.list_widget.currentRow())

    def show_list_view(self):

        html_items = []

        for e in self.current_matches:
            html_items.append(
                f"<b>{e['code']}</b> (<i>{self.catalogue_service.display_name(e['catalogue'])}</i>)  {e['text']}"
            )

        html = "<br>".join(html_items)

        self.preview.setHtml(
            self.html_service.render_list(html),
            QUrl.fromLocalFile(str(KATEX_DIR.resolve()) + "/")
        )

    def set_theme(self, name):
        self.theme_service.set_theme(name)
        self.theme_service.apply(self)

    def apply_theme(self):
        t = self.themes[self.current_theme]

        focus_bg = t.get("focus_bg", t["panel"])
        focus_border = t.get("focus_border", t["accent"])

        self.setStyleSheet(f"""
            QWidget {{
                background-color: {t['bg']};
                color: {t['fg']};
                font-family: "{t['font']}";
            }}

            QLineEdit,
            QListWidget,
            QComboBox {{
                background-color: {t['panel']};
                border: 1px solid {t['border']};
                padding: 4px;
            }}

            QLineEdit:focus,
            QListWidget:focus,
            QComboBox:focus {{
                border: 3px solid {focus_border};
            }}

            QComboBox::drop-down {{
                border: none;
            }}

            QListWidget::item:selected {{
                background-color: {t['accent']};
                color: white;
            }}
        """)

    def populate_filters(self):

        self.catalogue_combo.addItem("Tous")

        for catalogue in self.catalogue_service.get_catalogues():

            self.catalogue_combo.addItem(
                self.catalogue_service.display_name(
                    catalogue
                )
            )

    def catalogue_changed(self):
        self.update_type_filter()
        self.update_search()

    def update_type_filter(self):

        current_catalogue = self.selected_catalogue()

        self.type_combo.blockSignals(True)

        self.type_combo.clear()

        self.type_combo.addItem("Tous")

        for source_type in self.catalogue_service.get_types(
            current_catalogue
        ):

            self.type_combo.addItem(
                self.catalogue_service.display_name(
                    source_type
                )
            )

        self.type_combo.blockSignals(False)

    def update_search(self):

        regex_text = self.search.text()

        selected_catalogue = self.selected_catalogue()

        selected_type = (
            self.catalogue_service.internal_name(
                self.type_combo.currentText()
            )
        )

        try:

            entries = self.catalogue_service.search(
                catalogue=selected_catalogue,
                source_type=selected_type,
                regex_text=regex_text
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
        )

        self.preview.setHtml(
            html,
            QUrl.fromLocalFile(str(KATEX_DIR.resolve()) + "/")
        )

    def tree_to_dict(self, item, depth=0):
        if depth == 2:
            return [item.child(i).text(0) for i in range(item.childCount())]

        return {
            item.child(i).text(0): self.tree_to_dict(item.child(i), depth + 1)
            for i in range(item.childCount())
        }

    def expanded_paths(self):

        expanded = set()

        def walk(item, path):

            path = path + (item.text(0),)

            if item.isExpanded():
                expanded.add(path)

            for i in range(item.childCount()):
                walk(item.child(i), path)

        for i in range(self.progression.topLevelItemCount()):
            walk(self.progression.topLevelItem(i), ())

        return expanded

    def restore_expanded(self, expanded):

        def walk(item, path):

            path = path + (item.text(0),)

            item.setExpanded(path in expanded)

            for i in range(item.childCount()):
                walk(item.child(i), path)

        for i in range(self.progression.topLevelItemCount()):
            walk(self.progression.topLevelItem(i), ())

    def restore_progression(self, data):

        expanded = self.expanded_paths()

        self.progression.clear()

        def build(parent, obj):

            for key, value in obj.items():

                item = QTreeWidgetItem([key])
                parent.addChild(item)

                if isinstance(value, dict):
                    build(item, value)

                elif isinstance(value, list):

                    for code in value:

                        child = QTreeWidgetItem([code])

                        child.setData(
                            0,
                            Qt.UserRole,
                            code
                        )

                        item.addChild(child)

        for key, value in data.items():

            root = QTreeWidgetItem([key])

            self.progression.addTopLevelItem(root)

            build(root, value)
        
        self.restore_expanded(expanded)

    def snapshot_progression(self):

        data = {}

        for i in range(self.progression.topLevelItemCount()):

            root = self.progression.topLevelItem(i)

            data[root.text(0)] = self.tree_to_dict(root)

        return data

    def load_progression(self):

        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Charger une progression",
            str(get_path("progression import path")),
            "JSON (*.json)"
        )

        if not filename:
            return

        with open(filename, encoding="utf8") as f:
            data = json.load(f)

        self.restore_progression(data)
        self.currentFile = Path(filename)

        self.undo_redo.clear()

    def save_progression(self):

        if self.currentFile is None:
            return self.save_on_progression()

        data=self.snapshot_progression()

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
            "",
            "JSON Files (*.json);;All Files (*)",
            options=options)
        
        if not filename:
            return  # User cancelled the dialog

        data = self.snapshot_progression()

        self.persistence_service.save_progression(
            filename,
            data
        )
        self.currentFile = Path(filename)

    def push_undo(self):
        self.undo_redo.record(self.snapshot_progression())

    def undo(self):
        state = self.undo_redo.undo(self.snapshot_progression())
        if state is None:
            return

        self.restore_progression(state)

    def redo(self):
        state = self.undo_redo.redo(self.snapshot_progression())
        if state is None:
            return

        self.restore_progression(state)

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

        tex_path = get_path(
            "progression export path"
        )

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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
