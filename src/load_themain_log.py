import re
from pathlib import Path
from src.tools import LATEX_DIR, DATA_DIR


file_open = re.compile(r"\(([^()\n]+\.tex)")
error_re = re.compile(r"^! (.+)")
latex_warning = re.compile(r"LaTeX Warning: (.+)")
package_warning = re.compile(r"Package .* Warning: (.+)")
overfull = re.compile(r"(Over|Under)full \\[hv]box .*")
line_info = re.compile(r"lines? (\d+)")


def parse_log(text):

    stack = []
    results = []

    for line in text.splitlines():

        # ouverture de fichiers .tex
        for m in file_open.finditer(line):
            stack.append(m.group(1))

        current_file = stack[-1] if stack else "unknown"

        # erreurs
        m = error_re.search(line)
        if m:
            results.append(("ERROR", current_file, m.group(1)))
            continue

        # LaTeX warning
        m = latex_warning.search(line)
        if m:
            results.append(("WARNING", current_file, m.group(1)))
            continue

        # Package warning
        m = package_warning.search(line)
        if m:
            results.append(("WARNING", current_file, m.group(1)))
            continue

        # Overfull / Underfull
        m = overfull.search(line)
        if m:
            results.append(("INFO", current_file, m.group(0)))
            continue

    return results


def write_output(results, outpath):

    lines = []
    current = None

    for level, file, msg in results:

        if file != current:
            lines.append("")
            lines.append(f"FILE: {file}")
            lines.append("-" * (6 + len(file)))
            current = file

        lines.append(f"[{level}] {msg}")

    Path(outpath).write_text("\n".join(lines), encoding="utf8")

logpath_in = LATEX_DIR / 'main.log'
logpath_out = DATA_DIR / 'logs' / 'main.log'

def main():

    log_in = logpath_in.read_text(encoding="latin1", errors="ignore")

    results = parse_log(log_in)

    write_output(results, logpath_out)

if __name__ == "__main__":
    main()
