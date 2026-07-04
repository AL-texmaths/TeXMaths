import json
import sys
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict
from src.exe_pathes import resolve_executable, resolve_pathes

# =========================
# PLATFORM DETECTION
# =========================

IS_WINDOWS = sys.platform.startswith("win")

if IS_WINDOWS:
    import winreg
    import ctypes


# =========================
# PATHS
# =========================

def base_dir():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


RESOURCE_DIR = base_dir()

DATA_DIR = RESOURCE_DIR / "data"
SRC_DIR = RESOURCE_DIR / "src"
OUTPUT_DIR = RESOURCE_DIR / "output"
LATEX_DIR = DATA_DIR / "latex"
TMP_DIR = LATEX_DIR / "tmp"

if not TMP_DIR.exists():
    TMP_DIR.mkdir(parents=True, exist_ok=True)

CONFIG_PATH = base_dir() / "config.json"

def get_config():
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Config introuvable : {CONFIG_PATH}")

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        CONFIG = json.load(f)
    return CONFIG

def get_exe(exe_name):
    try:
        exe_candidates = get_config()['executables'][exe_name]
    except KeyError:
        print(f"Executable '{exe_name}' not found in config.")
        return None
    if not isinstance(exe_candidates, list):
        exe_candidates = [exe_candidates]
    return resolve_executable(*exe_candidates)

def get_path(path_name):
    try:
        path_candidates = get_config()['paths'][path_name]
    except KeyError:
        print(f"Path '{path_name}' not found in config.")
        return None
    return resolve_pathes(*path_candidates)

KATEX_DIR = get_path('katex')

# =========================
# WINDOWS ONLY: FILE VERSION
# =========================

def get_file_version(path: Path) -> Optional[str]:
    if not IS_WINDOWS:
        return None

    try:
        path_str = str(path)

        size = ctypes.windll.version.GetFileVersionInfoSizeW(path_str, None)
        if not size:
            return None

        buf = (ctypes.c_byte * size)()

        if not ctypes.windll.version.GetFileVersionInfoW(path_str, 0, size, buf):
            return None

        ver_ptr = ctypes.c_void_p()
        ver_len = ctypes.c_uint()

        if not ctypes.windll.version.VerQueryValueW(
            buf, "\\", ctypes.byref(ver_ptr), ctypes.byref(ver_len)
        ):
            return None

        class VS_FIXEDFILEINFO(ctypes.Structure):
            _fields_ = [
                ("dwSignature", ctypes.c_uint32),
                ("dwStrucVersion", ctypes.c_uint32),
                ("dwFileVersionMS", ctypes.c_uint32),
                ("dwFileVersionLS", ctypes.c_uint32),
                ("dwProductVersionMS", ctypes.c_uint32),
                ("dwProductVersionLS", ctypes.c_uint32),
                ("dwFileFlagsMask", ctypes.c_uint32),
                ("dwFileFlags", ctypes.c_uint32),
                ("dwFileOS", ctypes.c_uint32),
                ("dwFileType", ctypes.c_uint32),
                ("dwFileSubtype", ctypes.c_uint32),
                ("dwFileDateMS", ctypes.c_uint32),
                ("dwFileDateLS", ctypes.c_uint32),
            ]

        info = ctypes.cast(ver_ptr, ctypes.POINTER(VS_FIXEDFILEINFO)).contents
        ms = info.dwFileVersionMS
        ls = info.dwFileVersionLS

        return f"{ms >> 16}.{ms & 0xFFFF}.{ls >> 16}.{ls & 0xFFFF}"

    except Exception:
        return None


# =========================
# WINDOWS REGISTRY SEARCH
# =========================

def find_adobe_apps() -> Dict[str, Dict[str, Optional[str]]]:
    if not IS_WINDOWS:
        return {}

    exe_map = {
        "acrobat": "Acrobat.exe",
        "reader": "AcroRd32.exe"
    }

    REG_PATHS = [
        (winreg.HKEY_LOCAL_MACHINE,
         r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths"),
        (winreg.HKEY_LOCAL_MACHINE,
         r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths"),
        (winreg.HKEY_CURRENT_USER,
         r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths"),
    ]

    results: Dict[str, Dict[str, Optional[str]]] = {}

    for app, exe in exe_map.items():
        for root, base_path in REG_PATHS:
            try:
                with winreg.OpenKey(root, f"{base_path}\\{exe}") as key:
                    raw_path, _ = winreg.QueryValueEx(key, "")
                    path = Path(raw_path)

                    if path.exists():
                        results[app] = {
                            "path": str(path),
                            "version": get_file_version(path)
                        }
                        break
            except Exception:
                continue

    return results


def choose_pdf_app(require_edit: bool = False) -> Optional[str]:
    apps = find_adobe_apps()

    if require_edit and "acrobat" in apps:
        return apps["acrobat"]["path"]

    if "acrobat" in apps:
        return apps["acrobat"]["path"]

    if "reader" in apps:
        return apps["reader"]["path"]

    return None


# =========================
# GLOBAL APPS
# =========================

# ADOBE_PATH = choose_pdf_app(require_edit=True)
try:
    ADOBE_PATH = get_exe("adobe")
except FileNotFoundError:
    ADOBE_PATH = None

PDF_XCHANGE_PATH = None
try:
    PDF_XCHANGE_PATH = get_exe("pdf_xchange")
except FileNotFoundError:
    PDF_XCHANGE_PATH = None

if IS_WINDOWS and not ADOBE_PATH:
    print("Aucune application Adobe trouvée (Windows only check)")


# =========================
# MESSAGES
# =========================

MESSAGES = {
    "printer": "Printer index ? ",
    "nb_copy": "How many copies ? ",
    "print_settings": "Print settings ? ",
    "file": "File name ? ",
    "files": "Files name ? (</> separator) "
}


YEAR_DIR = OUTPUT_DIR / get_config()["settings"]["year"]
DEFAULT_DATA_LOG_DIR = DATA_DIR / "logs"


# =========================
# SAFE SUBPROCESS WRAPPER
# =========================

def compile_latex(tex_file_path: str | Path,
                  cwd:None | str | Path=None,
                  motor='lualatex',
                  cmd_args=None,
                  silent=True,
                  log=print,
                  **kwargs):
    
    if cmd_args is None:
        cmd_args = []

    tex_file_path = Path(tex_file_path)
    if cwd is not None:
        cwd = Path(cwd)
        tex_file_path = cwd / tex_file_path

    if silent:
        log = lambda *args, **kwargs: None

    if not tex_file_path.exists():
        return subprocess.CompletedProcess([], 1, "", f"File not found {tex_file_path}")

    if cwd is None:
        cwd = tex_file_path.parent
        tex_file_cmd_path = tex_file_path.name
    else:
        tex_file_cmd_path = tex_file_path

    try:
        exe_path = get_exe(motor)
    except FileNotFoundError:
        exe_path = 'lualatex'  # fallback to system path
    
    print(exe_path)

    if IS_WINDOWS and not str(exe_path).lower().endswith(".exe"):
        exe_path = exe_path.with_suffix(".exe")

        if not Path(exe_path).exists():
            return subprocess.CompletedProcess([], 2, "", f"Executable not found : {exe_path}")

    cmd_list = [str(exe_path)] + cmd_args + [str(tex_file_cmd_path)]
    if not silent:
        log(f"Running command: {' '.join(cmd_list)} in {cwd}")

    result = subprocess.run(
        cmd_list,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    return result


# =========================
# UTILITIES (UNCHANGED)
# =========================

def camel_to_sentence(s: str) -> str:
    s = s.replace('_', ' ').replace('-', ' ')
    s = re.sub(r'(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])', ' ', s)
    return s[0].upper() + s[1:] if s else s


def getmodtime(fichier_path):
    return datetime.fromtimestamp(Path(fichier_path).stat().st_mtime)


def show(message, sep='=', sup=2):
    n = max(map(len, message.split('\n'))) + sup
    print(sep * n)
    print(message)
    print(sep * n)


def get_pattern(doc_type, extension=None):
    DOC_DICT = get_config()["settings"]["index documents"][doc_type]
    if extension is None:
        return DOC_DICT['name pattern']
    return doc_type + DOC_DICT['name pattern'].replace('([A-Za-z\\.]+)$', f'{extension}$')

def del_files_by_ext(dirpath, extensions):
    """
    Supprime les fichiers avec des extensions spécifiées dans le répertoire `dirpath`.

    :param dirpath: Le chemin du répertoire où les fichiers seront supprimés.
    :param extensions: Liste des extensions des fichiers à supprimer (ex. ['.txt', '.log']).
    """
    # Vérifier si le répertoire existe
    if not dirpath.exists():
        print(f"Le répertoire {dirpath} n'existe pas.")
        return

    # Parcours du répertoire
    for filename in dirpath.iterdir():
        # Construire le chemin complet du fichier
        file_path = dirpath /filename
        # Vérifier si c'est un fichier et si son extension correspond à celles spécifiées
        if file_path.is_file() and any(filename.suffix == ext for ext in extensions):
            try:
                file_path.unlink()
                print(f"Fichier supprimé : {file_path}")
            except Exception as e:
                print(f"Erreur lors de la suppression de {file_path}: {e}")

def get_last_run_date(script_path):
    """
    Function : return the last execution date of the
    script
    """
    if type(script_path) == str:
        script_path = Path(script_path)
    log_filename = script_path.with_suffix('.log').name
    log_file_path = DATA_DIR / "logs" / log_filename
    if log_file_path.exists():
        with open(log_file_path, "r", encoding="utf-8") as log_file:
            last_run_time_str = log_file.read().strip()
            return datetime.strptime(last_run_time_str, "%Y-%m-%d %H:%M:%S")
    else:
        return datetime.now()

def update_last_run_date(script_path):
    """
    Function : update the last execution date of the script
    """
    if type(script_path) == str:
        script_path = Path(script_path)
    log_filename = script_path.with_suffix('.log').name
    current_run_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file_path = DATA_DIR / "logs" / log_filename
    with open(log_file_path, "w", encoding="utf-8") as log_file:
        print("Updating last run date | {} | {}".format(script_path.name, current_run_date))
        log_file.write(current_run_date)

def chapter_dirname(level, chapter_key):
    """
    """
    return next((YEAR_DIR / level).glob(chapter_key+'*'))

def get_cours_file_path(file_name_input:str):
    """
    """
    file_name_input = file_name_input.replace(' ', '-')
    chapter_path = chapter_dirname(*file_name_input.split('-')[:2]) 
    return chapter_path / f'{file_name_input}.pdf'

# =========================
# WINDOWS TEST TOOL
# =========================

def test_executable(executable):
    if IS_WINDOWS:
        result = subprocess.run(["where", executable],
                                 capture_output=True, text=True)
        return result.returncode == 0
    else:
        result = subprocess.run(["which", executable],
                                 capture_output=True, text=True)
        return result.returncode == 0


# =========================
if __name__ == '__main__':
    print(f"module {__file__} ok")