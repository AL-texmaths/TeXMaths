from PySide6.QtWidgets import QTreeWidgetItem
from PySide6.QtCore import Qt


class ProgressionService:

    def __init__(self, code_service, analysis_service, config):
        self.code_service = code_service
        self.analysis_service = analysis_service
        self.config = config

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

        for code in selected_catalogue.get("childs"):

            item.addChild(
                QTreeWidgetItem([
                    self.code_service.code_label(code)
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

    def can_add_level(self, tree):
        return True

    def can_add_chapter(self, tree, selected_catalogue):

        if not selected_catalogue:
            return False

        if tree.topLevelItemCount() == 0:
            return False

        return True

    def can_add_seance(self, tree):
        chapter = self.get_selected_chapter(tree)
        if chapter is None:
            return False

        for i in range(chapter.childCount()):
            if chapter.child(i).text(0) == "Séances":
                return True

        return False

    def get_selected_chapter(self, tree):
        item = tree.currentItem()
        if item is None:
            return None

        # remonter jusqu'au niveau 1 (chapitre)
        while item.parent() is not None and item.parent().parent() is not None:
            item = item.parent()

        # vérifier que c'est bien un chapitre (niveau 1)
        if item.parent() is None:
            return None

        return item

    def add_selected_item(self, tree, entry):

        chapter = self.get_selected_chapter(tree)
        if chapter is None:
            return None

        target_label = self.code_service.code_label(entry.type)

        target = None

        for i in range(chapter.childCount()):
            child = chapter.child(i)

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

        item.setToolTip(
            0,
            f"Catalogue: {self.code_service.display_name(entry.catalogue)}\n"
            f"{entry.text}\n"
        )

        target.addChild(item)

        # expand proprement tout le chemin
        parent = item.parent()
        while parent is not None:
            parent.setExpanded(True)
            parent = parent.parent()

        tree.setCurrentItem(item)
        tree.scrollToItem(item)

        return item

    def add_seance(self, tree):

        chapter = self.get_selected_chapter(tree)
        if chapter is None:
            return None

        # chercher le noeud "Séances"
        target = None

        for i in range(chapter.childCount()):
            child = chapter.child(i)
            if child.text(0) == "Séances":
                target = child
                break

        if target is None:
            return None

        item = QTreeWidgetItem(["Nouvelle séance"])
        item.setFlags(item.flags() | Qt.ItemIsEditable)

        target.addChild(item)

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
                        entry = self.code_service.get_entry_by_code(code)

                        if entry is not None:

                            child.setToolTip(
                                0,
                                entry.text
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