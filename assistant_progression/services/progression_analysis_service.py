# assistant_progression/services/progression_analysis_service.py
from PySide6.QtCore import Qt
from assistant_progression.app.logger import logger, logger_wraper


class ProgressionAnalysisService:

    def __init__(self, catalogue_service):
        self.catalogue_service = catalogue_service

    def get_used_codes(self, tree):
        used = set()

        def scan(item):
            for i in range(item.childCount()):
                child = item.child(i)
                code = child.data(0, 0)
                if code:
                    used.add(code)
                scan(child)

        for i in range(tree.topLevelItemCount()):
            scan(tree.topLevelItem(i))

        return used

    def get_unused_entries(self, tree, selected_catalogue):

        selected_catalogue_name = selected_catalogue.name if selected_catalogue else "Tous"

        used = self.get_used_codes(tree)

        unused = []

        for entry in self.catalogue_service.entries:

            if selected_catalogue_name != "Tous":
                if entry.catalogue.name != selected_catalogue_name:
                    continue

            if entry.code not in used:
                unused.append(entry)

        return unused

    @logger_wraper
    def find_usage_locations(self, tree, entry):
        locations = []

        def scan(node, path):
            for i in range(node.childCount()):
                child = node.child(i)

                if child.data(0, Qt.UserRole) == entry.id:
                    locations.append(path)

                scan(child, path + "/" + child.text(0))

        for i in range(tree.topLevelItemCount()):
            root = tree.topLevelItem(i)
            scan(root, root.text(0))

        return locations