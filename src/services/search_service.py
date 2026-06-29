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
            empty_filters):
            if not pattern:
                return []
            try:
                regex = re.compile(pattern, re.IGNORECASE)
            except re.error:
                return
            
            matching_items = []

            for key, infos in self.repository.load().items():
                prefix = key.split()[0]

                if prefix not in active_prefixes:
                    continue

                # Filtre champs vides
                skip = False
                for field, checkbox in empty_filters.items():
                    if checkbox.isChecked():
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

            return matching_items