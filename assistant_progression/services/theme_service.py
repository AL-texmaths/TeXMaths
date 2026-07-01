class ThemeService:
    def __init__(self, themes, default_theme):
        self.themes = themes
        self.current_theme = default_theme

    def get_current_theme_name(self):
        return self.current_theme

    def set_theme(self, name):
        if name in self.themes:
            self.current_theme = name

    def get_current_theme(self):
        return self.themes[self.current_theme]

    def get_theme_names(self):
        return self.themes.keys()

    def apply(self, widget):
        t = self.get_current_theme()

        focus_bg = t.get("focus_bg", t["panel"])
        focus_border = t.get("focus_border", t["accent"])

        widget.setStyleSheet(f"""

/* ==========================================================
   Widget de base
   ========================================================== */

QWidget {{
    background: {t['bg']};
    color: {t['fg']};
    font-family: "{t['font']}";
}}

/* ==========================================================
   Menus
   ========================================================== */

QMenuBar {{
    background: {t['panel']};
    border-bottom: 1px solid {t['border']};
}}

QMenuBar::item {{
    padding: 4px 10px;
}}

QMenuBar::item:selected {{
    background: {t['accent']};
    color: white;
}}

QMenu {{
    background: {t['panel']};
    border: 1px solid {t['border']};
}}

QMenu::item:selected {{
    background: {t['accent']};
    color: white;
}}

QMenu::item:disabled {{
    color: {t['border']};
}}

/* ==========================================================
   Boutons
   ========================================================== */

QPushButton {{
    background: {t['panel']};
    border: 1px solid {t['border']};
    padding: 6px;
    border-radius: 4px;
}}

QPushButton:hover {{
    border: 1px solid {t['accent']};
}}

QPushButton:pressed {{
    background: {focus_bg};
}}

QPushButton:disabled {{
    color: #777;
}}

/* ==========================================================
   Widgets d'édition
   ========================================================== */

QLineEdit,
QComboBox,
QListWidget,
QTreeWidget {{
    background: {t['panel']};
    color: {t['fg']};
    border: 1px solid {t['border']};
}}

QLineEdit,
QComboBox {{
    padding: 4px;
}}

QLineEdit:focus,
QComboBox:focus,
QListWidget:focus,
QTreeWidget:focus {{
    border: 2px solid {focus_border};
}}

/* ==========================================================
   Listes
   ========================================================== */

QListWidget::item {{
    padding: 3px;
}}

QListWidget::item:selected {{
    background: {t['accent']};
    color: white;
}}

/* ==========================================================
   TreeWidget
   ========================================================== */

QTreeWidget {{
    alternate-background-color: {focus_bg};
}}

QTreeWidget::item {{
    height: 28px;
    padding: 2px;
}}

QTreeWidget::item:selected {{
    background: {t['accent']};
    color: white;
}}

/* ==========================================================
   Header du TreeWidget
   ========================================================== */

QHeaderView::section {{
    background: {t['panel']};
    color: {t['fg']};
    border: 1px solid {t['border']};
    padding: 5px;
    font-weight: bold;
}}

/* ==========================================================
   Splitter
   ========================================================== */

QSplitter::handle {{
    background: {t['border']};
}}

QSplitter::handle:hover {{
    background: {t['accent']};
}}

""")