
soothing = """
QWidget {
    background-color: #E6E2D3;  /* Soft cream background */
    color: #3D3D3D;  /* Soft dark text color for readability */
    font-family: 'Segoe UI', sans-serif;
    font-size: 12px;
}

QMainWindow {
    background-color: #E6E2D3;
}

/* Tables */
QTableWidget {
    background-color: #F4F1E1;  /* Very light beige background for tables */
    gridline-color: #D0C6A1;    /* Soft greenish gridlines */
    selection-background-color: #AEC4FF;  /* Selected item color (blueish) */
    selection-color: #3D3D3D;   /* Dark text for selection */
    border: 1px solid #D0C6A1;  /* Soft border color */
}

QHeaderView::section {
    background-color: #A0B49E;  /* Soft greenish beige for header */
    color: #3D3D3D;  /* Header text color */
    padding: 4px;
    border: 1px solid #D0C6A1;
    font-weight: bold;
}

/* Tabs */
QTabWidget::pane {
    border: 1px solid #D0C6A1;
    background: #E6E2D3;
}

QTabBar::tab {
    background: #F4F1E1;  /* Soft cream for tab background */
    color: #3D3D3D;  /* Dark text color for tabs */
    padding: 6px 12px;
    border: 1px solid #D0C6A1;
}

QTabBar::tab:selected {
    background: #A0B6C8;  /* Soft pastel blue for selected tab */
    border-bottom: 3px solid #D0C6A1;  /* Soft greenish border */
    font-weight: bold;
}

QTabBar::tab:hover {
    background: #D8D6CA;  /* Slightly darker cream when hovered */
}

/* Buttons */
QPushButton {
    background-color: #ADC1D7;  /* Softer blue-grey for button background */
    color: #3D3D3D;  /* Text color on buttons */
    border: 1px solid #D0C6A1;
    padding: 6px 14px;
    border-radius: 6px;
}

QPushButton:hover {
    background-color: #B6C8D8;  /* Slightly lighter blue-grey on hover */
}

QPushButton:pressed {
    background-color: #A0B6C8;  /* Softer blue-grey when pressed */
}

/* Console */
QTextEdit {
    background-color: #F4F1E1;  /* Very light cream background for console */
    border: 1px solid #D0C6A1;  /* Soft border for text area */
}

/* Splitter */
QSplitter::handle {
    background-color: #D0C6A1;  /* Soft greenish beige for splitter */
}

/* Scrollbars */
QScrollBar:vertical {
    background: #F4F1E1;
    width: 10px;
}

QScrollBar::handle:vertical {
    background: #D0C6A1;
    min-height: 20px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #B8D8FF;
}

/* Alerts */
QLabel#alert {
    color: #FFB47D;  /* Soft peach for alerts */
}

QLabel#success {
    color: #B2E6C7;  /* Soft green for success messages */
}

QLabel#info {
    color: #AEC4FF;  /* Soft pastel blue for informational messages */
}

QLabel#highlight {
    color: #FFFFB4;  /* Soft pastel yellow for highlighted text */
}
"""

vscode_dark = """
QWidget {
    background-color: #1e1e1e;  /* Dark Modern editor background */
    color: #cccccc;             /* Default text color */
    font-family: 'Segoe UI', sans-serif;
    font-size: 12px;
}

QMainWindow {
    background-color: #1e1e1e;
}

/* Tables */
QTableWidget {
    background-color: #252526;  /* Sidebar/panel background */
    gridline-color: #3c3c3c;    /* Subtle grid lines */
    selection-background-color: #264f78;  /* VS Code selection blue */
    selection-color: #ffffff;
    border: 1px solid #3c3c3c;
}

QHeaderView::section {
    background-color: #2d2d2d;  /* Header background */
    color: #cccccc;
    padding: 4px;
    border: 1px solid #3c3c3c;
    font-weight: bold;
}

/* Tabs */
QTabWidget::pane {
    border: 1px solid #3c3c3c;
    background: #1e1e1e;
}

QTabBar::tab {
    background: #2d2d2d;        /* Inactive tab background */
    color: #969696;             /* Inactive tab text */
    padding: 6px 12px;
    border: 1px solid #252526;
    border-bottom: none;
}

QTabBar::tab:selected {
    background: #1e1e1e;        /* Active tab matches editor */
    color: #ffffff;
    border-top: 1px solid #007acc;  /* VS Code blue top border on active tab */
    font-weight: bold;
}

QTabBar::tab:hover {
    background: #2a2a2a;
    color: #cccccc;
}

/* Buttons */
QPushButton {
    background-color: #0e639c;  /* VS Code primary button blue */
    color: #ffffff;
    border: 1px solid #0e639c;
    padding: 6px 14px;
    border-radius: 2px;
}

QPushButton:hover {
    background-color: #1177bb;  /* Lighter blue on hover */
    border-color: #1177bb;
}

QPushButton:pressed {
    background-color: #0d5a8e;  /* Darker blue when pressed */
}

/* Console / Text areas */
QTextEdit {
    background-color: #1e1e1e;
    color: #d4d4d4;             /* Editor foreground */
    border: 1px solid #3c3c3c;
}

/* Splitter */
QSplitter::handle {
    background-color: #3c3c3c;
}

/* Scrollbars */
QScrollBar:vertical {
    background: #1e1e1e;
    width: 10px;
}

QScrollBar::handle:vertical {
    background: #4e4e4e;
    min-height: 20px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #686868;
}

/* Alerts */
QLabel#alert {
    color: #f48771;  /* VS Code error/warning red-orange */
}

QLabel#success {
    color: #89d185;  /* VS Code terminal green */
}

QLabel#info {
    color: #75beff;  /* VS Code info blue */
}

QLabel#highlight {
    color: #dcdcaa;  /* VS Code yellow (function names) */
}
"""

modern_dark = """
QWidget {
    background-color: #202124;
    color: #e8eaed;
    font-family: 'Segoe UI', sans-serif;
    font-size: 12px;
}

/* Main Window */

QMainWindow {
    background-color: #202124;
}

/* ===========================
   Menu
   =========================== */

QMenuBar {
    background: #2b2d31;
    border-bottom: 1px solid #3d4045;
}

QMenuBar::item {
    padding: 4px 10px;
    background: transparent;
}

QMenuBar::item:selected {
    background: #4f8cff;
    color: white;
}

QMenu {
    background: #2b2d31;
    border: 1px solid #3d4045;
}

QMenu::item {
    padding: 6px 20px;
}

QMenu::item:selected {
    background: #4f8cff;
    color: white;
}

QMenu::item:disabled:selected {
    background: transparent;
    color: #777777;
}

/* ===========================
   Buttons
   =========================== */

QPushButton {
    background: #2b2d31;
    color: #e8eaed;
    border: 1px solid #3d4045;
    padding: 6px 14px;
    border-radius: 4px;
}

QPushButton:hover {
    border: 1px solid #4f8cff;
}

QPushButton:pressed {
    background: #3a4658;
}

QPushButton:disabled {
    color: #777777;
}

/* ===========================
   Tables
   =========================== */

QTableWidget {
    background: #2b2d31;
    alternate-background-color: #24262a;
    color: #e8eaed;
    gridline-color: #3d4045;
    border: 1px solid #3d4045;
    selection-background-color: #4f8cff;
    selection-color: white;
}

QHeaderView::section {
    background: #2b2d31;
    color: #e8eaed;
    border: 1px solid #3d4045;
    padding: 5px;
    font-weight: bold;
}

/* ===========================
   Tabs
   =========================== */

QTabWidget::pane {
    border: 1px solid #3d4045;
    background: #202124;
}

QTabBar::tab {
    background: #2b2d31;
    color: #bbbbbb;
    padding: 6px 14px;
    border: 1px solid #3d4045;
    border-bottom: none;
}

QTabBar::tab:selected {
    background: #202124;
    color: white;
    border-top: 2px solid #4f8cff;
    font-weight: bold;
}

QTabBar::tab:hover {
    border-color: #4f8cff;
}

/* ===========================
   Text areas
   =========================== */

QTextEdit {
    background: #2b2d31;
    color: #e8eaed;
    border: 1px solid #3d4045;
}

QLineEdit {
    background: #2b2d31;
    color: #e8eaed;
    border: 1px solid #3d4045;
    padding: 4px;
}

QLineEdit:focus {
    border: 2px solid #4f8cff;
}

/* ===========================
   Splitter
   =========================== */

QSplitter::handle {
    background: #3d4045;
}

QSplitter::handle:hover {
    background: #4f8cff;
}

/* ===========================
   ScrollBars
   =========================== */

QScrollBar:vertical {
    background: #202124;
    width: 10px;
}

QScrollBar::handle:vertical {
    background: #50545a;
    border-radius: 4px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background: #4f8cff;
}

/* ===========================
   Alerts
   =========================== */

QLabel#alert {
    color: #ff6b6b;
}

QLabel#success {
    color: #5fd38d;
}

QLabel#info {
    color: #6fb8ff;
}

QLabel#highlight {
    color: #ffd86b;
}
"""

fusion_modern_dark_red = """
QWidget {
    background-color: #232326;
    color: #ECECEC;
    font-family: "Latin Modern Roman";
    font-size: 12px;
}

QMainWindow {
    background: #232326;
}

/* ===========================
   Menu
   =========================== */

QMenuBar {
    background: #2D2D31;
    border-bottom: 1px solid #45454A;
}

QMenuBar::item {
    padding: 5px 10px;
    background: transparent;
}

QMenuBar::item:selected {
    background: #8E2A2A;
    color: white;
}

QMenu {
    background: #2D2D31;
    border: 1px solid #45454A;
}

QMenu::item {
    padding: 6px 22px;
    color: #ECECEC;
}

QMenu::item:disabled {
    color: #777777;
}

QMenu::item:selected:enabled {
    background: #8E2A2A;
    color: white;
}

QMenu::item:selected:disabled {
    background: transparent;
    color: #777777;
}

/* ===========================
   Buttons
   =========================== */

QPushButton {
    background: #34343A;
    color: #ECECEC;
    border: 1px solid #55555A;
    border-radius: 5px;
    padding: 6px 14px;
}

QPushButton:hover {
    border: 1px solid #B33939;
    background: #3A3A40;
}

QPushButton:pressed {
    background: #8E2A2A;
    border: 1px solid #B33939;
}

QPushButton:disabled {
    color: #777777;
}

/* ===========================
   Tables
   =========================== */

QTableWidget {
    background: #2C2C31;
    alternate-background-color: #303036;
    color: #ECECEC;
    gridline-color: #45454A;
    border: 1px solid #45454A;
    selection-background-color: #8E2A2A;
    selection-color: white;
}

QHeaderView::section {
    background: #34343A;
    color: white;
    padding: 5px;
    border: 1px solid #45454A;
    font-weight: bold;
}

/* ===========================
   Tabs
   =========================== */

QTabWidget::pane {
    border: 1px solid #45454A;
    background: #232326;
}

QTabBar::tab {
    background: #34343A;
    color: #BBBBBB;
    padding: 6px 15px;
    border: 1px solid #45454A;
    border-bottom: none;
}

QTabBar::tab:selected {
    background: #232326;
    color: white;
    border-top: 3px solid #B33939;
    font-weight: bold;
}

QTabBar::tab:hover {
    border-color: #B33939;
}

/* ===========================
   Text
   =========================== */

QTextEdit,
QPlainTextEdit {
    background: #2C2C31;
    color: #ECECEC;
    border: 1px solid #45454A;
}

QLineEdit,
QComboBox,
QSpinBox,
QDoubleSpinBox {
    background: #2C2C31;
    color: #ECECEC;
    border: 1px solid #55555A;
    border-radius: 4px;
    padding: 4px;
}

QLineEdit:focus,
QComboBox:focus,
QSpinBox:focus,
QDoubleSpinBox:focus {
    border: 2px solid #B33939;
}

/* ===========================
   ComboBox
   =========================== */

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox QAbstractItemView {
    background: #2D2D31;
    color: white;
    selection-background-color: #8E2A2A;
}

/* ===========================
   Tree / List
   =========================== */

QTreeView,
QListView {
    background: #2C2C31;
    border: 1px solid #45454A;
    alternate-background-color: #303036;
}

QTreeView::item:selected,
QListView::item:selected {
    background: #8E2A2A;
}

/* ===========================
   Scrollbars
   =========================== */

QScrollBar:vertical {
    background: #232326;
    width: 10px;
}

QScrollBar::handle:vertical {
    background: #5A5A60;
    border-radius: 5px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background: #B33939;
}

QScrollBar::add-line,
QScrollBar::sub-line {
    height: 0px;
}

/* ===========================
   Splitter
   =========================== */

QSplitter::handle {
    background: #45454A;
}

QSplitter::handle:hover {
    background: #B33939;
}

/* ===========================
   Status Bar
   =========================== */

QStatusBar {
    background: #2D2D31;
    border-top: 1px solid #45454A;
}

/* ===========================
   Alerts
   =========================== */

QLabel#alert {
    color: #FF6666;
}

QLabel#success {
    color: #63D471;
}

QLabel#info {
    color: #74B9FF;
}

QLabel#highlight {
    color: #FF5A5A;
}
"""

THEMES = {
    "VS Code Dark": vscode_dark,
    "Soothing": soothing,
    "Modern Dark": modern_dark,
    "Fusion Modern Dark Red": fusion_modern_dark_red,
}