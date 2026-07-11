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
PROBA_COEFF = settings["proba_coeff"]

def get_all_classes():
    classes = []
    for filename in CLASS_DIR.iterdir():
        matches = re.findall(LIST_KEY.format('(.*?)', 'txt'), str(filename))
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
    passages: list[Passage] = field(default_factory=list)
    moyenne: float | None = None

    def get_probability_weight(self):
        if self.moyenne is None:
            return 1.0
        else:
            return PROBA_COEFF**len(self.passages)


class StudentClass:
    def __init__(self, class_key):
        self.class_key = class_key
        self.students: dict[str, Student] | None = None
        self.load_students()
    
    def get_class_list_path(self):
        return CLASS_DIR / LIST_KEY.format(self.class_key, 'txt')

    def get_class_dict_path(self):
        return CLASS_DIR / LIST_KEY.format(self.class_key, 'json')

    def load_students(self):
        if not self.get_class_dict_path().exists():
            print(f'Class dictionary does not exist at \n {self.get_class_dict_path()}\n Creating a new one.')
            result = self.reset_student_list()
            if result == 1:
                return
        try:
            with open(self.get_class_dict_path(), 'r', encoding='utf-8') as f:
                students_dict = json.load(f)
                self.students = {name: Student(**data) for name, data in students_dict.items()}
        except json.JSONDecodeError:
            print(f"Error decoding JSON from {self.get_class_dict_path()}. Resetting student_list.")
            self.reset_student_list()
    
    def save_student_list(self):
        with open(self.get_class_dict_path(), 'w', encoding='utf-8') as f:
            json.dump({name: asdict(student) for name, student in self.students.items()}, f, indent=4, ensure_ascii=False)

    def get_random_student_name(self):
        names = []
        probabilities = []
        for name, student in self.students.items():
            names.append(name)
            probabilities.append(student.get_probability_weight())
        total_probability = sum(probabilities)
        normalized_probabilities = [p / total_probability for p in probabilities]
        return random.choices(names, weights=normalized_probabilities, k=1)[0]

    def get_random_student(self):
        student_name = self.get_random_student_name()
        return self.students[student_name]
    
    def reset_student_list(self):
        answer = input(f"Voulez-vous réinitialiser la liste des étudiants pour la classe {self.class_key} ? (O/N) ")
        while answer.strip().upper() not in ['O', 'N']:
            print(f'Commande <{answer}> invalide. Répondre par O ou N :')
            answer = input()
        if answer.strip().upper() == 'N':
            print("Abandon de la réinitialisation de la liste des étudiants.")
            return 1
        print(f"Resetting student list for classe: {self.class_key}")
        self.students = {}
        with open(self.get_class_list_path(), 'r', encoding='utf-8') as f:
            for line in f:
                student = Student(name=line.strip(), classe=self.class_key)
                self.students[student.name] = student
        self.save_student_list()
        return 0
    
    def make_passage(self):
        passage = Passage()
        passage.date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        passage.question = input('Entrez la question posée : ')
        passage.note = input('Entrez la note obtenue : ')
        return passage

    def save_passage(self, student: Student, passage: Passage):
        student.passages.append(asdict(passage))
        self.save_student_list()

    def passage(self, search_duration=3, sleep_time=0.05):
        if not self.students:
            print(f"No students found for class {self.class_key}. Please reset the student list.")
            return 1
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