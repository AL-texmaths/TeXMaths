import re
import json
import time
import random
from src.tools import get_config
from src.exe_pathes import resolve_pathes
from datetime import datetime
from dataclasses import dataclass, field, asdict

config  = get_config()
settings = config["settings"]["student_lists"]
CLASS_DIR = resolve_pathes(*config["paths"]["student_lists"])
LIST_KEY = settings["list_key"]
JSON_KEY = settings["proba_key"]
DIV_NUM = settings["div_num"]
N = settings["max_num_passages"]

def get_all_classes():
    classes = []
    for filename in CLASS_DIR.iterdir():
        matches = re.findall(LIST_KEY.format('(.*?)'), str(filename))
        if matches:
            classes.append(matches[0])
    return classes


@dataclass
class Passage:
    date: str | None = None
    question: str | None = None
    note: float | None = None

@dataclass
class Student:
    name: str
    classe: str
    probability: float
    passages: list[Passage] = field(default_factory=list)
    moyenne: float | None = None


class StudentClass:
    def __init__(self, class_key):
        self.class_key = class_key
        self.load_class_dict()
        self.load_students()
    
    def get_class_list_path(self):
        return CLASS_DIR / LIST_KEY.format(self.class_key)

    def get_class_dict_path(self):
        return CLASS_DIR / JSON_KEY.format(self.class_key)

    def load_class_dict(self):
        if not self.get_class_dict_path().exists():
            self.reset_class_dict()
        try:
            with open(self.get_class_dict_path(), 'r', encoding='utf-8') as f:
                self.current_dict = json.load(f)
        except json.JSONDecodeError:
            print(f"Error decoding JSON from {self.get_class_dict_path()}. Resetting class dictionary.")
            self.reset_class_dict()
    
    def save_class_dict(self):
        with open(self.get_class_dict_path(), 'w', encoding='utf-8') as f:
            json.dump(self.current_dict, f, indent=4, ensure_ascii=False)
    
    def load_students(self):
        self.students = {name: Student(name=name, **data) for name, data in self.current_dict.items()}

    def get_random_student_name(self):
        names = []
        probabilities = []
        for name, student in self.students.items():
            names.append(name)
            probabilities.append(student.probability)
        total_probability = sum(probabilities)
        normalized_probabilities = [p / total_probability for p in probabilities]
        return random.choices(names, weights=normalized_probabilities, k=1)[0]

    def get_random_student(self):
        student_name = self.get_random_student_name()
        return self.students[student_name]

    def update_student_probability(self, student):
        student.probability /= DIV_NUM
        student.moyenne = sum(eval(passage['note']) for passage in student.passages) / len(student.passages) if student.passages else None
        self.save_class_dict()
    
    def reset_class_dict(self):
        print(f"Resetting class dictionary for {self.class_key}")
        self.current_dict = {}
        with open(self.get_class_list_path(), 'r', encoding='utf-8') as f:
            for line in f:
                student_name = line.strip()
                self.current_dict[student_name] = {
                    "classe": self.class_key,
                    "probability": DIV_NUM ** N,
                    "passages": list(),
                    "moyenne": None
                }
        self.save_class_dict()
    
    def make_passage(self):
        passage = Passage()
        passage.date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        passage.question = input('Entrez la question posée : ')
        passage.note = input('Entrez la note obtenue : ')
        return passage

    def save_passage(self, student: Student, passage: Passage):
        student.passages.append(asdict(passage))
        self.update_student_probability(student)
        self.save_class_dict()

    def passage(self, search_duration=3, sleep_time=0.05):
        max_lenght = max(map(lambda student: len(student.name), self.students.values()))
        print("Recherche d'un nom ...")
        for _ in range(int(search_duration/sleep_time)):
            time.sleep(sleep_time)
            print(' '*max_lenght, end='\r')
            print(self.get_random_student().name, end='\r')
        choosen_student = self.get_random_student()
        print(' '*max_lenght, end='\r')
        print('='*max_lenght)
        print(choosen_student.name)
        print('='*max_lenght)

        passage = self.make_passage()
        codezero = input('Enregistrer le passage ? (O/N)')
        while not codezero.strip() == 'O' and not codezero.strip() == 'N':
            print(f'Commande <{codezero}> invalide. Répondre par O ou N :')
            codezero = input()
        if codezero == 'O':
            self.save_passage(choosen_student, passage)

        nextstudent = input('Voulez vous poursuivre ? (O/N)')
        while not nextstudent.strip() == 'O' and not nextstudent.strip() == 'N':
            print(f'Commande <{nextstudent}> invalide. Répondre par O ou N :')
            nextstudent = input()
        
        return nextstudent

if __name__ == '__main__':
    classe = input('Entrez le nom de la classe ')
    while not classe in get_all_classes():
        print(f'La classe <{classe}> n\'existe pas.')
        classe = input('Entrez le nom de la classe ')
    student_class = StudentClass(classe)
    nextstudent = student_class.passage()
    while nextstudent == 'O':
        nextstudent = student_class.passage()