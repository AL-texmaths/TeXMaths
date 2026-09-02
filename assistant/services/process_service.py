import subprocess
from pathlib import Path


class ProcessService:
    """Service pour ouvrir des fichiers avec des applications externes"""

    @staticmethod
    def open_with(executable_path, file_path, *args, place_file_last=True):
        """
        Ouvre un fichier avec une application externe
        
        Args:
            executable_path: Chemin de l'exécutable
            file_path: Chemin du fichier à ouvrir
            *args: Arguments supplémentaires à passer à l'exécutable
        """
        try:
            executable_path = str(executable_path)
            file_path = str(file_path)

            # Allow callers to request that the file path be placed after the
            # additional arguments. Some PDF viewers (eg. PDF XChange) expect
            # arguments like `/A "page=1"` before the file name.
            if place_file_last:
                cmd = [executable_path, file_path] + list(args)
            else:
                cmd = [executable_path] + list(args) + [file_path]

            subprocess.Popen(cmd, cwd=str(Path(file_path).parent))
                
        except Exception as e:
            raise OSError(f"Erreur lors de l'ouverture du fichier: {e}")
