from __future__ import annotations

import sys
import shutil
import json
import subprocess
from pathlib import Path

def get_config() -> dict:
    """
    Load the configuration from the config.json file.

    Returns:
        A dictionary containing the configuration.
    """
    config_path = Path("assistant_progression") / "config.json"

    with open(config_path, "r", encoding="utf-8") as f:
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

def compile_latex(
    tex_file: str | Path,
    args: list[str] = [
        "-interaction=nonstopmode",
        "-file-line-error",
        ],
    motor: str = "latexmk"
    ):
    """
    Compile a LaTeX file using the specified engine and arguments.
    """
    tex_file = Path(tex_file)
    if not tex_file.exists():
        raise FileNotFoundError(f"The specified LaTeX file does not exist: {tex_file}")

    try:
        executable_path = resolve_executable(motor)
    except KeyError:
        raise ValueError(f"No executable configuration found for motor: {motor}")
    
    cmd = [str(executable_path), *args, str(tex_file)]
    print(f"Running command: {' '.join(cmd)}")

    print("motor =", motor)
    print("executable_path =", executable_path)
    print("cmd =", cmd)

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
    )

    print("Command    :", result.args)
    print("Return code:", result.returncode)
    print("STDOUT:")
    print(result.stdout)
    print("STDERR:")
    print(result.stderr)

print(resolve_path("cycle 4 BO 2026"))
