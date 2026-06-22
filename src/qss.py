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