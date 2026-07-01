# assistant_progression/services/progression_analysis_service.py

class ProgressionAnalysisService:

    def __init__(self, code_service):
        self.code_service = code_service

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
        used = self.get_used_codes(tree)

        unused = []

        for entry in self.code_service.entries:

            if selected_catalogue != "Tous":
                if entry.catalogue != selected_catalogue:
                    continue

            if entry.code not in used:
                unused.append(entry)

        return unused

    def find_usage_locations(self, tree, code):
        locations = []

        def scan(node, path):
            for i in range(node.childCount()):
                child = node.child(i)

                if child.data(0, 0) == code:
                    locations.append(path)

                scan(child, path + "/" + child.text(0))

        for i in range(tree.topLevelItemCount()):
            root = tree.topLevelItem(i)
            scan(root, root.text(0))

        return locations