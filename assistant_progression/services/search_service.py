from assistant_progression.services.code_service import CodeService


class SearchService:

    def __init__(self, code_service: CodeService):
        self.code_service = code_service

    def selected_catalogue(self, catalogue_combo):

        return self.code_service.internal_name(
            catalogue_combo.currentText()
        )

    def selected_type(self, type_combo):

        return self.code_service.internal_name(
            type_combo.currentText()
        )

    def populate_filters(self, catalogue_combo):

        catalogue_combo.clear()

        catalogue_combo.addItem("Tous")

        for catalogue in self.code_service.get_catalogues():

            catalogue_combo.addItem(
                self.code_service.display_name(
                    catalogue
                )
            )

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

        for source_type in self.code_service.get_types(
            current_catalogue
        ):

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

        return self.code_service.search(
            catalogue=selected_catalogue,
            source_type=selected_type,
            regex_text=regex_text
        )