# progression_controller.py
from src_ap.services.undo_redo_service import record_tree_undo


class ProgressionController:
    def __init__(self, progression_service, undo_redo_service):
        self.progression_service = progression_service
        self.undo_redo = undo_redo_service
    
    def snapshot(self, tree):
        return self.progression_service.snapshot(tree)

    def undo(self, tree, refresh_callback=None):
        # conserver l'état d'expansion actuel pour le réappliquer
        expanded = self.progression_service.get_expanded_paths(tree)

        state = self.undo_redo.undo(self.snapshot(tree))
        if state is None:
            return

        self.progression_service.restore(tree, state)

        # réappliquer l'expansion précédente (ne déplie que les chemins connus)
        self.progression_service.apply_expanded_paths(tree, expanded)

        if refresh_callback:
            refresh_callback()
    
    def redo(self, tree, refresh_callback=None):
        expanded = self.progression_service.get_expanded_paths(tree)

        state = self.undo_redo.redo(self.snapshot(tree))
        if state is None:
            return

        self.progression_service.restore(tree, state)

        self.progression_service.apply_expanded_paths(tree, expanded)

        if refresh_callback:
            refresh_callback()
    
    @record_tree_undo
    def add_custom_item(self, tree, text, refresh_callback=None):
        item = self.progression_service.add_custom_item(tree)

        if item:
            tree.editItem(item, 0)

        if refresh_callback:
            refresh_callback()

    @record_tree_undo
    def add_level(self, tree, refresh_callback=None):
        item = self.progression_service.add_level(tree)

        if item:
            tree.editItem(item, 0)

        if refresh_callback:
            refresh_callback()

    @record_tree_undo
    def add_chapter(self, tree, catalogue, current_item, refresh_callback=None):
        item = self.progression_service.add_chapter(tree, catalogue, current_item)

        if item:
            tree.editItem(item, 0)

        if refresh_callback:
            refresh_callback()
    
    @record_tree_undo
    def add_seance(self, tree, refresh_callback=None):
        item = self.progression_service.add_seance(tree)

        if item:
            tree.editItem(item, 0)

        if refresh_callback:
            refresh_callback()
    
    @record_tree_undo
    def add_selected_item(
        self,
        tree,
        entry,
        on_warning=None,
        on_success=None,
        refresh_callback=None
    ):
        item = self.progression_service.add_selected_item(tree, entry)

        if item is None:
            if on_warning:
                on_warning("Please select a chapter to add the item.")
            return

        if on_success:
            on_success(f"Item {entry.code} added to the progression.")

        if refresh_callback:
            refresh_callback()
    
    @record_tree_undo
    def delete_item(self, tree, refresh_callback=None):
        self.progression_service.delete_item(tree)

        if refresh_callback:
            refresh_callback()

    def copy_item(self, tree, refresh_callback=None):
        self.progression_service.copy_item(tree)
        if refresh_callback:
            refresh_callback()

    @record_tree_undo
    def cut_item(self, tree, refresh_callback=None):
        self.progression_service.cut_item(tree)
        if refresh_callback:
            refresh_callback()

    @record_tree_undo
    def paste_item(self, tree, refresh_callback=None):
        self.progression_service.paste_item(tree)
        if refresh_callback:
            refresh_callback()
    
    @record_tree_undo
    def move_item(self, tree, delta, refresh_callback=None):
        self.progression_service.move_item(tree, delta)

        if refresh_callback:
            refresh_callback()
    
    def move_item_up(self, tree, refresh_callback=None):
        self.move_item(tree, -1, refresh_callback)
    
    def move_item_down(self, tree, refresh_callback=None):
        self.move_item(tree, 1, refresh_callback)