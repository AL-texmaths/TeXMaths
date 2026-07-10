import re
import json
from src_ap.utils.textools import get_pattern
"""
Lit les fichiers exercice-*-data.tex et stocke les
données dans un fichier json
"""

CYCLE_KEY = 'cycle_{}_BO_{}'

class UpdateDataService:
    def __init__(self, context, logger=print):
        self.context = context
        self.types_dict = context.config.settings.pedago_service.pedago_doc_types
        self.latex_path = context.paths.latex
        self.code_index_path = context.paths.code_index
        self.logger = logger

        self.cycle_value_default = '4'
        self.bo_value_default = '2026'
        self.errors = 0
    
    def display_error(self, message):
        self.logger(message)
        self.errors += 1

    @staticmethod
    def identity(value, **kwargs):
        return value

    def source(self, value, **kwargs):
        if value == '':
            return ''
        else:
            try:
                result = self.context.code_index_data['src'][value]
            except KeyError:
                self.display_error(f'WARNING : source invalide ({value})\n' + kwargs['tex_relpath'])
                result = ''
            return result

    def cycle(self, value, **kwargs):
        if value == '':
            self.display_error(f'WARNING : empty cycle value\n' + kwargs['tex_relpath'])
            return ''
        return str(value)

    def decode_code_index_list(self, value, *, top_key=None, subkey=None, top_label=None, **kwargs):
        """Decode a comma-separated list of codes from CODE_INDEX.

        - If `top_key` is provided, look up CODE_INDEX[top_key][code].
        - Otherwise, build `cycle_key = CYCLE_KEY.format(kwargs['cycle'], kwargs['bo'])` and look up CODE_INDEX[cycle_key][subkey][code].
        Returns '' when input is empty, otherwise a list with decoded values ('' for unknown codes).
        """
        value = value.replace(' ', '')
        if value == '':
            self.display_error(f'WARNING : empty value for {top_label or subkey}\n' + kwargs.get('tex_relpath', ''))
            return ''
        result = []
        cycle_key = None
        for token in value.split(','):
            try:
                if top_key is not None:
                    result.append(self.context.code_index_data[top_key][token])
                else:
                    cycle_key = CYCLE_KEY.format(kwargs['cycle'], kwargs['bo'])
                    result.append(self.context.code_index_data[cycle_key][subkey][token])
            except KeyError:
                if top_key is not None:
                    label = top_label or top_key
                    self.display_error(f'WARNING : {label} invalide ({token})\n' + kwargs.get('tex_relpath', ''))
                else:
                    label_map = {'cns': 'connaissance', 'cmp': 'compétence', 'aut': 'automatisme'}
                    label = label_map.get(subkey, subkey)#type:ignore
                    self.display_error(f'WARNING : {label} du {cycle_key} invalide ({token})\n' + kwargs.get('tex_relpath', ''))
                result.append('')
        return result

    def competencesDuSocle(self, value, **kwargs):
        return self.decode_code_index_list(value, top_key='cmpsocle', top_label='competence du socle', **kwargs)

    def connaissancesRequises(self, value, **kwargs):
        return self.decode_code_index_list(value, subkey='cns', **kwargs)

    def competencesTravaillees(self, value, **kwargs):
        return self.decode_code_index_list(value, subkey='cmp', **kwargs)

    def automatismes(self, value, **kwargs):
        return self.decode_code_index_list(value, subkey='aut', **kwargs)

    def objectifsApprentissage(self, value, **kwargs):
        return self.decode_code_index_list(value, subkey='obj', **kwargs)

    def prolongements(self, value, **kwargs):
        return self.decode_code_index_list(value, subkey='pro', **kwargs)

    def update_doc_dict(self, doc_dict):
        tex_relpath = doc_dict['tex']
        with open(tex_relpath, 'r', encoding='utf8') as file:
            ex_enonce = file.read()
            doc_dict['enonce'] = ex_enonce
        lines = iter(ex_enonce.splitlines())
        line = next(lines)
        while not line.startswith(f'\\startdatakeys'):
            try:
                line = next(lines)
            except StopIteration:
                self.display_error(f'Error: Could not find \\startdatakeys in {tex_relpath}')
                break
        datakeys = ''
        cycle_value = self.cycle_value_default
        bo_value = self.bo_value_default
        while not line.startswith(f'\\enddatakeys'):
            try:
                line = next(lines)
            except StopIteration:
                self.display_error(f'Error: Could not find \\enddatakeys in {tex_relpath}')
                break
            # ignorer les lignes commentées commençant par '%' (après espaces éventuels)
            if line.lstrip().startswith('%'):
                continue
            datakeys += line
            if 'cycle' in line:
                try:
                    cycle_value = re.findall(r'\{(.*?)\}', line)[0]
                except (IndexError, ValueError):
                    pass
            if 'BO' in line:
                try:
                    bo_value = re.findall(r'\{(.*?)\}', line)[0]
                except (IndexError, ValueError):
                    pass
        matches = re.findall(r'\\(.*?)\{(.*?)\}', datakeys)

        for key, value in matches:
            decode_func = getattr(self, key, self.identity)
            doc_dict[key] = decode_func(value, cycle=cycle_value, bo=bo_value, tex_relpath=tex_relpath)
        while not line.startswith('\\begin{document}'):
            try:
                line = next(lines)
            except StopIteration:
                self.display_error(f'Error: Could not find \\begin{{document}} in {tex_relpath}')
                break
        

    def get_doc_dict(self, tex_relpath, str_id, doc_type):
        pdf_path = tex_relpath.with_suffix('.pdf').resolve()
        ex_dict = {
            "type": doc_type,
            "id": str_id,
            'tex': str(tex_relpath),
            "pdf": str(pdf_path),
        }
        if doc_type == 'flash':
            preview_path = str(pdf_path.parent / "previews" / ('preview-' + pdf_path.name))
            ex_dict['preview'] = preview_path
        self.update_doc_dict(ex_dict)
        self.logger(f"Updated document dictionary for {tex_relpath}")
        return ex_dict

    def update_data_index(self):
        """
        """
        Data_dict = {}
        for doc_type, doc_dict in self.types_dict.items():
            foldername = doc_dict.dir_name
            dirpath = self.latex_path / foldername
            pattern = get_pattern(self.types_dict, doc_type, 'tex').replace('(data|[a-z])', 'data')
            for file_path in dirpath.iterdir():
                matches = re.findall(pattern, str(file_path))
                if matches:
                    if type(matches[0]) is tuple:
                        str_id = '-'.join(matches[0])
                    else:
                        str_id = matches[0]
                    doc_type = file_path.stem.split('-')[0]
                    Data_dict[foldername.capitalize() + ' ' + str_id] = self.get_doc_dict(dirpath / file_path, str_id, doc_type)
            
        
        with open(
            self.code_index_path / self.context.config.settings.current.pdf_data_file_name,
            'w', encoding='utf-8') as outfile:
                json.dump(Data_dict, outfile, indent=4, ensure_ascii=False)
        