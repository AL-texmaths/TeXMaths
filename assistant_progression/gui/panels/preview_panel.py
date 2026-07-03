from PySide6.QtCore import QUrl
from PySide6.QtWebEngineWidgets import QWebEngineView
from assistant_progression.services.html_service import HtmlService
from assistant_progression.gui.panels.regex_panel import ViewMode

class PreviewPanel(QWebEngineView):
    def __init__(self, regex_panel, progression_panel, theme_service, code_service, analysis_service, katex_path=None):
        super().__init__()
        self.regex_panel = regex_panel
        self.progression_panel = progression_panel
        self.theme_service = theme_service
        self.code_service = code_service
        self.analysis_service = analysis_service
        self.html_service = HtmlService()

        if katex_path is not None:
            self.base_path = QUrl.fromLocalFile(str(katex_path) + "/")
        else:
             self.base_path = QUrl("https://cdn.jsdelivr.net/npm/katex@0.16.22/dist/")
    
    def set_html(self, html):
        self.setHtml(html, self.base_path)
    
    def show_list_view(self):
        html_items = []

        for entry in self.regex_panel.current_matches:

            html_items.append(
                (
                    f"<b>{entry.code}</b> "
                    f"(<i>{entry.catalogue}</i>) "
                    f"{entry.text}"
                )
            )

        html_no_render = "<br>".join(html_items)
        html = self.html_service.render_list(html_no_render, self.theme_service.get_current_theme())

        self.set_html(html)
    

    def show_entry_view(self):

        row = self.regex_panel.list_widget.currentRow()

        if row < 0 or row >= len(self.regex_panel.current_matches):
            html = self.html_service.render_entry(
                code="",
                content="",
                catalogue=self.regex_panel.selected_catalogue().name,
                source_type="",
                theme=self.theme_service.get_current_theme(),
            )
            self.set_html(html)
            return

        entry = self.regex_panel.current_matches[row]

        html = self.html_service.render_entry(
            code=entry.code,
            content=entry.text,
            catalogue=entry.catalogue,
            source_type=self.code_service.display_name(entry.type),
            theme=self.theme_service.get_current_theme(),
            locations=self.analysis_service.find_usage_locations(
                self.progression_panel.progression_tree,
                entry
                )
        )

        self.set_html(html)
    
    def refresh_view(self):
        mode = self.regex_panel.view_mode_combo.currentText()

        if mode == ViewMode.FILTERED_LIST:
            self.show_list_view()
        elif mode == ViewMode.SINGLE:
            self.show_entry_view()