# undo_redo_service.py
import copy

def record_tree_undo(method):
    def wrapper(self, tree, *args, **kwargs):
        self.undo_redo.record(self.progression_service.snapshot(tree))
        return method(self, tree, *args, **kwargs)
    return wrapper

class UndoRedoService:
    def __init__(self):
        self.undo_stack = []
        self.redo_stack = []

    def record(self, state):
        self.undo_stack.append(copy.deepcopy(state))
        self.redo_stack.clear()
        # debug
        print("record")
        print(len(self.undo_stack), len(self.redo_stack))

    def can_undo(self):
        return bool(self.undo_stack)

    def can_redo(self):
        return bool(self.redo_stack)

    def undo(self, current_state):
        # debug
        print("undo before", len(self.undo_stack), len(self.redo_stack))
        if not self.undo_stack:
            return None

        self.redo_stack.append(copy.deepcopy(current_state))
        state = self.undo_stack.pop()
        # debug
        print("undo after", len(self.undo_stack), len(self.redo_stack))
        return state

    def redo(self, current_state):
        # debug
        print("redo before", len(self.undo_stack), len(self.redo_stack))
        if not self.redo_stack:
            return None

        self.undo_stack.append(copy.deepcopy(current_state))
        state = self.redo_stack.pop()
        # debug
        print("redo", len(self.undo_stack), len(self.redo_stack))
        return state

    def clear(self):
        self.undo_stack.clear()
        self.redo_stack.clear()