from __future__ import annotations

import json
import subprocess
from pathlib import Path

from assistant_progression.utils.resolve import (
    resolve_executable,
    CODE_LABELS_DIR,
    CODE_INDEX_DIR,
    TEX_PACKAGES_DIR,
    CONFIG
    )

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
    logger=print
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
    logger(f"Running command: {' '.join(cmd)}")

    logger(f"motor = {motor}")
    logger(f"executable_path = {executable_path}")
    logger(f"cmd = {cmd}")

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
    )

    logger(f"Command    : {result.args}")
    logger(f"Return code: {result.returncode}")
    logger("STDOUT:")
    logger(result.stdout)
    logger("STDERR:")
    logger(result.stderr)

    return result

def check_code_index_data(logger=print):
    """
    Check if the code index data is up-to-date with the LaTeX
    source files.
    If not, recompile the LaTeX files to update the data.
    """
    cwd = CODE_LABELS_DIR
    for tex_file in cwd.glob("*.tex"):
        compile = False
        data_path = tex_file.with_name(tex_file.stem + "-data.txt")
        if not data_path.exists():
            logger(f"File {data_path} does not exist. Compiling {tex_file}.")
            compile = True
        elif data_path.stat().st_mtime < tex_file.stat().st_mtime:
            logger(f"File {data_path} is older than {tex_file}. Recompiling.")
            compile = True
        elif CONFIG["catalogues"]["packages to check"].get(tex_file.name) is not None:
            packages = CONFIG["catalogues"]["packages to check"][tex_file.name]
            for package in packages:
                
                package_path = next(TEX_PACKAGES_DIR.rglob(package), None)

                if package_path is None:
                    print(f"Fichier introuvable {package} dans {TEX_PACKAGES_DIR}")
                else:
                    print(package_path)

                if data_path.stat().st_mtime < package_path.stat().st_mtime:
                    logger(f"File {data_path} is older than package {package_path}. Recompiling.")
                    compile = True
                    break

        if compile:
            result = compile_latex(tex_file, logger=logger)
            if result.returncode != 0:
                logger(f"Compilation of {tex_file} failed. Please check the LaTeX file.")
                continue

def insert_nested(d, codes_values):
    """
    Insert a value into a nested dictionary based on a list of keys.
    """
    *keys, value = codes_values

    current = d
    for key in keys[:-1]:
        current = current.setdefault(key, {})

    current[keys[-1]] = value

def update_code_index(logger=print):
    """
    Update the code index with the latest data from the LaTeX
    source files
    """
    check_code_index_data(logger=logger)
    cwd = CODE_LABELS_DIR
    code_index_parent = CODE_INDEX_DIR

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
    update_code_index()