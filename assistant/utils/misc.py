import re


def insert_nested(d, codes_values):
    """
    Insert a value into a nested dictionary based on a list of keys.
    """
    *keys, value = codes_values

    current = d
    for key in keys[:-1]:
        current = current.setdefault(key, {})

    current[keys[-1]] = value

def camel_to_sentence(s: str) -> str:
    s = s.replace('_', ' ').replace('-', ' ')
    s = re.sub(r'(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])', ' ', s)
    return s[0].upper() + s[1:] if s else s