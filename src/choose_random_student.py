import re
import json
import time
import random
from src.tools import DATA_DIR

DIRPATH = DATA_DIR / "student_lists"

div__number = 3

def get_current_classe_dict():
    with open(DIRPATH / 'full_student_list.json', 'r', encoding='utf-8') as full_file:
        classe_dict = json.load(full_file)
    return classe_dict

def get_all_classes():
    classes = []
    for filename in DIRPATH.iterdir():
        matches = re.findall('liste-(.*?).txt', str(filename))
        if matches:
            classes.append(matches[0])
    return classes

def get_new_classe_dict():
    classes_dict = {}
    for classe in get_all_classes():
        with open(DIRPATH / 'liste-{}.txt'.format(classe), 'r', encoding='utf8') as listfile:
            for line in listfile:
                if line[-1] == '\n':
                    key = line[:-1]
                else:
                    key = line
                classes_dict[key] = {'classe' :classe}
    return classes_dict

current_classe_dict = get_current_classe_dict()
new_classe_dict = get_new_classe_dict()

keys_to_del = []
for key in current_classe_dict.keys():
    if not key in new_classe_dict.keys():
        keys_to_del.append(key)
    
for key in keys_to_del:
    del current_classe_dict[key]

for key in new_classe_dict.keys():
    if not key in current_classe_dict.keys():
        current_classe_dict[key] = new_classe_dict[key]

max_lenght = max(map(lambda name: len(name), current_classe_dict.keys()))

def get_classe(classe):
    names = list(filter(lambda key: current_classe_dict[key]['classe'] == classe, current_classe_dict.keys()))
    probability = list(map(lambda key: current_classe_dict[key]['probability'], filter(lambda key: current_classe_dict[key]['classe'] == classe, current_classe_dict.keys())))
    return names, probability


def get_random_name(classe):
    names = list(filter(lambda key: current_classe_dict[key]['classe'] == classe, current_classe_dict.keys()))
    probability = list(map(lambda key: current_classe_dict[key]['probability'], filter(lambda key: current_classe_dict[key]['classe'] == classe, current_classe_dict.keys())))
    s = sum(probability)
    probability = [p/s for p in probability]
    return random.choices(names, weights=probability, k=1)[0]

def passage(search_duration=3, sleep_time=0.05):
    print("Recherche d'un nom ...")
    for _ in range(int(search_duration/sleep_time)):
        time.sleep(sleep_time)
        print(' '*max_lenght, end='\r')
        print(get_random_name(classe), end='\r')
    choosen_name = get_random_name(classe)
    print(' '*max_lenght, end='\r')
    print('='*max_lenght)
    print(choosen_name)
    print('='*max_lenght)

    codezero = input('Enregistrer le passage ? (O/N)')
    while not codezero.strip() == 'O' and not codezero.strip() == 'N':
        print(f'Commande <{codezero}> invalide. Répondre par O ou N :')
        codezero = input()
    if codezero == 'O':
        current_classe_dict[choosen_name]['probability'] = current_classe_dict[choosen_name]['probability']/div__number

    with open(DIRPATH / 'full_student_list.json', 'w', encoding='utf8') as fullstudentlist:
            json.dump(current_classe_dict, fullstudentlist, indent=4, ensure_ascii=False)
    
    nextstudent = input('Voulez vous poursuivre ? (O/N)')
    while not nextstudent.strip() == 'O' and not nextstudent.strip() == 'N':
        print(f'Commande <{nextstudent}> invalide. Répondre par O ou N :')
        nextstudent = input()
    
    return nextstudent

if __name__ == '__main__':
    classe = input('Entrez le nom de la classe ')
    for name, prob in zip(*get_classe(classe)):
        print(f'{name} : {prob}')
    nextstudent = passage()
    while nextstudent == 'O':
        nextstudent = passage()