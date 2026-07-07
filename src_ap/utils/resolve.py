import sys
import json
import shutil
from pathlib import Path

from src_ap.models.config import Config

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

CONFIG_PATH = (Path("src_ap") / "config.json").absolute()

def get_config() -> dict:
    """
    Load the configuration from the config.json file.

    Returns:
        A dictionary containing the configuration.
    """
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

CONFIG = get_config()


def resolve_executable(executable: str, config:Config|None=None) -> Path:
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
    if config is not None:
        executables = config.executables.get(executable)
    else:
        executables = None
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

    if executables is None:
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

def resolve_path(candidates: Path | str | list[str], config:Config|None=None) -> Path:
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

    if config is not None and isinstance(candidates, str):
        return resolve_path(config.paths_candidates.get(candidates))

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
