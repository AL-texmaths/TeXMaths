import json
from pathlib import Path
from src_ap.models.pedago import PedagoDoc
from src_ap.utils.textools import latex_text_to_unicode


class PedagoDataService:
    def __init__(self, pdf_data_path:Path|str, to_convert: list[str] = []):
        self.pdf_data_path = Path(pdf_data_path)
        self.to_convert = to_convert
        self.data, self._data = {}, {}

    def refresh(self):
        self.load()
        self.build_obj()
    
    def load(self):
        if not self.pdf_data_path.exists():
            print('WARNING: PDF data file does not exist.\n Consider updating data index.')
            return
        print(f'Loading PDF data from {self.pdf_data_path}')
        with open(self.pdf_data_path, 'r', encoding='utf-8') as f:
            self._data = json.load(f)

    def build_obj(self):
        for pedadoc_dict in self._data.values():
            try:
                pedagodoc_obj = PedagoDoc(**pedadoc_dict)
                self.data["-".join([pedagodoc_obj.type, pedagodoc_obj.id])] = pedagodoc_obj
                for to_convert_attr in self.to_convert:
                    attr_value = getattr(pedagodoc_obj, to_convert_attr, None)
                    if attr_value is not None:
                        if isinstance(attr_value, str):
                            converted_value = latex_text_to_unicode(attr_value)
                        elif isinstance(attr_value, list):
                            converted_value = [latex_text_to_unicode(c) for c in attr_value]
                        else:
                            print(f'WARNING: Unexpected type for attribute {to_convert_attr} in PedagoDoc')
                            continue
                        setattr(pedagodoc_obj, to_convert_attr, converted_value)

            except TypeError as e:
                msg = str(e)
                import re
                m = re.search(r"unexpected keyword argument '([^']+)'", msg)
                if m:
                    print(f'WARNING: Wrong field name: {m.group(1)} in PedagoDoc {pedadoc_dict.get("type")} {pedadoc_dict.get("id")}')
                else:
                    print(msg)
                continue
    
    def get_types(self) -> list[str]:
        prefixes = set()
        for document in self.data.values():
            prefixes.add(document.type)
        return sorted(prefixes)

    def get_fields(self) -> list[str]:
        fields = set()
        for document in self.data.values():
            fields.update(document.__dict__.keys())
        return sorted(fields)
