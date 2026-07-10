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
        theme = self.get_current_theme()
        colors = theme.colors
        style = theme.style
    
        focus_bg = colors.focus_bg
        focus_border = colors.focus_border

        widget.setStyleSheet(f"""

/* ==========================================================
   Widget de base
   ========================================================== */

QWidget {{
    background: {colors.bg};
    color: {colors.fg};
    font-family: "{style.font.family}";
    font-size: {style.font.size};
}}

/* ==========================================================
   Menus
   ========================================================== */

QMenuBar {{
    background: {colors.panel};
    border-bottom: 1px solid {colors.border};
}}

QMenuBar::item {{
    padding: 4px 10px;
}}

QMenuBar::item:selected {{
    background: {colors.accent};
    color: white;
}}

QMenu {{
    background: {colors.panel};
    border: 1px solid {colors.border};
}}

QMenu::item:selected {{
    background: {colors.accent};
    color: white;
}}

QMenu::item:disabled {{
    color: {colors.border};
}}

/* ==========================================================
   Boutons
   ========================================================== */

QPushButton {{
    background: {colors.panel};
    border: 1px solid {colors.border};
    padding: 6px;
    border-radius: 4px;
}}

QPushButton:hover {{
    border: 1px solid {colors.accent};
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
    background: {colors.panel};
    color: {colors.fg};
    border: 1px solid {colors.border};
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
    background: {colors.accent};
    color: white;
}}

/* ==========================================================
   TreeWidget
   ========================================================== */

QTreeWidget {{
    alternate-background-color: {focus_bg};
}}

QTreeWidget::item {{
    height: {style.progression_tree.items_height};
    padding: {style.progression_tree.padding};
}}

QTreeWidget::item:selected {{
    background: {colors.accent};
    color: white;
}}

/* ==========================================================
   Header du TreeWidget
   ========================================================== */

QHeaderView::section {{
    background: {colors.panel};
    color: {colors.fg};
    border: 1px solid {colors.border};
    padding: 5px;
    font-weight: bold;
}}

/* ==========================================================
   Splitter
   ========================================================== */

QSplitter::handle {{
    background: {colors.border};
}}

QSplitter::handle:hover {{
    background: {colors.accent};
}}

/* ==========================================================
   Onglets (Tabs)
   ========================================================== */

QTabWidget::pane {{
    border: 1px solid {colors.border};
    background: {colors.bg};
}}

QTabBar::tab {{
    background: {colors.panel};
    color: {colors.fg};
    padding: 6px 12px;
    border: 1px solid {colors.border};
    border-bottom: none;
    margin-right: 2px;
}}

QTabBar::tab:selected {{
    background: {colors.accent};
    color: white;
    border: 1px solid {colors.border};
    border-bottom: 3px solid {colors.accent};
    font-weight: bold;
}}

QTabBar::tab:hover {{
    background: {focus_bg};
}}

""")