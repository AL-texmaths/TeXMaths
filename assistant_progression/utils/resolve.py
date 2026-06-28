import sys
import json
import shutil
from pathlib import Path

def check_project_layout(Base_dir: Path):

    REQUIRED_FILES = [
    Base_dir / "config.json",
    ]

    DATA_DIR = Base_dir / "data"

    REQUIRED_DIRS = [
        DATA_DIR / "latex" / "catalogues",
        DATA_DIR / "katex",
        DATA_DIR / "progressions",
        DATA_DIR / "texmf",
        DATA_DIR / "latex" / "codes_labels",
        DATA_DIR / "latex" / "sequencages",
    ]

    missing = []

    for f in REQUIRED_FILES:
        if not f.exists():
            missing.append(f)

    for d in REQUIRED_DIRS:
        if not d.exists():
            missing.append(d)

    if missing:
        raise RuntimeError(
            "Missing required project files:\n" +
            "\n".join(str(m) for m in missing)
        )

CONFIG_PATH = (Path("assistant_progression") / "config.json").absolute()

def get_config() -> dict:
    """
    Load the configuration from the config.json file.

    Returns:
        A dictionary containing the configuration.
    """
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

CONFIG = get_config()


def resolve_executable(executable: str) -> Path:
    """
    Resolve the first available executable.

    Search order:
    1. Next to the application bundle (PyInstaller support).
    2. In the current executable directory.
    3. In the system PATH.

    Args:
        executable: Name of the executable to resolve.

    Returns:
        Absolute path to the resolved executable.

    Raises:
        FileNotFoundError: If no executable could be found.
        ValueError: If the executable list is empty.
    """
    config = get_config()
    executables = config.get("executables", {}).get(executable, [])
    #1. Search in PATH
    resolved = shutil.which(executable)
    if resolved:
        return Path(resolved).absolute()
    # Future-proof PyInstaller support
    candidates_dirs: list[Path] = []
    if getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            candidates_dirs.append(Path(meipass))

        candidates_dirs.append(Path(sys.executable).parent)

    # Search near the current script/module
    try:
        candidates_dirs.append(Path(__file__).absolute().parent)
    except NameError:
        pass

    # 1. Search in local candidate directories
    for executable in executables:
        for directory in candidates_dirs:
            candidate = directory / executable
            if candidate.is_file():
                return candidate.absolute()

    # 2. Search in PATH
    for executable in executables:
        resolved = shutil.which(executable)
        if resolved:
            return Path(resolved).absolute()
    
    raise FileNotFoundError(
        f"Could not resolve any executable from: {', '.join(executables)}"
    )

def resolve_path(candidates: Path | str | list[str], config=True) -> Path:
    """
    Resolve the first existing path among the candidates.

    Search order:
    1. Absolute path as-is.
    2. Relative to current working directory.
    3. Relative to this module directory.
    4. Relative to PyInstaller executable directory.
    5. Relative to PyInstaller _MEIPASS directory.

    Args:
        candidates: Candidate paths ordered by preference.

    Returns:
        Absolute resolved path.

    Raises:
        ValueError: If candidates is empty.
        FileNotFoundError: If no candidate can be resolved.
    """
    if not candidates:
        raise ValueError("candidates must not be empty")

    if config and isinstance(candidates, str):
        return resolve_path(CONFIG.get("paths").get(candidates), config=False)

    if isinstance(candidates, (str, Path)):
        candidates = [Path(candidates)]

    search_roots: list[Path] = [
        Path.cwd(),
    ]

    try:
        search_roots.append(Path(__file__).resolve().parent)
    except NameError:
        pass

    if getattr(sys, "frozen", False):
        search_roots.append(Path(sys.executable).parent)

        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            search_roots.append(Path(meipass))

    for candidate in candidates:
        path = Path(candidate)

        # Absolute path
        if path.is_absolute():
            if path.exists():
                return path.resolve()
            continue

        # Relative path
        for root in search_roots:
            resolved = root / path
            if resolved.exists():
                return resolved.resolve()

    raise FileNotFoundError(
        "Could not resolve any path from: "
        + ", ".join(map(str, candidates))
    )

try:
    KATEX_DIR = resolve_path('katex')
except FileNotFoundError:
    print("Warning: KaTeX directory not found. Mathematical expressions may not render correctly.")
    KATEX_DIR = Path()

try:
    CODE_INDEX_DIR = resolve_path('code index')
except FileNotFoundError:
    print("Warning: Code index directory not found. No datas imported.")
    CODE_INDEX_DIR = Path()

CODE_INDEX_FILE_PATH = CODE_INDEX_DIR / "code_index.json"

if not CODE_INDEX_FILE_PATH.exists():
    print(f"Warning: Code index file not found at {CODE_INDEX_FILE_PATH}.")
    CODE_INDEX_FILE_PATH = Path()

try:
    DEFAULT_PROG_DIR = resolve_path('progression import path')
except FileNotFoundError:
    print("Warning: Progression import directory not found.")
    DEFAULT_PROG_DIR = Path()

try:
    PROGRESSION_EXPORT_DIR = resolve_path('progression export path')
except FileNotFoundError:
    print("Warning: Progression export directory not found. Exporting progressions may not work.")
    PROGRESSION_EXPORT_DIR = Path().cwd()

try:
    CODE_LABELS_DIR = resolve_path('code labels')
except FileNotFoundError:
    print("Warning: Code labels directory not found. Updating catalogue may not work.")
    CODE_LABELS_DIR = Path()

try:
    TEX_PACKAGES_DIR = resolve_path('texmf')
except FileNotFoundError:
    print("Warning: tex tree 'texmf' directory not found.")
    TEX_PACKAGES_DIR = Path()

if TEX_PACKAGES_DIR.exists():
    TEX_PACKAGES_DIR = TEX_PACKAGES_DIR / "tex" / "latex"
    if not TEX_PACKAGES_DIR.exists():
        print("Warning: texmf directory must contain a 'tex/latex' subdirectory.")