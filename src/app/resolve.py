from __future__ import annotations

import os
import sys
import shutil
from pathlib import Path


def resolve_executable(*candidates: str) -> str | None:
    """
    Recherche le premier exécutable valide parmi les candidats fournis.

    Exemples:
        resolve_executable("python")
        resolve_executable(
            "python",
            "/usr/bin/python3.12",
            r".\\Root\\Programmes\\Python\\python.exe"
        )

    Retourne:
        Le chemin absolu de l'exécutable trouvé, sinon None.
    """

    search_bases = []

    # Répertoire du script ou de l'exécutable PyInstaller
    if getattr(sys, "frozen", False):
        search_bases.append(Path(sys.executable).parent)
    else:
        search_bases.append(Path(__file__).resolve().parent)

    # Répertoire courant
    search_bases.append(Path.cwd())

    # Supprime les doublons tout en conservant l'ordre
    search_bases = list(dict.fromkeys(search_bases))

    for candidate in candidates:
        if not candidate:
            continue

        candidate = os.path.expandvars(os.path.expanduser(candidate))

        # 1. Recherche dans le PATH
        found = shutil.which(candidate)
        if found:
            return str(Path(found).resolve())

        p = Path(candidate)

        # 2. Chemin absolu
        if p.is_absolute():
            if p.is_file() and os.access(p, os.X_OK):
                return str(p.resolve())
            continue

        # 3. Chemins relatifs
        for base in search_bases:
            full = (base / p).resolve()

            if full.is_file() and os.access(full, os.X_OK):
                return str(full)

            # Cas Windows : ajout automatique de PATHEXT
            if os.name == "nt" and full.suffix == "":
                for ext in os.environ.get("PATHEXT", ".EXE;.BAT;.CMD;.COM").split(";"):
                    test = full.with_suffix(ext.lower())

                    if test.is_file():
                        return str(test.resolve())

    return None

def resolve_paths(*candidates: str) -> Path | None:
    """
    Retourne le premier chemin existant trouvé parmi les candidats.

    Recherche :
    - chemins absolus ;
    - chemins relatifs au script ;
    - chemins relatifs à l'exécutable PyInstaller ;
    - chemins relatifs à sys._MEIPASS ;
    - chemins relatifs au répertoire courant.

    Exemple :
        resolve_paths(
            "config.json",
            "./data",
            "/etc/myapp/config.json"
        )

    Retourne :
        Path : chemin absolu trouvé
        None : aucun chemin trouvé
    """

    search_bases: list[Path] = []

    # Répertoire du script ou de l'exécutable PyInstaller
    if getattr(sys, "frozen", False):
        search_bases.append(Path(sys.executable).resolve().parent)
    else:
        search_bases.append(Path(__file__).resolve().parent)

    # Répertoire temporaire PyInstaller (--onefile)
    if hasattr(sys, "_MEIPASS"):
        search_bases.append(Path(sys._MEIPASS))

    # Répertoire courant
    search_bases.append(Path.cwd())

    # Suppression des doublons en conservant l'ordre
    search_bases = list(dict.fromkeys(search_bases))

    for candidate in candidates:
        if not candidate:
            continue

        p = Path(os.path.expandvars(os.path.expanduser(candidate)))

        # Chemin absolu
        if p.is_absolute():
            if p.exists():
                return p.resolve()
            continue

        # Chemin relatif
        for base in search_bases:
            full = (base / p).resolve()

            if full.exists():
                return full

    return None