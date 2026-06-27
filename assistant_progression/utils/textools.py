from __future__ import annotations

import json
import subprocess
from pathlib import Path

from assistant_progression.utils.resolve import resolve_executable, resolve_path, get_config

CONFIG = get_config()
TEX_PACKAGES_DIR = resolve_path('texmf') / "tex" / "latex" / "packages"

def compile_latex(
    tex_file: str | Path,
    args: list[str] = [
        "-interaction=nonstopmode",
        "-file-line-error",
        "-lualatex",
        "-shell-escape",
        ],
    motor: str = "latexmk",
    outputdir: str | Path | None = None,
    ):
    """
    Compile a LaTeX file using the specified engine and arguments.
    """
    if outputdir is None:
        outputdir = tex_file.parent
        tex_file = Path(tex_file)
    else:
        outputdir = Path(outputdir)
        tex_file = outputdir / Path(tex_file)
    if not tex_file.exists():
        raise FileNotFoundError(f"The specified LaTeX file does not exist: {tex_file}")

    try:
        executable_path = resolve_executable(motor)
    except KeyError:
        raise ValueError(f"No executable configuration found for motor: {motor}")

    cmd = [str(executable_path), *args, f"-output-directory={outputdir}", str(tex_file)]
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

    return result

def check_code_index_data():
    #1 - Se placer dans data/latex/codes_labels
    #2- pour chaque fichier tex, vérifier s'il existe un fichier data.txt correspondant
    #3- si le fichier data.txt n'existe pas, compiler le fichier tex correspondant
    #4 si le fichier data existe mais est plus ancien que le fichier tex, recompiler le fichier tex correspondant
    #5 si les packages sont plus anciens recompiler
    cwd = resolve_path("code labels")
    for tex_file in cwd.glob("*.tex"):
        compile = False
        data_path = tex_file.with_name(tex_file.stem + "-data.txt")
        if not data_path.exists():
            print(f"File {data_path} does not exist. Compiling {tex_file}.")
            compile = True
        elif data_path.stat().st_mtime < tex_file.stat().st_mtime:
            print(f"File {data_path} is older than {tex_file}. Recompiling.")
            compile = True
        elif CONFIG["packages to check"].get(tex_file.name) is not None:
            packages = CONFIG["packages to check"][tex_file.name]
            for package in packages:
                package_path = TEX_PACKAGES_DIR / package
                if data_path.stat().st_mtime < package_path.stat().st_mtime:
                    print(f"File {data_path} is older than package {package_path}. Recompiling.")
                    compile = True
                    break

        if compile:
            result = compile_latex(tex_file)
            if result.returncode != 0:
                print(f"Compilation of {tex_file} failed. Please check the LaTeX file.")
                continue

def insert_nested(d, codes_values):
    *keys, value = codes_values

    current = d
    for key in keys[:-1]:
        current = current.setdefault(key, {})

    current[keys[-1]] = value

def update_code_index():
    #5- extraire les données du fichier data.txt dans un dict puis ecrire le dict dans un fichier json
    check_code_index_data()
    cwd = resolve_path("code labels")
    code_index_parent = resolve_path("code index")

    code_index_data = {}
    for data_file in cwd.glob("*-data.txt"):
        with open(data_file, "r", encoding="utf-8") as f:
            for line in f:
                codes_values = line.strip().split('|:|')
                insert_nested(code_index_data, codes_values)

    code_index_file = code_index_parent / "code_index.json"
    with open(code_index_file, "w", encoding="utf-8") as f:
            json.dump(code_index_data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    # Example usage
    update_code_index()