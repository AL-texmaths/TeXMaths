from shutil import which
from pathlib import Path

def resolve_executable(*candidates):
    """
    Résout le chemin d'un exécutable à partir d'une liste de candidats.
    Cherche d'abord dans le PATH, puis vérifie si le chemin existe.
    Args:
        candidates (list): Liste de chemins ou noms d'exécutables à tester.
    Returns:
        Path: Le chemin de l'exécutable trouvé.
    """
    for exe in candidates:
        # Cherche dans le PATH
        found = which(exe)
        if found:
            return Path(found)

        # Vérifie si c'est un chemin existant
        if Path(exe).exists():
            return Path(exe)

    raise FileNotFoundError(f"Aucun exécutable trouvé parmi {candidates}")

def resolve_pathes(*candidates):
    """
    Résout le chemin d'un fichier ou d'un répertoire à partir d'une liste de candidats.
    Args:
        candidates (list): Liste de chemins à tester.
    Returns:
        Path: Le chemin trouvé.
    """
    for path in candidates:
        if Path(path).exists():
            return Path(path)

    raise FileNotFoundError(f"Aucun chemin trouvé parmi {candidates}")