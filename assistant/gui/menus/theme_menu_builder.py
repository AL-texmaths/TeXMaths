from PySide6.QtGui import QAction
from PySide6.QtCore import QTimer


class ThemeMenuBuilder:

    def __init__(self, theme_service, action_method, preview_method):
        self.theme_service = theme_service
        self.action_method = action_method
        self._preview_method = preview_method
        self.current_theme_name = None
        self._hover_timer = QTimer()
        self._hover_timer.setSingleShot(True)
        self._hover_timer.timeout.connect(self._apply_preview)
        self._pending_theme = None

    def _apply_preview(self):
        """Apply the pending preview after debounce delay."""
        if self._pending_theme is not None:
            self.preview_method(self._pending_theme)
    
    def preview_method(self, name):
        if name != self.current_theme_name:
            self.current_theme_name = name
            self._preview_method(name)

    def populate(self, menu):

        menu.clear()

        for theme_name in self.theme_service.get_theme_names():

            action = QAction(theme_name, menu)
            action.triggered.connect(
                lambda checked, name=theme_name:
                    self.action_method(name)
            )

            menu.addAction(action)
            action.hovered.connect(
                lambda name=theme_name:
                    self.preview_method(name)
            )
    
    def _schedule_preview(self, theme_name):
        """Schedule a preview with debouncing to prevent multiple rapid calls."""
        self._pending_theme = theme_name
        self._hover_timer.stop()
        self._hover_timer.start(50)  # 50ms debounce
