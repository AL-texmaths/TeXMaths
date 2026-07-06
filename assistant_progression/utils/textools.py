from __future__ import annotations

import json
import subprocess
from pathlib import Path

from assistant_progression.models.config import Config
from assistant_progression.utils.resolve import resolve_executable

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
    logger=print,
    config:Config|None=None
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
        executable_path = resolve_executable(motor, config=config)
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

def check_code_index_data(code_labels_dir, texmf_dir, config:Config|None=None, logger=print):
    """
    Check if the code index data is up-to-date with the LaTeX
    source files.
    If not, recompile the LaTeX files to update the data.
    """
    for tex_file in code_labels_dir.glob("*.tex"):
        compile = False
        data_path = tex_file.with_name(tex_file.stem + "-data.txt")
        if not data_path.exists():
            logger(f"File {data_path} does not exist. Compiling {tex_file}.")
            compile = True
        elif data_path.stat().st_mtime < tex_file.stat().st_mtime:
            logger(f"File {data_path} is older than {tex_file}. Recompiling.")
            compile = True

        sty_file_name = None

        if config is not None:
            catalogues = config.catalogues
        else:
            logger("check_code_index_data:No config provided, catalogues will be empty.")
            catalogues = {}
        for key in catalogues.keys():
            catalogue = catalogues[key]
            if tex_file.name == catalogue.tex_file_name:
                sty_file_name = catalogue.sty_file_name

        if sty_file_name is not None:
            logger(f"Checking package {sty_file_name}")
            package_path = next(texmf_dir.rglob(sty_file_name), None)

            if package_path is None:
                logger(f"Fichier introuvable {sty_file_name} dans {texmf_dir}")
            else:
                logger(f"Analysing package {sty_file_name} at {package_path}")

            if data_path.stat().st_mtime < package_path.stat().st_mtime:
                logger(f"File {data_path} is older than package {package_path}. Recompiling.")
                compile = True
        
        result = 0
        if compile:
            result = compile_latex(tex_file, logger=logger, config=config)
            if result.returncode != 0:
                logger(f"Compilation of {tex_file} failed. Please check the LaTeX file.")
                continue
        return result

def insert_nested(d, codes_values):
    """
    Insert a value into a nested dictionary based on a list of keys.
    """
    *keys, value = codes_values

    current = d
    for key in keys[:-1]:
        current = current.setdefault(key, {})

    current[keys[-1]] = value

def update_code_index(
        code_labels_dir:Path|str,
        code_index_dir:Path|str,
        texmf_dir:Path|str,
        config:Config|None=None,
        code_index_file_name:str="code_index.json",
        logger=print
        ) -> int:
    """
    Update the code index with the latest data from the LaTeX
    source files
    """
    result = check_code_index_data(
        code_labels_dir=code_labels_dir,
        texmf_dir=texmf_dir,
        config=config,
        logger=logger
        )

    code_index_data = {}
    for data_file in code_labels_dir.glob("*-data.txt"):
        with open(data_file, "r", encoding="utf-8") as f:
            for line in f:
                codes_values = line.strip().split('|:|')
                insert_nested(code_index_data, codes_values)
    
    if config is not None and code_index_file_name is None:
            code_index_file_name = config.settings.current.code_index_file_name

    code_index_file = code_index_dir / code_index_file_name
    with open(code_index_file, "w", encoding="utf-8") as f:
            json.dump(code_index_data, f, ensure_ascii=False, indent=4)
    
    return result
