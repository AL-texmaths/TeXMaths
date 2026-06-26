# assistant_progression/services/progression_service.py

from PySide6.QtWidgets import QTreeWidgetItem
from PySide6.QtCore import Qt


class ProgressionService:

    def __init__(self, catalogue_service, analysis_service, config):
        self.catalogue_service = catalogue_service
        self.analysis_service = analysis_service
        self.config = config

    def is_aut_obj_pro_catalogue(self, catalogue):
        return catalogue in self.config.get(
            "aut obj pro catalogues",
            []
        )

    def add_level(self, tree):
        item = QTreeWidgetItem(["Nouveau niveau"])
        item.setFlags(item.flags() | Qt.ItemIsEditable)
        tree.addTopLevelItem(item)
        tree.setCurrentItem(item)
        return item

    def add_chapter(self, tree, selected_catalogue, current_item):

        if current_item is None:
            return None

        if current_item.parent() is not None:
            current_item = current_item.parent()

        item = QTreeWidgetItem(["Nouveau chapitre"])
        item.setFlags(item.flags() | Qt.ItemIsEditable)

        if self.is_aut_obj_pro_catalogue(selected_catalogue):

            for code in ("aut", "obj", "pro", "sea"):

                item.addChild(
                    QTreeWidgetItem([
                        self.catalogue_service.code_label(code)
                    ])
                )

        item.setFlags(item.flags() | Qt.ItemIsEditable)
        current_item.addChild(item)
        tree.setCurrentItem(item)

        return item

    def delete_item(self, tree):
        item = tree.currentItem()
        if not item:
            return

        parent = item.parent()

        if parent:
            parent.removeChild(item)
        else:
            tree.takeTopLevelItem(tree.indexOfTopLevelItem(item))

    def move_item(self, tree, delta):
        item = tree.currentItem()
        if not item:
            return

        parent = item.parent()

        if parent:
            index = parent.indexOfChild(item)
            new = index + delta

            if 0 <= new < parent.childCount():
                parent.takeChild(index)
                parent.insertChild(new, item)

        else:
            index = tree.indexOfTopLevelItem(item)
            new = index + delta

            if 0 <= new < tree.topLevelItemCount():
                tree.takeTopLevelItem(index)
                tree.insertTopLevelItem(new, item)

        tree.setCurrentItem(item)

    def add_selected_item(self, tree, entry):

        selected = tree.currentItem()

        if selected is None:
            return None

        # équivalent de l'ancien is_chapter()
        if (
            selected.parent() is None
            or selected.data(0, Qt.UserRole) is not None
        ):
            return None

        target_label = self.catalogue_service.code_label(
            entry.type
        )

        target = None

        for i in range(selected.childCount()):

            child = selected.child(i)

            if child.text(0) == target_label:
                target = child
                break

        if target is None:
            return None

        item = QTreeWidgetItem([entry.code])

        item.setData(
            0,
            Qt.UserRole,
            entry.code
        )

        target.addChild(item)

        return item
    
    def add_seance(self, tree):

            parent = tree.currentItem()

            if parent is None:
                return None

            if parent.text(0) != "Séances":
                return None

            item = QTreeWidgetItem(["Nouvelle séance"])

            item.setFlags(
                item.flags() | Qt.ItemIsEditable
            )

            parent.addChild(item)

            tree.setCurrentItem(item)

            return item

    def tree_to_dict(self, item, depth=0):

        if depth == 2:
            return [
                item.child(i).text(0)
                for i in range(item.childCount())
            ]

        return {
            item.child(i).text(0):
            self.tree_to_dict(
                item.child(i),
                depth + 1
            )
            for i in range(item.childCount())
        }

    def snapshot(self, tree):

        data = {}

        for i in range(tree.topLevelItemCount()):

            root = tree.topLevelItem(i)

            data[root.text(0)] = self.tree_to_dict(root)

        return data

    def expanded_paths(self, tree):

        expanded = set()

        def walk(item, path):

            path = path + (item.text(0),)

            if item.isExpanded():
                expanded.add(path)

            for i in range(item.childCount()):
                walk(item.child(i), path)

        for i in range(tree.topLevelItemCount()):
            walk(
                tree.topLevelItem(i),
                ()
            )

        return expanded

    def restore_expanded(
        self,
        tree,
        expanded
    ):

        def walk(item, path):

            path = path + (item.text(0),)

            item.setExpanded(
                path in expanded
            )

            for i in range(item.childCount()):
                walk(item.child(i), path)

        for i in range(tree.topLevelItemCount()):
            walk(
                tree.topLevelItem(i),
                ()
            )
    def restore(self, tree, data):

        expanded = self.expanded_paths(tree)

        tree.clear()

        def build(parent, obj):

            for key, value in obj.items():

                item = QTreeWidgetItem([key])

                parent.addChild(item)

                if isinstance(value, dict):

                    build(item, value)

                elif isinstance(value, list):

                    for code in value:

                        child = QTreeWidgetItem([code])

                        child.setData(
                            0,
                            Qt.UserRole,
                            code
                        )

                        item.addChild(child)

        for key, value in data.items():

            root = QTreeWidgetItem([key])

            tree.addTopLevelItem(root)

            build(root, value)

        self.restore_expanded(
            tree,
            expanded
        )