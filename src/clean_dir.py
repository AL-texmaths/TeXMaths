import sys
from pathlib import Path
from src.tools import TMP_DIR

directory = Path(sys.argv[1])

if not directory.exists() or not directory.is_dir():
    print(f"Le répertoire {directory} n'existe pas ou n'est pas un répertoire.")
    sys.exit(1)

# Déplacer le contenu du répertoires exemples vers la corbeille
for file_path in directory.glob('*'):
    tmp_path = TMP_DIR / file_path.name
    if tmp_path.exists():
        tmp_path.unlink()
    file_path.rename(tmp_path)
    print(f"Déplacé {file_path} vers {tmp_path}")