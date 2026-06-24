import sys
import json
import re
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QListWidget,
)
from PySide6.QtWebEngineWidgets import QWebEngineView

from src.tools import KATEX_DIR

class MainWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Recherche référentiel")
        self.resize(1200, 700)

        with open("data/latex/catalogues/code_index.json", encoding="utf-8") as f:
            self.data = json.load(f)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Regex (ex: A3.*)")

        self.list_widget = QListWidget()

        self.preview = QWebEngineView()

        left = QVBoxLayout()
        left.addWidget(self.search)
        left.addWidget(self.list_widget)

        layout = QHBoxLayout(self)
        layout.addLayout(left, 1)
        layout.addWidget(self.preview, 3)

        self.search.textChanged.connect(self.update_search)
        self.list_widget.currentTextChanged.connect(
            self.show_entry
        )

        self.update_search("")

    def update_search(self, text):

        self.list_widget.clear()

        if not text:
            matches = sorted(self.data.keys())

        else:
            try:
                regex = re.compile(text, re.IGNORECASE)
            except re.error:
                return

            matches = [
                code
                for code in self.data
                if regex.search(code)
            ]

            matches.sort()

        self.list_widget.addItems(matches)

        if matches:
            self.list_widget.setCurrentRow(0)

    def show_entry(self, code):

        if not code:
            return

        content = self.data[code]

        html = self.make_html(code, content)

        self.preview.setHtml(html)

    def make_html(self, code, content):

        katex_dir = KATEX_DIR.absolute()

        css = (katex_dir / "katex.min.css").as_uri()
        js = (katex_dir / "katex.min.js").as_uri()
        render = (katex_dir / "auto-render.min.js").as_uri()

        return f"""
<!DOCTYPE html>
<html>
<head>

<meta charset="utf-8">

<link rel="stylesheet" href="{css}">

<script defer src="{js}"></script>
<script defer src="{render}"></script>

<script>
document.addEventListener("DOMContentLoaded", function() {{
    renderMathInElement(document.body, {{
        delimiters: [
            {{left: "$$", right: "$$", display: true}},
            {{left: "$", right: "$", display: false}},
            {{left: "\\\\(", right: "\\\\)", display: false}},
            {{left: "\\\\[", right: "\\\\]", display: true}}
        ]
    }});
}});
</script>

<style>
body {{
    font-family: sans-serif;
    padding: 20px;
    font-size: 18px;
}}
.code {{
    font-size: 24px;
    font-weight: bold;
    margin-bottom: 20px;
}}
</style>

</head>

<body>

<div class="code">{code}</div>

<p>{content}</p>

</body>
</html>
"""

if __name__ == "__main__":

    app = QApplication(sys.argv)

    w = MainWindow()
    w.show()

    sys.exit(app.exec())