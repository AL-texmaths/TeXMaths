import re
import json
from src.tools import get_config, LATEX_DIR, get_pattern
"""
Lit les fichiers exercice-*-data.tex et stocke les
données dans un fichier json
"""
CATALOGUES = LATEX_DIR / "catalogues"
DOC_DICT = get_config()['settings']['index documents']

CYCLE_VALUE_DEFAUT = 'cycle 4'
BO_VALUE_DEFAULT = 'BO 2020'

with open(CATALOGUES / "code_index.json", 'r', encoding='utf-8') as codeindexfile:
        CODE_INDEX = json.load(codeindexfile)

# fonction de décodages des méta-données
def identity(value, **kwargs):
    return value, 0

def source(value, logger=print, **kwargs):
    if value == '':
        return '', 0
    else:
        try:
            result = CODE_INDEX['src'][value]
        except KeyError:
            logger(f'WARNING : source invalide ({value})\n' + kwargs['tex_relpath'])
            result = '', 1
        return result, 0

def cycle(value, logger=print, **kwargs):
    if value == '':
        logger(f'WARNING : empty cycle value\n' + kwargs['tex_relpath'])
        return '', 1
    return 'cycle ' + value, 0

def _decode_code_index_list(value, logger=print, *, top_key=None, subkey=None, top_label=None, **kwargs):
    """Decode a comma-separated list of codes from CODE_INDEX.

    - If `top_key` is provided, look up CODE_INDEX[top_key][code].
    - Otherwise, build `cycle_key = kwargs['cycle'] + ' ' + kwargs['bo']` and look up CODE_INDEX[cycle_key][subkey][code].
    Returns '' when input is empty, otherwise a list with decoded values ('' for unknown codes).
    """
    value = value.replace(' ', '')
    if value == '':
        logger(f'WARNING : empty value for {top_label or subkey}\n' + kwargs.get('tex_relpath', ''))
        return '', 1
    result = []
    cycle_key = None
    warns = 0
    for token in value.split(','):
        try:
            if top_key is not None:
                result.append(CODE_INDEX[top_key][token])
            else:
                cycle_key = kwargs['cycle'] + ' ' + kwargs['bo']
                result.append(CODE_INDEX[cycle_key][subkey][token])
        except KeyError:
            if top_key is not None:
                label = top_label or top_key
                logger(f'WARNING : {label} invalide ({token})\n' + kwargs.get('tex_relpath', ''))
            else:
                label_map = {'cns': 'connaissance', 'cmp': 'compétence', 'aut': 'automatisme'}
                label = label_map.get(subkey, subkey)#type:ignore
                logger(f'WARNING : {label} du {cycle_key} invalide ({token})\n' + kwargs.get('tex_relpath', ''))
            warns += 1
            result.append('')
    return result, warns

def competencesDuSocle(value, logger=print, **kwargs):
    return _decode_code_index_list(value, logger=logger, top_key='cmpsocle', top_label='competence du socle', **kwargs)

def connaissancesRequises(value, logger=print, **kwargs):
    return _decode_code_index_list(value, logger=logger, subkey='cns', **kwargs)

def competencesTravaillees(value, logger=print, **kwargs):
    return _decode_code_index_list(value, logger=logger, subkey='cmp', **kwargs)

def automatismes(value, logger=print, **kwargs):
    return _decode_code_index_list(value, logger=logger, subkey='aut', **kwargs)

def objectifsApprentissage(value, logger=print, **kwargs):
    return _decode_code_index_list(value, logger=logger, subkey='obj', **kwargs)

def prolongements(value, logger=print, **kwargs):
    return _decode_code_index_list(value, logger=logger, subkey='pro', **kwargs)

def update_doc_dict(doc_dict, logger=print):
    tex_relpath = doc_dict['tex']
    with open(tex_relpath, 'r', encoding='utf8') as file:
        ex_enonce = file.read()
        doc_dict['enonce'] = ex_enonce
    lines = iter(ex_enonce.splitlines())
    line = next(lines)
    errors = 0
    while not line.startswith(f'\\startdatakeys'):
        try:
            line = next(lines)
        except StopIteration:
            logger(f'Error: Could not find \\startdatakeys in {tex_relpath}')
            errors += 1
            break
    datakeys = ''
    cycle_value = CYCLE_VALUE_DEFAUT
    bo_value = BO_VALUE_DEFAULT
    while not line.startswith(f'\\enddatakeys'):
        try:
            line = next(lines)
        except StopIteration:
            logger(f'Error: Could not find \\enddatakeys in {tex_relpath}')
            errors += 1
            break
        # ignorer les lignes commentées commençant par '%' (après espaces éventuels)
        if line.lstrip().startswith('%'):
            continue
        datakeys += line
        if 'cycle' in line:
            try:
                cycle_value = 'cycle ' + re.findall(r'\{(.*?)\}', line)[0]
            except (IndexError, ValueError):
                pass
        if 'BO' in line:
            try:
                bo_value = 'BO ' + re.findall(r'\{(.*?)\}', line)[0]
            except (IndexError, ValueError):
                pass
    matches = re.findall(r'\\(.*?)\{(.*?)\}', datakeys)
    for key, value in matches:
        try: 
            decode_func = globals()[key]
        except KeyError:
            decode_func = identity
        doc_dict[key], warns = decode_func(value, logger=logger, cycle=cycle_value, bo=bo_value, tex_relpath=tex_relpath)
    while not line.startswith('\\begin{document}'):
        try:
            line = next(lines)
        except StopIteration:
            logger(f'Error: Could not find \\begin{{document}} in {tex_relpath}')
            errors += 1
            break
    return errors, warns
        

def get_doc_dict(tex_relpath, str_id, doc_type, logger=print):
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
    errors, warns = update_doc_dict(ex_dict, logger=logger)
    return ex_dict, errors, warns

def update_json(logger=print):
    """
    """
    Data_dict = {}
    errors, warns = 0, 0
    for doc_type, doc_dict in DOC_DICT.items():
        foldername = doc_dict['folder name']
        dirpath = LATEX_DIR / foldername
        pattern = get_pattern(doc_type, 'tex').replace('(data|[a-z])', 'data')
        for file_path in dirpath.iterdir():
            matches = re.findall(pattern, str(file_path))
            if matches:
                if type(matches[0]) is tuple:
                    str_id = '-'.join(matches[0])
                else:
                    str_id = matches[0]
                doc_type = file_path.stem.split('-')[0]
                Data_dict[foldername.capitalize() + ' ' + str_id], errors_sup, warns_sup = get_doc_dict(dirpath / file_path, str_id, doc_type, logger=logger)
                errors += errors_sup
                warns += warns_sup
        
    
    with open(CATALOGUES / "data_index.json", 'w', encoding='utf-8') as outfile:
            json.dump(Data_dict, outfile, indent=4, ensure_ascii=False)
    
    return errors, warns

if __name__ == "__main__":
    print('UPDATING : data index ...')
    update_json()
    print(f'module {__file__} ok')