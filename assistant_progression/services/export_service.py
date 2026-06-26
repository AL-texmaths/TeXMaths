from pathlib import Path


class ExportService:

    def export_progression(
        self,
        filename,
        progression,
        labels
    ):
        latex = self.build_latex(
            progression,
            labels
        )

        Path(filename).write_text(
            latex,
            encoding="utf-8"
        )

    def build_latex(
        self,
        progression,
        labels
    ):

        lines = []

        level_num = 0

        for level, chapters in progression.items():

            if level_num > 0:
                lines.append("\\showtotalseance")

            level_num += 1

            lines.append(
                f"\\level{{{level}}}"
            )

            for chapter, content in chapters.items():

                lines.append(
                    f"\\sequence{{{chapter}}}"
                )

                automatismes = ",".join(
                    content.get(
                        labels["aut"],
                        []
                    )
                )

                objectifs = ",".join(
                    content.get(
                        labels["obj"],
                        []
                    )
                )

                prolongements = ",".join(
                    content.get(
                        labels["pro"],
                        []
                    )
                )

                lines.append(
                    f"    \\BoItems{{{automatismes}}}"
                    f"{{{objectifs}}}"
                    f"{{{prolongements}}}"
                )

                for seance in content.get(
                    labels["sea"],
                    []
                ):

                    lines.append(
                        f"    \\seance{{{seance}}}"
                    )

                lines.append(
                    "\\endsequence"
                )

        lines.append(
            "\\showtotalseance"
        )

        return "\n".join(lines) + "\n"