# progression_service.py
from PySide6.QtWidgets import QTreeWidgetItem
from PySide6.QtCore import Qt


from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem


def dump_tree(tree: QTreeWidget, show_user_role=False):
    """Affiche le contenu d'un QTreeWidget."""

    def dump_item(item: QTreeWidgetItem, prefix="", last=True):
        branch = "└── " if last else "├── "
        line = []

        for col in range(tree.columnCount()):
            text = item.text(col)
            if show_user_role:
                data = item.data(col, Qt.ItemDataRole.UserRole)
                line.append(f"{text!r} [{data!r}]")
            else:
                line.append(repr(text))

        child_prefix = prefix + ("    " if last else "│   ")
        for i in range(item.childCount()):
            dump_item(
                item.child(i),
                child_prefix,
                i == item.childCount() - 1
            )

    for i in range(tree.topLevelItemCount()):
        dump_item(
            tree.topLevelItem(i),
            last=(i == tree.topLevelItemCount() - 1)
        )


class ProgressionService:

    def __init__(self, code_service, catalogue_service, analysis_service, config):
        self.code_service = code_service
        self.catalogue_service = catalogue_service
        self.analysis_service = analysis_service
        self.config = config
        self._clipboard = None

    def make_item(self, text, data=None):
        item = QTreeWidgetItem([text])
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
        item.setData(0, Qt.UserRole, data)
        return item

    def add_level(self, tree):
        item = self.make_item("Nouveau niveau")
        tree.addTopLevelItem(item)
        tree.setCurrentItem(item)
        return item

    def add_custom_item(self, tree):
        current_item = tree.currentItem()
        if current_item is None:
            return None

        item = self.make_item("Nouvel élément")
        if current_item.text(0) == "Prérequis":
            item.setData(0, Qt.UserRole, "prerequis")
        elif current_item.text(0) == "Séances":
            item.setData(0, Qt.UserRole, "seance")
        current_item.addChild(item)
        current_item.setExpanded(True)
        tree.setCurrentItem(item)
        return item

    def add_chapter(self, tree, selected_catalogue, current_item):

        if current_item is None:
            return None

        if current_item.parent() is not None:
            current_item = current_item.parent()

        item = self.make_item("Nouveau chapitre")

        for code in selected_catalogue.types:

            item.addChild(
                self.make_item(self.code_service.display_name(code))
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

    def clone_item(self, item):
        new_item = QTreeWidgetItem([item.text(i) for i in range(item.columnCount())])
        new_item.setFlags(item.flags())
        for col in range(item.columnCount()):
            new_item.setData(col, Qt.UserRole, item.data(col, Qt.UserRole))
            new_item.setToolTip(col, item.toolTip(col))
        
        for i in range(item.childCount()):
            new_item.addChild(self.clone_item(item.child(i)))
        return new_item

    def copy_item(self, tree):
        item = tree.currentItem()
        if item:
            self._clipboard = self.clone_item(item)

    def cut_item(self, tree):
        item = tree.currentItem()
        if item:
            self._clipboard = self.clone_item(item)
            self.delete_item(tree)

    def paste_item(self, tree):
        if not self._clipboard:
            return None
        
        current_item = tree.currentItem()
        new_item = self.clone_item(self._clipboard)
        
        if current_item:
            current_item.addChild(new_item)
            current_item.setExpanded(True)
        else:
            tree.addTopLevelItem(new_item)
        
        tree.setCurrentItem(new_item)
        return new_item

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
    
    def can_add_item(self, tree):
        return self.get_selected_chapter(tree) is not None

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

        target_label = self.code_service.display_name(entry.type)

        target = None

        for i in range(chapter.childCount()):
            child = chapter.child(i)

            if child.text(0) == target_label:
                target = child
                break

        if target is None:
            return None

        item = self.make_item(entry.code, data=entry.id)

        item.setToolTip(
            0,
            f"Catalogue: {entry.catalogue.name}\n"
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

        item = self.make_item("Nouvelle séance", "seance")
        target.addChild(item)

        tree.setCurrentItem(item)

        return item

    def item_to_dict(self, item):
        return {
            "text": item.text(0),
            "data": item.data(0, Qt.UserRole),
            "tooltip": item.toolTip(0),
            "expanded": item.isExpanded(),
            "children": [
                self.item_to_dict(item.child(i))
                for i in range(item.childCount())
            ],
        }
    
    def dict_to_item(self, node):

        item = self.make_item(
            node["text"],
            node.get("data")
        )

        item.setToolTip(
            0,
            node.get("tooltip", "")
        )

        item.setExpanded(
            node.get("expanded", False)
        )

        for child in node.get("children", []):
            item.addChild(
                self.dict_to_item(child)
            )

        return item
    
    def snapshot(self, tree):

        return [
            self.item_to_dict(tree.topLevelItem(i))
            for i in range(tree.topLevelItemCount())
        ]
    
    def restore(self, tree, data):
        
        tree.clear()

        for node in data:
            tree.addTopLevelItem(
                self.dict_to_item(node)
            )
    
    def _collect_expanded_paths(self, item, prefix, out):
        path = prefix + (item.text(0),)
        if item.isExpanded():
            out.add(path)

        for i in range(item.childCount()):
            self._collect_expanded_paths(item.child(i), path, out)

    def get_expanded_paths(self, tree):
        """Retourne un set de tuples représentant les chemins (texte par niveau)
        des éléments actuellement dépliés dans l'arbre.
        """
        out = set()
        for i in range(tree.topLevelItemCount()):
            self._collect_expanded_paths(tree.topLevelItem(i), tuple(), out)
        return out

    def _apply_expanded_paths(self, item, prefix, paths):
        path = prefix + (item.text(0),)
        if path in paths:
            item.setExpanded(True)

        for i in range(item.childCount()):
            self._apply_expanded_paths(item.child(i), path, paths)

    def apply_expanded_paths(self, tree, paths):
        """Applique l'expansion pour tous les chemins présents dans `paths`.
        Ne modifie que les éléments à déplier (ne replie pas explicitement les autres).
        """
        if not paths:
            return

        for i in range(tree.topLevelItemCount()):
            self._apply_expanded_paths(tree.topLevelItem(i), tuple(), paths)