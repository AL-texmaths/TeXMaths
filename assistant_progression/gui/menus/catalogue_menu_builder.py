from PySide6.QtGui import QAction


class CatalogueMenuBuilder:

    def __init__(self, catalogue_service, texmf_path, config):
        self.catalogue_service = catalogue_service
        self.texmf_path = texmf_path
        self.config = config

    def populate(self, menu):

        menu.clear()

        for catalogue_name in self.catalogue_service.get_catalogue_names():

            if catalogue_name == "Tous":
                continue

            action = QAction(catalogue_name, menu)
            action.triggered.connect(
                lambda checked=False, name=catalogue_name:
                    self.catalogue_service.open_catalogue_package(
                        name, self.texmf_path, self.config
                    )
            )

            menu.addAction(action)