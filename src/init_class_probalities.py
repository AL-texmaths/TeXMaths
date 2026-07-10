import sys
import json
from src.tools import get_config
from src.exe_pathes import resolve_pathes

LIST_KEY = 'liste-{0}.txt'
JSON_KEY = 'proba-{0}.json'
DIV_NUM = 3
N = 5


config  = get_config()
class_keys = sys.argv[1].split(',')
class_dir = resolve_pathes(*config["paths"]["student_lists"])

for class_key in class_keys:
    class_path = class_dir / LIST_KEY.format(class_key)
    class_dict_path = class_dir / JSON_KEY.format(class_key)

    class_dict = {}

    with open(class_path, 'r', encoding='utf-8') as f:
        for student_name in f:
            class_dict[student_name] = {
                "classe": class_key,
                "probability": DIV_NUM ** N
            }

    with open(class_dict_path, 'w', encoding='utf-8') as f:
        json.dump(class_dict, f, indent=4, ensure_ascii=False)