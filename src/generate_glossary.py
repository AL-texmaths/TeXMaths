#!/usr/bin/env python3
"""Génère les commandes LaTeX du glossaire à partir de glossaire.yaml."""

from pathlib import Path
import argparse
import re
import unicodedata

import yaml


NIVEAUX = ("6e", "5e", "4e", "3e")


def cle_alphabetique(nom: str) -> str:
    """Trie sans distinction de casse ni d'accents."""
    normalise = unicodedata.normalize("NFD", nom.casefold())
    return "".join(c for c in normalise if not unicodedata.category(c).startswith("M"))


def sur_une_ligne(texte: str) -> str:
    """Conserve les paragraphes LaTeX tout en supprimant les retours à la ligne."""
    texte = re.sub(r"\n[ \t]*\n+", lambda _: r"\par ", texte.strip())
    return texte.replace("\n", " ")


def generer_latex(
    source: Path, destination: Path, niveau_maximal: str | None = None
) -> None:
    if niveau_maximal is not None and niveau_maximal not in NIVEAUX:
        raise ValueError(f"Niveau maximal invalide : {niveau_maximal!r}.")

    with source.open("r", encoding="utf-8") as fichier:
        donnees = yaml.safe_load(fichier) or {}
    if not isinstance(donnees, dict):
        raise ValueError("Le fichier YAML doit contenir un dictionnaire à la racine.")
    mots = donnees.get("mots")
    if not isinstance(mots, list):
        raise ValueError("Le fichier YAML doit contenir une liste 'mots'.")

    selection = []
    for numero, mot in enumerate(mots, start=1):
        if not isinstance(mot, dict):
            raise ValueError(f"L'entrée n° {numero} n'est pas un dictionnaire.")
        nom = mot.get("nom")
        definition = mot.get("definition_ecrite")
        if not isinstance(nom, str) or not nom.strip():
            raise ValueError(f"L'entrée n° {numero} doit posséder un nom non vide.")
        if not isinstance(definition, str):
            raise ValueError(f"L'entrée n° {numero} doit posséder une définition écrite.")
        if niveau_maximal is not None:
            niveau = mot.get("niveau")
            if niveau not in NIVEAUX:
                raise ValueError(f"Niveau invalide pour l'entrée n° {numero} : {niveau!r}.")
            if NIVEAUX.index(niveau) > NIVEAUX.index(niveau_maximal):
                continue
        selection.append((nom, definition))

    selection.sort(key=lambda mot: cle_alphabetique(mot[0]))
    lignes = [
        r"\writeword{" + sur_une_ligne(nom) + "}{" + sur_une_ligne(definition) + "}%"
        for nom, definition in selection
    ]

    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("".join(ligne + "\n" for ligne in lignes), encoding="utf-8")
    print(f"{len(selection)} mots exportés dans : {destination}")


def main():
    parser = argparse.ArgumentParser(
        description="Génère un fichier LaTeX depuis le glossaire YAML, trié par nom."
    )
    parser.add_argument(
        "source", nargs="?", type=Path, default=Path("data/latex/glossaire.yaml")
    )
    parser.add_argument(
        "destination", nargs="?", type=Path,
        default=None,
        help="Fichier de sortie (par défaut : glossaire-generated.tex à côté de la source).",
    )
    parser.add_argument(
        "--niveau-maximal", choices=NIVEAUX,
        help="Ne garder que ce niveau et les niveaux précédents (ex. 5e : 6e, 5e).",
    )
    args = parser.parse_args()
    destination = args.destination or args.source.parent / "glossaire-generated.tex"
    generer_latex(args.source, destination, args.niveau_maximal)


if __name__ == "__main__":
    main()
