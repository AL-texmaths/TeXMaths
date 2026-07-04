from pathlib import Path


COMMANDS = {
        "aut": "useaut",
        "obj": "useobj",
        "pro": "usepro",
    }

class ExportService:

    def export_node(self, node, out):
        text = node.get("text", "")
        data = node.get("data")
        children = node.get("children", [])

        # Feuille : un item du BO
        if data:
            try:
                _, kind, ident = data.split(":")
                cmd = COMMANDS.get(kind)
                if cmd:
                    out.write(f"\\{cmd}[{ident}]\n")
            except ValueError:
                print(f"Format de data invalide : {data}")
            return

        # Niveau (5eme, 4eme, ...)
        if children and all("children" in c for c in children):
            if text.endswith("eme") or text.endswith("e"):
                out.write(f"\\level{{{text}}}\n")

        # Séquence
        category_names = {
            "Automatismes",
            "Objectifs d'apprentissage",
            "Prolongements",
            "Séances",
        }

        if children and {c.get("text") for c in children} <= category_names:
            out.write(f"\\sequence{{{text}}}\n")

            for child in children:
                self.export_node(child, out)

            out.write("\\endsequence\n\n")
            return

        # Cas général
        for child in children:
            self.export_node(child, out)


    def export_progression(self, filename, progression_tree, code_labels):
        with open(filename, "w", encoding="utf-8") as out:
            for node in progression_tree:
                self.export_node(node, out)