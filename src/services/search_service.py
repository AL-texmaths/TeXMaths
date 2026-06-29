from pathlib import Path
import re


class SearchService:

    def __init__(self, repository):
        self.repository = repository
    
    def search(
            self,
            pattern,
            active_prefixes,
            active_fields,
            active_empty_filters,
            sort_mode
        ):
            if not pattern:
                return []
            try:
                regex = re.compile(pattern, re.IGNORECASE)
            except re.error:
                return []
            if not active_prefixes:
                return []
            
            matching_items = []

            for key, infos in self.repository.load().items():
                prefix = key.split()[0]

                if prefix not in active_prefixes:
                    continue

                # Filtre champs vides
                skip = False

                for field in active_empty_filters:
                    value = infos.get(field, "")

                    if value not in ["", None, []]:
                        skip = True
                        break
                if skip:
                    continue

                # Rassembler les parties recherchables selon les champs actifs
                searchable_parts = []
                for field in active_fields:
                    value = infos.get(field, "")
                    if isinstance(value, list):
                        searchable_parts.extend(str(v) for v in value)
                    else:
                        searchable_parts.append(str(value))

                if regex.search(" ".join(searchable_parts)):
                    matching_items.append((key, infos))
                
            if sort_mode == 0:
                # Tri par ordre alphabétique
                matching_items.sort(key=lambda x: x[0].lower())  # Tri par nom
            elif sort_mode == 1:
                # Tri par date de modification du fichier PDF
                matching_items.sort(key=lambda x: Path(x[1]["pdf"]).stat().st_mtime, reverse=True)

            return matching_items