from PySide6.QtCore import Signal

class ResultsListWidget:

    documentSelected = Signal(str)
    openPdfRequested = Signal(str)
    openTexRequested = Signal(str)
    
    # utilisation ailleurs :
    # results_widget.documentSelected.connect(
    #     controller.load_document
    # )

    def __init__(self):
        """"""

    def display_results(self):
        """"""
    
    def show_reults_context_menu(self):
        """"""
    
    # méthodes : keyboard navigation
    def keyPressEvent(self, event):
        """"""
    
    def eventFilter(self, obj, event):
        """"""
