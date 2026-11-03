#!/usr/bin/env python3
"""Compare le contenu des exercices d'un Markdown source avec le .tex généré.

Seules les transformations structurelles autorisées sont ignorées :
listes (enumerate/parts/subparts, \\item/\\part/\\subpart), \\question[..],
espaces de réponse, personnalisation locale des parties, \\newpage, commentaires
et espacements. Tout le reste doit être identique.

Usage : python verifier_fidelite.py entree.md sujet.tex
Code retour : 0 si tous les exercices sont fidèles, 1 sinon.
"""
import re
import sys
from pathlib import Path

LIST_ENVS = r"(?:enumerate|parts|subparts|subsubparts|choices|oneparchoices)"
CUSTOM_GROUP = re.compile(
    r"\\begingroup\s*\\renewcommand\\partlabel\{\}.*?\\renewcommand\{\\part\}\{%.*?\}%\s*\}\s*",
    re.S,
)


def normalise(text: str, drop_list_markers: bool) -> str:
    text = re.sub(r"(?<!\\)%.*", "", text)  # commentaires
    text = CUSTOM_GROUP.sub("", text)
    text = re.sub(r"\\endgroup", "", text)
    text = re.sub(r"\\question(\[[^\]]*\])?", "", text)
    text = re.sub(r"\\answerspace\s*\\answerspacelg", "", text)
    text = re.sub(r"\\(?:newpage|clearpage|pagebreak)(\[[^\]]*\])?", "", text)
    if drop_list_markers:
        text = re.sub(r"\\(?:begin|end)\{" + LIST_ENVS + r"\}", "", text)
        text = re.sub(r"\\(?:item|part|subpart|subsubpart)\b(\[[^\]]*\])?", "", text)
    return re.sub(r"\s+", "", text)


def exercices_md(path: Path) -> list[str]:
    md = path.read_text(encoding="utf-8")
    return re.findall(r"```latex\n(.*?)```", md, re.S)


def exercices_tex(path: Path) -> list[str]:
    tex = path.read_text(encoding="utf-8")
    body = tex.split(r"\begin{questions}", 1)[1].rsplit(r"\end{questions}", 1)[0]
    body = CUSTOM_GROUP.sub("", body)
    return re.split(r"(?=\\question)", body)[1:]


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    sources = exercices_md(Path(sys.argv[1]))
    generes = exercices_tex(Path(sys.argv[2]))
    if len(sources) != len(generes):
        print(f"ERREUR : {len(sources)} exercice(s) source, {len(generes)} \\question générée(s)")
        return 1
    ok = True
    for i, (src, gen) in enumerate(zip(sources, generes), 1):
        a, b = normalise(src, True), normalise(gen, True)
        if a == b:
            print(f"Exercice {i} : identique ({len(a)} caractères comparés)")
            continue
        ok = False
        k = next((j for j, (x, y) in enumerate(zip(a, b)) if x != y), min(len(a), len(b)))
        print(f"Exercice {i} : DIFFÉRENCE à la position {k}")
        print("  source :", a[max(0, k - 40):k + 60])
        print("  généré :", b[max(0, k - 40):k + 60])
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
