import os

with open("data\\latex\\exercices\\exercice-0715-data.tex", "rb") as f:
    data = f.read()

for i, b in enumerate(data):
    if b == 0x0B:
        print("Trouvé à l'octet :", i)