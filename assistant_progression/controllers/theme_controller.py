# theme_controller.py
from assistant_progression.services.theme_service import ThemeService
from assistant_progression.services.persistence_service import PersistenceService
from assistant_progression.models.config import Config


class ThemeController:
    def __init__(
            self,
            theme_service:ThemeService,
            persistence_service:PersistenceService,
            config: Config,
            on_theme_changed=lambda:None
            ):
        self.theme_service = theme_service
        self.persistence_service = persistence_service
        self.config = config
        self.on_theme_changed = on_theme_changed
        self._saved_theme = None
        self._theme_committed = False

    def begin_preview(self):
        self._saved_theme = self.theme_service.get_current_theme_name()
        self._theme_committed = False
    
    def cancel_preview(self):
        if self._theme_committed:
            return

        if self._saved_theme:
            self.theme_service.set_theme(self._saved_theme)
        self.on_theme_changed()
    
    def commit_theme(self, name):
        self._theme_committed = True

        self.theme_service.set_theme(name)

        self.config.settings.current.theme = name
        self.persistence_service.save_config(self.config)
        self.on_theme_changed()
    
    def set_theme(self, name):
        self.theme_service.set_theme(name)
        self.on_theme_changed()