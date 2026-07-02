from PySide6.QtCore import QUrl
from PySide6.QtWebEngineWidgets import QWebEngineView


class PreviewPanel(QWebEngineView):
    def __init__(self, regex_panel, katex_path=None):
        super().__init__()
        self.regex_panel = regex_panel

        if katex_path is not None:
            self.base_path = QUrl.fromLocalFile(str(katex_path) + "/")
        else:
             self.base_path = QUrl("https://cdn.jsdelivr.net/npm/katex@0.16.22/dist/")
    
    def set_html(self, html):
        self.setHtml(html, self.base_path)