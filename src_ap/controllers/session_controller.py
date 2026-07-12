from pathlib import Path


class SessionController:
    def __init__(self, config, persistence_service, main_window):
        self.config = config
        self.persistence = persistence_service
        self.main_window = main_window

    # --- THEME ---
    def set_theme(self, theme: str):
        self.config.settings.current.theme = theme
        self.persistence.save_config(self.config)

    def get_theme(self):
        return self.config.settings.current.theme

    # --- CATALOGUE ---
    def set_catalogue(self, catalogue: str | None):
        self.config.settings.current.catalogue = catalogue
        self.persistence.save_config(self.config)

    def get_catalogue(self):
        return self.config.settings.current.catalogue

    # --- TYPE ---
    def set_type(self, type_: str | None):
        self.config.settings.current.type = type_
        self.persistence.save_config(self.config)

    def get_type(self):
        return self.config.settings.current.type

    # --- FILE ---
    def set_current_file(self, path: str | None):
        self.config.settings.current.current_file_path = path
        self.persistence.save_config(self.config)

    def get_current_file(self):
        current_file_path = self.config.settings.current.current_file_path
        if current_file_path is None:
            return None
        return Path(current_file_path)

    def get_progression_dir(self):
        current_file_path = self.get_current_file()
        if current_file_path is not None:
            return current_file_path.parent
        return Path.cwd()
    # --- GUI ---
    def commit_gui_settings(self):
        self.init_save_main_window_settings(save=False)
        self.init_save_splitter_settings(save=False)
        self.init_save_unused_items_dialog_settings(save=False)
        self.persistence.save_config(self.config)

    def init_save_main_window_settings(self, save=True):
        self.config.settings.gui.main_window.width = self.main_window.width()
        self.config.settings.gui.main_window.height = self.main_window.height()
        if save:
            self.persistence.save_config(self.config)

    def init_save_splitter_settings(self, save=True):
        self.config.settings.gui.splitter.size = self.main_window.splitter.sizes()
        if save:
            self.persistence.save_config(self.config)
    
    def init_save_unused_items_dialog_settings(self, save=True):
        if self.main_window.unused_items_dialog is not None:
            self.config.settings.gui.unused_items_dialog.width = self.main_window.unused_items_dialog.width()
            self.config.settings.gui.unused_items_dialog.height = self.main_window.unused_items_dialog.height()
        if save:
            self.persistence.save_config(self.config)