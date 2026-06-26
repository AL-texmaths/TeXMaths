# assistant_progression/services/theme_service.py

class ThemeService:
    def __init__(self, themes, default_theme):
        self.themes = themes
        self.current_theme = default_theme

    def set_theme(self, name: str):
        if name in self.themes:
            self.current_theme = name

    def get_current_theme(self):
        return self.themes[self.current_theme]

    def apply(self, widget):
        t = self.get_current_theme()

        focus_bg = t.get("focus_bg", t["panel"])
        focus_border = t.get("focus_border", t["accent"])

        widget.setStyleSheet(f"""
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

            QListWidget::item:selected {{
                background-color: {t['accent']};
                color: white;
            }}
        """)
    
    def get_theme_names(self):
        return self.themes.keys()