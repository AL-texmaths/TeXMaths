import subprocess
import sys
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
            
            if sys.platform.startswith("win"):
                subprocess.Popen(cmd)
            else:
                subprocess.Popen(cmd)
                
        except Exception as e:
            raise OSError(f"Erreur lors de l'ouverture du fichier: {e}")
