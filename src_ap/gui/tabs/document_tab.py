from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QSplitter,
    QComboBox,
    )
from src_ap.models.search_filters import SearchFilters
from src_ap.gui.widgets.pdf_viewer import PdfViewerWidget
from src_ap.gui.widgets.metadata_view import MetadataView
from src_ap.controllers.search_pdf_controller import SearchPDFController
from src_ap.controllers.pdf_documents_controller import PdfDocumentsController
from src_ap.gui.widgets.results_list import ResultsList
from src_ap.gui.widgets.search_input import SearchInput


class DocumentTab(QWidget):
    def __init__(self, context, filter_pdf_doc_menu):
        super().__init__()
        self.context = context
        self.filter_pdf_doc_menu = filter_pdf_doc_menu

        self.pdf_viewer = PdfViewerWidget()
        self.pdf_documents_controller = PdfDocumentsController(context)
        layout = QVBoxLayout(self)
        self.horizontal_splitter = QSplitter(Qt.Horizontal)

        # search layout
        left_layout = QVBoxLayout()
    
        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        self.horizontal_splitter.addWidget(left_widget)

        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        self.inner_splitter = QSplitter(Qt.Vertical)
        self.inner_splitter.addWidget(self.pdf_viewer.view)
        self.inner_splitter.setStretchFactor(0, 3)
        self.inner_splitter.setStretchFactor(1, 1)

        self.metadata_view = MetadataView(self.context)
        self.inner_splitter.addWidget(
            self.metadata_view
        )

        self.results_list = ResultsList(
            self.context,
            self.pdf_viewer,
            self.pdf_documents_controller,
            self.metadata_view
            )
        self.results_list.installEventFilter(self)
        
        self.search_input = SearchInput(self.update_results, self.results_list)
        self.search_input.installEventFilter(self)

        left_layout.addWidget(self.search_input)
        left_layout.addWidget(self.results_list)

        right_layout.addWidget(self.inner_splitter)
        QTimer.singleShot(0, self.search_input.setFocus)
        self.horizontal_splitter.addWidget(right_widget)

        layout.addWidget(self.horizontal_splitter)

        self.key_filter_actions = {}
        self.field_actions = {}

        self.sort_order_combo = QComboBox()
        self.sort_order_combo.addItem("Trier par ordre alphabétique")
        self.sort_order_combo.addItem("Trier par date de modification")
        # Défaut : trier par date de modification
        self.sort_order_combo.setCurrentIndex(1)
        self.sort_order_combo.currentIndexChanged.connect(self.update_results)
        left_layout.addWidget(self.sort_order_combo)

        self.search_pdf_controller = SearchPDFController(self.context.search_pdf_service)

        # Initialize save timers for debouncing splitter changes
        self._save_splitter_settings_timer = QTimer()
        self._save_splitter_settings_timer.setSingleShot(True)
        self._save_splitter_settings_timer.timeout.connect(self._save_splitter_settings_debounced)
        
        # Flag to load splitter sizes on first show
        self._splitter_sizes_loaded = False
        
        # Connect splitter changes to debounced save
        self.horizontal_splitter.splitterMoved.connect(self._schedule_save_splitter_settings)
        self.inner_splitter.splitterMoved.connect(self._schedule_save_splitter_settings)
    
    def showEvent(self, event):
        """Load splitter sizes when the widget is first shown."""
        super().showEvent(event)
        if not self._splitter_sizes_loaded:
            self._splitter_sizes_loaded = True
            self._load_splitter_sizes()
    
    def _load_splitter_sizes(self):
        """Load splitter sizes from config, apply defaults if not available."""
        try:
            saved_vertical = self.context.config.settings.gui.documents_tab.vertical_splitter
            saved_horizontal = self.context.config.settings.gui.documents_tab.horizontal_splitter
            
            # Get actual widget dimensions
            height = self.height()
            width = self.width()
            
            # Ensure we have reasonable dimensions
            if height <= 0:
                height = 600
            if width <= 0:
                width = 1000
            
            # Apply vertical splitter (bottom panel height)
            if saved_vertical and saved_vertical > 0 and saved_vertical < height - 120:
                top = height - saved_vertical
                self.inner_splitter.setSizes([top, saved_vertical])
            else:
                # Default: 75% top (PDF), 25% bottom (metadata)
                top = int(height * 0.75)
                bottom = height - top
                if bottom < 120:
                    bottom = 120
                    top = height - bottom
                self.inner_splitter.setSizes([top, bottom])
            
            # Apply horizontal splitter (right panel width)
            if saved_horizontal and saved_horizontal > 0 and saved_horizontal < width - 200:
                left_width = width - saved_horizontal
                self.horizontal_splitter.setSizes([left_width, saved_horizontal])
            else:
                # Default: left panel 60%, right panel 40%
                right_width = int(width * 0.4)
                left_width = width - right_width
                if left_width < 200:
                    left_width = 200
                    right_width = width - left_width
                self.horizontal_splitter.setSizes([left_width, right_width])
        except Exception as e:
            # Fallback to default sizes
            try:
                height = max(600, self.height())
                width = max(1000, self.width())
                
                # Vertical: 75% top, 25% bottom
                top = int(height * 0.75)
                bottom = height - top
                if bottom < 120:
                    bottom = 120
                    top = height - bottom
                self.inner_splitter.setSizes([top, bottom])
                
                # Horizontal: 60% left, 40% right
                right_width = int(width * 0.4)
                left_width = width - right_width
                self.horizontal_splitter.setSizes([left_width, right_width])
            except Exception as e2:
                print(f"Error applying default splitter sizes: {e2}")
    
    def _schedule_save_splitter_settings(self):
        """Schedule a debounced save of splitter settings."""
        self._save_splitter_settings_timer.stop()
        self._save_splitter_settings_timer.start(500)  # 500ms debounce
    
    def _save_splitter_settings_debounced(self):
        """Save splitter settings after debounce delay."""
        try:
            # Get horizontal splitter size (right panel width)
            if self.horizontal_splitter.sizes():
                sizes = self.horizontal_splitter.sizes()
                if len(sizes) >= 2:
                    self.context.config.settings.gui.documents_tab.horizontal_splitter = sizes[1]
            
            # Get vertical splitter size (bottom panel height)
            if self.inner_splitter.sizes():
                sizes = self.inner_splitter.sizes()
                if len(sizes) >= 2:
                    self.context.config.settings.gui.documents_tab.vertical_splitter = sizes[1]
            
            # Save config
            self.context.persistence_service.save_config(self.context.config)
        except Exception as e:
            print(f"Error saving splitter settings: {e}")
    
    def build_search_filters(self) -> SearchFilters:

        return SearchFilters(
            pattern=self.search_input.text().strip(),
            active_prefixes=self.filter_pdf_doc_menu.get_checked_types(),
            active_fields=self.filter_pdf_doc_menu.get_checked_fields(),
            sort_mode=self.sort_order_combo.currentIndex(),
        )

    def update_results(self):

        filters = self.build_search_filters()

        results = self.search_pdf_controller.search(filters)

        self.results_list.clear()

        for key, _ in results:
            self.results_list.addItem(key)
    
    def load_data(self):
        self.context.pedago_data_service.refresh()
        types = self.context.pedago_data_service.get_types()
        fields = self.context.pedago_data_service.get_fields()

        self.filter_pdf_doc_menu.rebuild_types_menu(types)
        self.filter_pdf_doc_menu.rebuild_fields_menu(fields)
    