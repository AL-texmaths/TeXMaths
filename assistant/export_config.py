import json

def json_keys_structure(obj, indent=0):
    """
    Retourne une liste de lignes représentant la structure des clés du JSON.
    """
    lines = []
    prefix = "  " * indent

    if isinstance(obj, dict):
        for key, value in obj.items():
            lines.append(f"{prefix}- {key}")
            lines.extend(json_keys_structure(value, indent + 1))

    elif isinstance(obj, list):
        # On ne décrit que la structure des éléments de liste
        if obj:
            lines.append(f"{prefix}- [list]")
            lines.extend(json_keys_structure(obj[0], indent + 1))
        else:
            lines.append(f"{prefix}- [list vide]")

    else:
        # valeur terminale (on ne détaille pas)
        lines.append(f"{prefix}- {type(obj).__name__}")

    return lines


def append_json_structure_to_readme(json_file_path, readme_path):
    """
    Lit un fichier JSON et ajoute sa structure de clés à un README.md sans écraser le contenu existant.
    """
    # Chargement du JSON
    with open(json_file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Génération de la structure
    structure_lines = json_keys_structure(data)

    # Ajout au README.md
    with open(readme_path, "a", encoding="utf-8") as f:
        f.write("\n\n")
        f.write("## Structure du fichier de configuration JSON\n\n")
        f.write("\n".join(structure_lines))
        f.write("\n")

import sys

if __name__ == "__main__":
    append_json_structure_to_readme(sys.argv[1], sys.argv[2])