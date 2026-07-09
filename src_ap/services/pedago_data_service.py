import json
from pathlib import Path
from src_ap.models.pedago import PedagoDoc


class PadagoDataService:
    def __init__(self, pdf_data_path:Path|str):
        self.pdf_data_path = Path(pdf_data_path)
        self.data, self._data = {}, {}
        self.refresh()

    def refresh(self):
        self.load()
        self.build_obj()
    
    def load(self):
        with open(self.pdf_data_path, 'r', encoding='utf-8') as f:
            self._data = json.load(f)
    
    def build_obj(self):
        for pedadoc_dict in self._data.values():
            try:
                pedagodoc_obj = PedagoDoc(**pedadoc_dict)
                self.data["-".join([pedagodoc_obj.type, pedagodoc_obj.id])] = pedagodoc_obj
            except TypeError as e:
                msg = str(e)
                import re
                m = re.search(r"unexpected keyword argument '([^']+)'", msg)
                if m:
                    print(f'WARNING: Wrong field name: {m.group(1)} in PedagoDoc {pedadoc_dict.get("type")} {pedadoc_dict.get("id")}')
                else:
                    print(msg)
                continue

pedago_data_service = PadagoDataService('D:/Projects/TeXMaths/data/latex/catalogues/data_index.json')