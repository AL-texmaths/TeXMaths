import sys
import json
import re
from html import escape

from PySide6.QtCore import Qt, QUrl

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QListWidget,
    QComboBox,
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

        if event.key() in (
            Qt.Key_Return,
            Qt.Key_Enter,
        ):

            self.list_widget.setFocus()
            return

        super().keyPressEvent(event)

class MainWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Recherche référentiel")
        self.resize(1400, 800)

        with open(
            "data/latex/catalogues/code_index.json",
            encoding="utf-8",
        ) as f:
            self.data = json.load(f)

        self.entries = []
        self.build_index()

        self.catalogue_combo = QComboBox()
        self.type_combo = QComboBox()

        self.list_widget = QListWidget()

        self.search = SearchLineEdit(
            self.list_widget
        )

        self.search.setPlaceholderText(
            "Regex sur code ou contenu"
        )
        self.preview = QWebEngineView()

        self.populate_filters()

        left = QVBoxLayout()
        left.addWidget(self.catalogue_combo)
        left.addWidget(self.type_combo)
        left.addWidget(self.search)
        left.addWidget(self.list_widget)

        layout = QHBoxLayout(self)
        layout.addLayout(left, 1)
        layout.addWidget(self.preview, 3)

        self.search.textChanged.connect(
            lambda _: self.update_search()
        )

        self.catalogue_combo.currentTextChanged.connect(
            self.catalogue_changed
        )

        self.type_combo.currentTextChanged.connect(
            lambda _: self.update_search()
        )

        self.list_widget.currentRowChanged.connect(
            self.show_entry
        )

        self.current_matches = []

        self.update_type_filter()
        self.update_search()

        self.search.setFocus()

    def build_index(self):

        for catalogue, catalogue_data in self.data.items():

            if not isinstance(catalogue_data, dict):
                continue

            for source_type, source_data in catalogue_data.items():

                if not isinstance(source_data, dict):
                    continue

                for code, text in source_data.items():

                    self.entries.append(
                        {
                            "catalogue": catalogue,
                            "type": source_type,
                            "code": code,
                            "text": text,
                        }
                    )

    def populate_filters(self):

        self.catalogue_combo.addItem("Tous")

        for catalogue in sorted(self.data.keys()):
            self.catalogue_combo.addItem(catalogue)

    def catalogue_changed(self):

        self.update_type_filter()
        self.update_search()

    def update_type_filter(self):

        current_catalogue = (
            self.catalogue_combo.currentText()
        )

        self.type_combo.blockSignals(True)

        self.type_combo.clear()
        self.type_combo.addItem("Tous")

        types = set()

        if current_catalogue == "Tous":

            for entry in self.entries:
                types.add(entry["type"])

        else:

            for entry in self.entries:

                if (
                    entry["catalogue"]
                    == current_catalogue
                ):
                    types.add(entry["type"])

        for t in sorted(types):
            self.type_combo.addItem(t)

        self.type_combo.blockSignals(False)

    def update_search(self):

        self.list_widget.clear()

        regex_text = self.search.text()

        selected_catalogue = (
            self.catalogue_combo.currentText()
        )

        selected_type = (
            self.type_combo.currentText()
        )

        entries = self.entries

        if selected_catalogue != "Tous":

            entries = [

                e

                for e in entries

                if (
                    e["catalogue"]
                    == selected_catalogue
                )
            ]

        if selected_type != "Tous":

            entries = [

                e

                for e in entries

                if (
                    e["type"]
                    == selected_type
                )
            ]

        if regex_text:

            try:

                regex = re.compile(
                    regex_text,
                    re.IGNORECASE,
                )

            except re.error:

                return

            entries = [

                e

                for e in entries

                if (
                    regex.search(e["code"])
                    or regex.search(e["text"])
                )
            ]

        entries.sort(
            key=lambda e: (
                e["catalogue"],
                e["type"],
                e["code"],
            )
        )

        self.current_matches = entries

        for entry in entries:

            self.list_widget.addItem(
                f'{entry["code"]} [{entry["type"]}]'
            )

        if entries:
            self.list_widget.setCurrentRow(0)
        else:
            self.preview.setHtml("")

    def show_entry(self, row):

        if row < 0:
            return

        if row >= len(self.current_matches):
            return

        entry = self.current_matches[row]

        html = self.make_html(
            code=entry["code"],
            content=entry["text"],
            catalogue=entry["catalogue"],
            source_type=entry["type"],
        )

        self.preview.setHtml(
            html,
            QUrl.fromLocalFile(
                str(KATEX_DIR.resolve()) + "/"
            )
        )

    def make_html(
        self,
        code,
        content,
        catalogue,
        source_type,
    ):

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


    renderMathInElement(
        document.body,
        {{
            delimiters: [
                {{
                    left: "$$",
                    right: "$$",
                    display: true
                }},
                {{
                    left: "$",
                    right: "$",
                    display: false
                }},
                {{
                    left: "\\\\(",
                    right: "\\\\)",
                    display: false
                }},
                {{
                    left: "\\\\[",
                    right: "\\\\]",
                    display: true
                }}
            ]
        }}
    );

}};

</script>

<style>

body {{
    font-family: sans-serif;
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

<div class="code">
{code}
</div>

<div class="meta">
<b>Catalogue :</b> {catalogue}
<br>
<b>Type :</b> {source_type}
</div>

<hr>

<div class="content">
{content}
</div>

</body>
</html>
"""



if __name__ == "__main__":

    app = QApplication(sys.argv)

    w = MainWindow()
    w.show()

    sys.exit(app.exec())