from PySide6.QtGui import QAction


class ThemeMenuBuilder:

    def __init__(self, theme_service, action_method, preview_method):
        self.theme_service = theme_service
        self.action_method = action_method
        self.preview_method = preview_method

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
