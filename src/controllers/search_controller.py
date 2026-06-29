class SearchController:

    def __init__(
        self,
        search_service,
    ):
        self.search_service = search_service

    def search(self, filters):
        return self.search_service.search(filters)