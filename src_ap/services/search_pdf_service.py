import re
from pathlib import Path

from src.models.search_filters import SearchFilters

class SearchPDFService:

    def __init__(self, repository):
        self.repository = repository
    
    def search(
            self,
            filters: SearchFilters,
        ):
            if not filters.pattern:
                return []
            try:
                regex = re.compile(filters.pattern, re.IGNORECASE)
            except re.error:
                return []
            if not filters.active_prefixes:
                return []
            
            matching_items = []

            for key, infos in self.repository.data.items():
                prefix = key.split()[0]

                if prefix not in filters.active_prefixes:
                    continue

                # Filtre champs vides
                skip = False

                for field in filters.empty_fields:
                    value = getattr(infos, field, "")

                    if value not in ["", None, []]:
                        skip = True
                        break
                if skip:
                    continue

                # Rassembler les parties recherchables selon les champs actifs
                searchable_parts = []
                for field in filters.active_fields:
                    value = getattr(infos, field, "")
                    if isinstance(value, list):
                        searchable_parts.extend(str(v) for v in value)
                    else:
                        searchable_parts.append(str(value))

                if regex.search(" ".join(searchable_parts)):
                    matching_items.append((key, infos))
                
            if filters.sort_mode == 0:
                # Tri par ordre alphabétique
                matching_items.sort(key=lambda x: x[0].lower())  # Tri par nom
            elif filters.sort_mode == 1:
                # Tri par date de modification du fichier PDF
                matching_items.sort(key=lambda x: x[1].get_pdf_modification_date(), reverse=True)

            return matching_items