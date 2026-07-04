from pathlib import Path


class ProgressionDocumentController:
    """
    Gère le document de progression courant.

    Cette classe ne connaît pas Qt.
    Elle ne fait que coordonner les services.
    """

    def __init__(
        self,
        progression_service,
        persistence_service,
        export_service,
        undo_redo_service,
        code_service,
        paths,
        current_file
    ):
        self.progression_service = progression_service
        self.persistence_service = persistence_service
        self.export_service = export_service
        self.undo_redo = undo_redo_service
        self.code_service = code_service
        self.paths = paths
        self.current_file = current_file

    @property
    def has_file(self):
        return self.current_file is not None

    def load(self, tree, filename):

        data = self.persistence_service.load_progression(filename)

        if data is None:
            return False
        
        self.progression_service.restore(
            tree,
            data
        )

        self.current_file = Path(filename)

        self.undo_redo.clear()

        return True

    def save(self, tree):

        if self.current_file is None:
            return False

        data = self.progression_service.snapshot(tree)

        self.persistence_service.save_progression(
            self.current_file,
            data
        )

        return True

    def save_as(self, tree, filename):

        data = self.progression_service.snapshot(tree)

        self.persistence_service.save_progression(
            filename,
            data
        )

        self.current_file = Path(filename)

        return True

    def export(
        self,
        tree,
        catalogue_name,
    ):

        if self.current_file is None:
            return None

        data = self.progression_service.snapshot(tree)

        tex_path = (
            self.paths.sequencages
            / f"sequencage-{catalogue_name.replace(' ', '_')}-{self.current_file.stem}-structure.tex"
        )

        self.export_service.export_progression(
            tex_path,
            data,
        )

        return tex_path