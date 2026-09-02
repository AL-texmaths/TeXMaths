import sys
import json
from tabulate import tabulate
from src.tools import get_config, resolve_pathes

classes = sys.argv[1].split(",")
config  = get_config()
STUDENT_LISTS_DIR = resolve_pathes(*config["paths"]["student_lists"])
LIST_KEY = config["settings"]["student_lists"]["list_key"]

for classe_key in classes:
    list_path = STUDENT_LISTS_DIR / LIST_KEY.format(classe_key, "json")

    if not list_path.exists():
        print(f"La classe {classe_key} n'existe pas.")
        continue
    with open(list_path, encoding="utf-8") as f:
        data = json.load(f)

    table = []

    for eleve in data.values():
        notes = [p["note"] for p in eleve["passages"]]

        moyenne = sum(notes) / len(notes) if notes else None

        table.append([
            eleve["name"],
            len(notes),
            f"{moyenne:.2f}" if moyenne is not None else "-"
        ])

    print(tabulate(
        table,
        headers=["Élève", "Nb passages", "Moyenne"],
        tablefmt="rounded_grid"
    ))