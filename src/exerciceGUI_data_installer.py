import sys
import shutil
from pathlib import Path
from src.tools import LATEX_DIR, CONFIG_PATH

DISTPATH = sys.argv[1]

DirToCopy = [
    "activites",
    "catalogues",
    "codes_cnscmpsrc",
    "diapo",
    "exercices",
    "flash",
    "flash\\previews"
    ]

FilesToCopy = [
    "config.json"
]
NewLaTeXDir = Path(DISTPATH) / "exerciceGUI" / "data" / "latex"

for dir_to_copy in DirToCopy:
    src_dir = LATEX_DIR / Path(dir_to_copy)
    dst_dir = NewLaTeXDir / Path(dir_to_copy)
    if not dst_dir.exists():
        dst_dir.mkdir(parents=True)
    for src_file_path in src_dir.iterdir():
        if src_file_path.suffix in ['.tex', '.pdf', '.log', '.json']:
            dst_file_path = dst_dir / src_file_path.name
            if not dst_file_path.exists():
                print(f'Copying {src_file_path} to {dst_file_path}')
                shutil.copy(src_file_path, dst_file_path)

shutil.copy(CONFIG_PATH, Path(DISTPATH) / "exerciceGUI")