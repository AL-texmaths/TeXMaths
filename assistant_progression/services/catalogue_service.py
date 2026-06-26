# services/catalogue_service.py
from assistant_progression.models.entry import Entry
from pathlib import Path
import json

def get_catalogue_data(catalogue_path):
    with open(catalogue_path, encoding="utf-8") as f:
        return json.load(f)

def build_entries(data, catalogue_name=None):
    entries = []
    for catalogue, catalogue_data in data.items():
        if catalogue_name and catalogue != catalogue_name:
            continue
        if isinstance(list(catalogue_data.values())[0], dict):
            for source_type, source_data in catalogue_data.items():
                for code, text in source_data.items():
                    entries.append(Entry(catalogue=catalogue, type=source_type, code=code, text=text))
        else:
            for source_type, source_code in catalogue_data.items():
                entries.append(Entry(catalogue=catalogue, type=source_type, code=source_code, text=""))
    return entries