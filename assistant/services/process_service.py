import subprocess
from pathlib import Path


class ProcessService:
    """Service pour ouvrir des fichiers avec des applications externes"""

    @staticmethod
    def open_with(executable_path, file_path, *args):
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
            
            cmd = [executable_path, file_path] + list(args)
            
            subprocess.Popen(cmd, cwd=str(Path(file_path).parent))
                
        except Exception as e:
            raise OSError(f"Erreur lors de l'ouverture du fichier: {e}")
