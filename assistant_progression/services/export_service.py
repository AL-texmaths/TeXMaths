TYPES  = ["aut", "obj", "pro", "sea"]

class ExportService:

    def __init__(self, code_labels):
        self.code_labels = code_labels

    def export_item(self, node):
        """Retourne la commande LaTeX d'un item."""
        data = node.get("data")
        if not data:
            return None

        if data == "seance":
            return ("seance", node["text"])

        try:
            _, kind, ident = data.split(":")
        except ValueError:
            return None

        cmd = self.code_labels.get(kind).command
        if cmd:
            return ("item", cmd.format(ident))

        return None

    def export_sequence(self, sequence, out):
        out.write(f"\\sequence{{{sequence['text']}}}\n")

        buffers = {self.code_labels.get(_type).name: [] for _type in TYPES}

        # remplir les buffers
        for category in sequence.get("children", []):
            cat_name = category.get("text")

            for item in category.get("children", []):
                result = self.export_item(item)
                if not result:
                    continue

                kind, value = result

                if kind == "seance":
                    buffers["Séances"].append(value)
                else:
                    buffers[cat_name].append(value)

        # écrire les blocs LaTeX
        for _type in TYPES:

            name = self.code_labels.get(_type).name

            if name == "Séances":
                continue

            items = buffers.get(name, [])
            if not items:
                continue

            out.write(f"\\par\\noindent\\textbf{{{name} :}}\n")
            out.write("\\begin{itemize}\n")

            for it in items:
                out.write(f"    \\item {it}\n")

            out.write("\\end{itemize}\n")

        # séances (hors itemize)
        for seance in buffers["Séances"]:
            out.write(f"\\seance{{{seance}}}\n")

        out.write("\\endsequence\n\n")

    def export_level(self, level, out):
        out.write(f"\\level{{{level['text']}}}\n")

        for sequence in level.get("children", []):
            self.export_sequence(sequence, out)

        out.write("\\endlevel\n\n")

    def export_progression(self, filename, progression_tree):
        with open(filename, "w", encoding="utf-8") as out:
            for level in progression_tree:
                self.export_level(level, out)