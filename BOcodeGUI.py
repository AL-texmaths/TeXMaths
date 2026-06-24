import sys
import json
import re
from html import escape

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QAction

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
)

from PySide6.QtWebEngineWidgets import QWebEngineView

from src.tools import KATEX_DIR


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

        self.setWindowTitle("Recherche référentiel")
        self.resize(1400, 800)

        with open("data/latex/catalogues/code_index.json", encoding="utf-8") as f:
            self.data = json.load(f)

        with open("config.json", encoding="utf-8") as f:
            self.config = json.load(f)

        self.code_labels = self.config["codes"]

        self.entries = []
        self.build_index()

        self.catalogue_combo = QComboBox()
        self.type_combo = QComboBox()

        # NOUVEAU : mode affichage
        self.view_mode_combo = QComboBox()
        self.view_mode_combo.addItems([
            "Détail (sélection)",
            "Liste complète filtrée"
        ])

        self.list_widget = QListWidget()
        self.search = SearchLineEdit(self.list_widget)

        self.search.setPlaceholderText("Regex sur code ou contenu")

        self.preview = QWebEngineView()

        self.populate_filters()

        default_code = "cycle 4 BO 2026"
        default_label = self.display_name(default_code)

        index = self.catalogue_combo.findText(default_label)
        if index >= 0:
            self.catalogue_combo.setCurrentIndex(index)

        left = QVBoxLayout()
        left.addWidget(self.catalogue_combo)
        left.addWidget(self.type_combo)
        left.addWidget(self.view_mode_combo)   # <-- AJOUT ICI
        left.addWidget(self.search)
        left.addWidget(self.list_widget)

        layout = QHBoxLayout(self)
        layout.addLayout(left, 1)
        layout.addWidget(self.preview, 3)

        self.search.textChanged.connect(lambda _: self.update_search())
        self.catalogue_combo.currentTextChanged.connect(self.catalogue_changed)
        self.type_combo.currentTextChanged.connect(lambda _: self.update_search())
        self.view_mode_combo.currentTextChanged.connect(lambda _: self.refresh_view())

        self.list_widget.currentRowChanged.connect(self.show_entry)

        self.current_matches = []

        self.update_type_filter()
        self.update_search()

        self.search.setFocus()

        self.themes = self.config["themes"]
        self.current_theme = self.config.get(
            "default_theme",
            next(iter(self.themes))
        )

        menu_bar = QMenuBar(self)
        edit_menu = QMenu("Édition", self)
        theme_menu = QMenu("Thème", self)

        for theme_name in self.themes.keys():
            action = QAction(theme_name, self)
            action.triggered.connect(lambda checked, name=theme_name: self.set_theme(name))
            theme_menu.addAction(action)

        edit_menu.addMenu(theme_menu)
        menu_bar.addMenu(edit_menu)

        layout.setMenuBar(menu_bar)

        self.apply_theme()

    # ---------------- VIEW SWITCH ----------------

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
                f"{e['code']} ({self.display_name(e['catalogue'])})  {e['text']}"
            )

        html = "<br>".join(html_items)

        self.preview.setHtml(
            self.make_list_html(html),
            QUrl.fromLocalFile(str(KATEX_DIR.resolve()) + "/")
        )

    def make_list_html(self, content):

        css = "katex.min.css"
        js = "katex.min.js"
        render = "contrib/auto-render.min.js"

        return f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">

<link rel="stylesheet" href="{css}">
<script src="{js}"></script>
<script src="{render}"></script>

<script>
window.onload = function() {{
    renderMathInElement(document.body, {{
        delimiters: [
            {{ left: "$$", right: "$$", display: true }},
            {{ left: "$", right: "$", display: false }},
            {{ left: "\\\\(", right: "\\\\)", display: false }},
            {{ left: "\\\\[", right: "\\\\]", display: true }}
        ]
    }});
}};
</script>

<style>
body {{
    font-family: "Latin Modern Roman", serif;
    padding: 20px;
    font-size: 18px;
}}

.item {{
    margin-bottom: 10px;
}}
</style>

</head>

<body>
<div class="item">{content}</div>
</body>
</html>
"""

    # ---------------- EXISTANT ----------------

    def set_theme(self, name):
        self.current_theme = name
        self.apply_theme()

    def apply_theme(self):
        t = self.themes[self.current_theme]

        self.setStyleSheet(f"""
            QWidget {{
                background-color: {t['bg']};
                color: {t['fg']};
                font-family: "{t['font']}";
            }}

            QLineEdit, QListWidget, QComboBox {{
                background-color: {t['panel']};
                border: 1px solid {t['border']};
                padding: 4px;
            }}

            QListWidget::item:selected {{
                background-color: {t['accent']};
                color: white;
            }}
        """)

    def display_name(self, code):
        return self.code_labels.get(code, code)

    def internal_name(self, display):
        for code, label in self.code_labels.items():
            if label == display:
                return code
        return display

    def build_index(self):
        for catalogue, catalogue_data in self.data.items():
            if not isinstance(catalogue_data, dict):
                continue

            for source_type, source_data in catalogue_data.items():
                if not isinstance(source_data, dict):
                    continue

                for code, text in source_data.items():
                    self.entries.append({
                        "catalogue": catalogue,
                        "type": source_type,
                        "code": code,
                        "text": text,
                    })

    def populate_filters(self):
        self.catalogue_combo.addItem("Tous")
        for catalogue in sorted(self.data.keys()):
            self.catalogue_combo.addItem(self.display_name(catalogue))

    def catalogue_changed(self):
        self.update_type_filter()
        self.update_search()

    def update_type_filter(self):

        current_catalogue = self.internal_name(self.catalogue_combo.currentText())

        self.type_combo.blockSignals(True)
        self.type_combo.clear()
        self.type_combo.addItem("Tous")

        types = set()

        for entry in self.entries:
            if current_catalogue == "Tous" or entry["catalogue"] == current_catalogue:
                types.add(entry["type"])

        for t in sorted(types):
            self.type_combo.addItem(self.display_name(t))

        self.type_combo.blockSignals(False)

    def update_search(self):

        regex_text = self.search.text()

        selected_catalogue = self.internal_name(self.catalogue_combo.currentText())
        selected_type = self.internal_name(self.type_combo.currentText())

        entries = self.entries

        if selected_catalogue != "Tous":
            entries = [e for e in entries if e["catalogue"] == selected_catalogue]

        if selected_type != "Tous":
            entries = [e for e in entries if e["type"] == selected_type]

        if regex_text:
            try:
                regex = re.compile(regex_text, re.IGNORECASE)
            except re.error:
                return

            entries = [
                e for e in entries
                if regex.search(e["code"]) or regex.search(e["text"])
            ]

        entries.sort(key=lambda e: (e["catalogue"], e["type"], e["code"]))

        self.current_matches = entries

        self.list_widget.clear()

        for entry in entries:
            self.list_widget.addItem(f'{entry["code"]} [{entry["type"]}]')

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

        html = self.make_html(
            code=entry["code"],
            content=entry["text"],
            catalogue=self.display_name(entry["catalogue"]),
            source_type=self.display_name(entry["type"]),
        )

        self.preview.setHtml(
            html,
            QUrl.fromLocalFile(str(KATEX_DIR.resolve()) + "/")
        )

    def make_html(self, code, content, catalogue, source_type):

        css = "katex.min.css"
        js = "katex.min.js"
        render = "contrib/auto-render.min.js"

        content = escape(content)

        return f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">

<link rel="stylesheet" href="{css}">
<script src="{js}"></script>
<script src="{render}"></script>

<script>
window.onload = function() {{
    renderMathInElement(document.body, {{
        delimiters: [
            {{ left: "$$", right: "$$", display: true }},
            {{ left: "$", right: "$", display: false }},
            {{ left: "\\\\(", right: "\\\\)", display: false }},
            {{ left: "\\\\[", right: "\\\\]", display: true }}
        ]
    }});
}};
</script>

<style>
body {{
    font-family: "Latin Modern Roman", serif;
    padding: 20px;
    font-size: 18px;
}}

.code {{
    font-size: 28px;
    font-weight: bold;
    margin-bottom: 10px;
}}

.meta {{
    color: #666;
    margin-bottom: 20px;
}}

.content {{
    line-height: 1.6;
}}
</style>

</head>

<body>

<div class="code">{code}</div>

<div class="meta">
<b>Catalogue :</b> {catalogue}<br>
<b>Type :</b> {source_type}
</div>

<hr>

<div class="content">{content}</div>

</body>
</html>
"""


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())