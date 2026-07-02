class SessionController:
    def __init__(self, config, persistence_service):
        self.config = config
        self.persistence = persistence_service

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
        return self.config.settings.current.current_file_path