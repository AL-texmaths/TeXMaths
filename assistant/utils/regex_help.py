# regex_help.py
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Recipe:
    need: str
    syntax: str
    example: str


# Les (?s:...) évitent les drapeaux globaux : la recette reste valide après "code:" ou "text:".
RECIPES = (
    Recipe("MotA ou MotB", "MotA|MotB", "fraction|pourcentage"),
    Recipe("MotA et MotB (ordre libre)", "(?s:^(?=.*MotA)(?=.*MotB))", "(?s:^(?=.*fraction)(?=.*pourcentage))"),
    Recipe("MotA mais pas MotB", "(?s:^(?=.*MotA)(?!.*MotB))", "(?s:^(?=.*fraction)(?!.*brevet))"),
    Recipe("Tous parmi A, B, C", "(?s:^(?=.*MotA)(?=.*MotB)(?=.*MotC))", "(?s:^(?=.*aire)(?=.*cercle)(?=.*disque))"),
    Recipe("Au moins un parmi A, B, C", "MotA|MotB|MotC", "aire|périmètre|volume"),
    Recipe("Aucun parmi A, B, C", "(?s:^(?!.*(?:MotA|MotB|MotC)))", "(?s:^(?!.*(?:brevet|dnb|corrigé)))"),
    Recipe(
        "(A ou B) et C, sans D",
        "(?s:^(?=.*(?:MotA|MotB))(?=.*MotC)(?!.*MotD))",
        "(?s:^(?=.*(?:aire|volume))(?=.*cercle)(?!.*brevet))",
    ),
    Recipe("Mot entier uniquement", r"\bMotA\b", r"\bair\b"),
    Recipe("MotA puis MotB (ordre imposé)", "MotA.*MotB", "fraction.*pourcentage"),
    Recipe("Commence par MotA", "^MotA", "^Calculer"),
    Recipe("Finit par MotA", "MotA$", "cm$"),
    Recipe("Un chiffre", r"MotA\d", r"exercice\d"),
    Recipe("Caractère spécial littéral (. ( ) + ? *)", r"MotA\.", r"3\.5"),
)

PLACEHOLDER = "MotA"

PREFIX_NOTE = (
    "Barre du catalogue : « code:REGEX » cible le code, « text:REGEX » cible le texte "
    "(ex. code:^AP.*fraction)."
)

GENERAL_NOTE = (
    "La recherche ignore la casse (mais pas les accents). "
    "Dans les recettes, remplacez MotA, MotB… par vos mots."
)

_WORD_RE = re.compile(r'"([^"]+)"|(\S+)')


def split_words(text: str) -> list[str]:
    """Découpe sur les espaces ; les guillemets regroupent une expression."""
    return [quoted or plain for quoted, plain in _WORD_RE.findall(text)]


def _term(word: str, whole_word: bool) -> str:
    term = re.escape(word).replace("\\ ", " ")
    return rf"\b{term}\b" if whole_word else term


def _alternation(words: list[str], whole_word: bool) -> str:
    terms = [_term(w, whole_word) for w in words]
    return terms[0] if len(terms) == 1 else "(?:" + "|".join(terms) + ")"


def build_regex(
    all_words: list[str],
    any_words: list[str],
    none_words: list[str],
    whole_word: bool = False,
) -> str:
    """Regex : tous les all_words, au moins un des any_words, aucun des none_words."""
    if not (all_words or any_words or none_words):
        return ""

    if not none_words:
        if not all_words:
            return "|".join(_term(w, whole_word) for w in any_words)
        if len(all_words) == 1 and not any_words:
            return _term(all_words[0], whole_word)

    parts = [f"(?=.*{_term(w, whole_word)})" for w in all_words]
    if any_words:
        parts.append(f"(?=.*{_alternation(any_words, whole_word)})")
    if none_words:
        parts.append(f"(?!.*{_alternation(none_words, whole_word)})")
    return "(?s:^" + "".join(parts) + ")"


def regex_error(pattern: str) -> str | None:
    """Message d'erreur si le motif est invalide, sinon None."""
    try:
        re.compile(pattern, re.IGNORECASE)
    except re.error as exc:
        return str(exc)
    return None
