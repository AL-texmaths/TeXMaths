# search_service.py
from assistant_progression.services.code_service import CodeService
from assistant_progression.services.catalogue_service import CatalogueService, Catalogue


class SearchService:

    def __init__(self, code_service: CodeService, catalogue_service: CatalogueService):
        self.code_service = code_service
        self.catalogue_service = catalogue_service

    def selected_catalogue(self, catalogue_combo):

        return self.catalogue_service.get_catalogue_from_name(
            catalogue_combo.currentText()
        )

    def selected_type(self, type_combo):

        return self.code_service.internal_name(
            type_combo.currentText()
        )

    def populate_filters(self, catalogue_combo):

        catalogue_combo.clear()

        for catalogue_key in self.catalogue_service.catalogues.keys():

            catalogue = self.catalogue_service.get_catalogue(catalogue_key)

            catalogue_combo.addItem(catalogue.name)
            

    def update_type_filter(
        self,
        catalogue_combo,
        type_combo
    ):

        current_catalogue = self.selected_catalogue(
            catalogue_combo
        )

        type_combo.blockSignals(True)

        type_combo.clear()

        type_combo.addItem("Tous")

        for source_type in current_catalogue.types:

            type_combo.addItem(
                self.code_service.display_name(
                    source_type
                )
            )

        type_combo.blockSignals(False)

    def search(
        self,
        catalogue_combo,
        type_combo,
        regex_text
    ):

        selected_catalogue = self.selected_catalogue(
            catalogue_combo
        )

        selected_type = self.selected_type(
            type_combo
        )

        return self.catalogue_service.search(
            catalogue_name=selected_catalogue.name if selected_catalogue else None,
            source_type=selected_type,
            regex_text=regex_text
        )