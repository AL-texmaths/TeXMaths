#!/usr/bin/env python3
"""Génère les commandes LaTeX du glossaire à partir de glossaire.yaml."""

from pathlib import Path
import argparse
import yaml
import sys

glossary_path_str = sys.argv[1] if len(sys.argv) > 1 else "data/latex/glossaire.yaml"
glossary_path = Path(glossary_path_str).resolve(strict=True)


CHAMPS_TEX = (
    "nom",
    "definition_ecrite",
    "definition_orale",
    "definition_rigoureuse",
    "niveau",
)


def tex_argument(value):
    """Place une valeur dans un argument LaTeX sans en modifier le contenu."""
    if value is None:
        value = ""
    return "{" + str(value).strip() + "}"


def generer_latex(source: Path, destination: Path) -> None:
    with source.open("r", encoding="utf-8") as fichier:
        donnees = yaml.safe_load(fichier) or {}

    mots = donnees.get("mots")
    if not isinstance(mots, list):
        raise ValueError("Le fichier YAML doit contenir une liste 'mots'.")

    lignes = [
        "% Fichier généré automatiquement à partir de glossaire.yaml.",
        "% Ne pas modifier directement : modifier le fichier YAML.",
        "",
    ]

    for numero, mot in enumerate(mots, start=1):
        if not isinstance(mot, dict):
            raise ValueError(f"L'entrée n° {numero} n'est pas un dictionnaire.")

        identifiant = mot.get("id")
        nom = mot.get("nom")
        if not identifiant or nom is None:
            raise ValueError(
                f"L'entrée n° {numero} doit posséder au minimum 'id' et 'nom'."
            )

        arguments = [tex_argument(mot.get(champ, "")) for champ in CHAMPS_TEX]
        lignes.append(r"\newword" + "\n    " + "\n    ".join(arguments))
        lignes.append("")

    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("\n".join(lignes), encoding="utf-8")
    print(f"{len(mots)} mots exportés dans : {destination}")


def main():
    parser = argparse.ArgumentParser(
        description="Génère un fichier LaTeX depuis le glossaire YAML."
    )
    parser.add_argument(
        "source", nargs="?", type=Path, default=glossary_path
    )
    parser.add_argument(
        "destination", nargs="?", type=Path,
        default=glossary_path.parent / "glossaire-generated.tex"
    )
    args = parser.parse_args()
    generer_latex(args.source, args.destination)


if __name__ == "__main__":
    main()
