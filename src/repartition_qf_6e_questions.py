"""Génère une version du planning 6e avec des questions flash et leur réponse."""
from collections import defaultdict
from pathlib import Path

from src.planning_flash_6e import JOURS, lire_chapitres, lire_cours_6g2, lire_annee_scolaire, repartir, semaine_iso

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "repartition_qf_6e_questions.txt"

# Une question courte et une réponse de référence par compétence du séquençage.
Q = {
    ("obj", "A3aa"): ("Dans 47 305, quelle est la valeur du chiffre 7 ?", "7 000"),
    ("obj", "A3ab"): ("Combien de dixièmes y a-t-il dans 3 unités ?", "30 dixièmes"),
    ("obj", "A3ac"): ("Écrire en chiffres : quatre cent huit mille vingt-six.", "408 026"),
    ("obj", "A3bb"): ("Quel nombre multiplié par 7 donne 5 ?", "5/7"),
    ("obj", "A3bc"): ("Compléter : 8 × ... = 56.", "7"),
    ("obj", "A3aw"): ("Effectuer la division euclidienne de 157 par 12.", "157 = 12 × 13 + 1 ; quotient 13, reste 1"),
    ("obj", "A3ax"): ("On range 53 cartes par paquets de 8. Combien de paquets complets et combien de cartes restantes ?", "6 paquets et 5 cartes"),
    ("obj", "C2aa"): ("AB = 4,6 cm. Quelle est la distance entre A et B ?", "4,6 cm"),
    ("obj", "C2ab"): ("M est le milieu de [AB] et AB = 9 cm. Calculer AM.", "4,5 cm"),
    ("obj", "C2ac"): ("Dans un cercle de centre O, le segment [AB] passe par O et A, B sont sur le cercle. Comment s'appelle [AB] ?", "Un diamètre"),
    ("obj", "C2ad"): ("Un cercle a pour centre O et rayon 3 cm. P est à 2 cm de O. P appartient-il au cercle ou au disque ?", "Au disque, mais pas au cercle"),
    ("obj", "C2ae"): ("Les points M et N sont à 5 cm de O. Quelle propriété ont-ils en commun ?", "OM = ON = 5 cm ; ils appartiennent au cercle de centre O et de rayon 5 cm"),
    ("obj", "A3bd"): ("Sur une droite graduée en quarts, placer 5/4.", "À 1 unité et un quart de 0"),
    ("obj", "A3be"): ("Partager un segment de 3 cm en 6 intervalles égaux. Quelle est la longueur d'un intervalle ?", "0,5 cm"),
    ("obj", "A3bh"): ("Compléter : 3/5 = .../20.", "12"),
    ("obj", "A3bi"): ("Comparer 5/8 et 3/4.", "5/8 < 3/4"),
    ("obj", "A3bj"): ("Ranger dans l'ordre croissant : 5/4 ; 1/2 ; 7/4.", "1/2 < 5/4 < 7/4"),
    ("obj", "C2ai"): ("Un angle mesure 125°. Est-il aigu, droit, obtus ou plat ?", "Obtus"),
    ("obj", "C2aj"): ("[FIGURE : angle AOB mesuré au rapporteur, graduations indiquant 65°] Quelle est la mesure de l'angle AOB ?", "65°"),
    ("obj", "C2ak"): ("Construire un angle ABC de 40° à l'aide du rapporteur.", "Tracer une demi-droite [BA), mesurer 40° en B puis tracer [BC)"),
    ("obj", "C2al"): ("La demi-droite [OM) partage l'angle AOB en deux angles égaux. Comment s'appelle [OM) ?", "La bissectrice de l'angle AOB"),
    ("obj", "C2am"): ("L'angle AOB mesure 76°. [OM) est sa bissectrice. Calculer AOM.", "38°"),
    ("obj", "A3ad"): ("Lequel est un nombre décimal : 7/20 ou 2/3 ?", "7/20 = 0,35 est décimal ; 2/3 ne l'est pas"),
    ("obj", "A3af"): ("Écrire 1,25 en fraction décimale, nombre mixte puis pourcentage.", "125/100 ; 1 + 1/4 ; 125 %"),
    ("obj", "A3ag"): ("Sur une demi-droite graduée de 0 à 2, placer 1,4.", "Entre 1 et 2, à 4 dixièmes après 1"),
    ("obj", "A3ah"): ("[FIGURE : droite graduée de 2 à 3 divisée en 10 intervalles égaux ; point M sur la 7e graduation après 2] Quelle est l'abscisse de M ?", "2,7"),
    ("obj", "A3ai"): ("Comparer 4,08 et 4,8.", "4,08 < 4,8"),
    ("obj", "A3aj"): ("Ranger dans l'ordre croissant : 0,7 ; 0,07 ; 0,77.", "0,07 < 0,7 < 0,77"),
    ("obj", "A3am"): ("Encadrer 6,38 entre deux dixièmes consécutifs.", "6,3 < 6,38 < 6,4"),
    ("obj", "A3ak"): ("Arrondir 8,764 au dixième.", "8,8"),
    ("obj", "A3bf"): ("La fraction 9/4 représente-t-elle un entier, un décimal non entier ou un nombre non décimal ?", "Un décimal non entier : 2,25"),
    ("obj", "C2af"): ("Comment définit-on la médiatrice d'un segment ?", "La droite perpendiculaire au segment passant par son milieu"),
    ("obj", "C2ag"): ("M appartient à la médiatrice de [AB]. Que peut-on affirmer sur MA et MB ?", "MA = MB"),
    ("obj", "C2ah"): ("MA = 4,2 cm et MB = 4,2 cm. Que peut-on dire de M par rapport à [AB] ?", "M appartient à la médiatrice de [AB]"),
    ("obj", "C2at"): ("Pour construire le symétrique A' d'un point A par rapport à une droite (d), quelle relation doit vérifier (d) avec [AA'] ?", "(d) est la médiatrice de [AA']"),
    ("obj", "C2au"): ("Une figure a un périmètre de 12 cm. Quel est le périmètre de son symétrique axial ?", "12 cm ; la symétrie conserve les longueurs"),
    ("obj", "A3ca"): ("Une balance est équilibrée : 3 sachets identiques et 2 cubes pèsent 14 cubes. Combien vaut un sachet ?", "4 cubes"),
    ("obj", "A3cb"): ("Une suite de motifs contient 4, 7, 10 carrés aux rangs 1, 2, 3. Combien au rang 5 ?", "16 carrés ; on ajoute 3 à chaque rang"),
    ("obj", "A3an"): ("Calculer 12,7 + 3,85.", "16,55"),
    ("obj", "A3al"): ("Arrondir π au centième.", "3,14"),
    ("obj", "C2an"): ("Construire un triangle ABC tel que AB = 5 cm, AC = 4 cm et BC = 6 cm.", "Construction au compas et à la règle : les cercles de centres A et B, rayons 4 cm et 6 cm, se coupent en C"),
    ("obj", "C2ao"): ("Un triangle isocèle a un angle au sommet de 40°. Combien mesure chaque angle à la base ?", "70°"),
    ("obj", "C2ap"): ("Quelle est la somme des angles d'un triangle ?", "180°"),
    ("obj", "C2aq"): ("Un triangle a deux angles de 48° et 67°. Calculer le troisième angle.", "65°"),
    ("obj", "C2ar"): ("Que peut-on dire du point d'intersection des médiatrices d'un triangle ?", "Il est à égale distance des trois sommets"),
    ("obj", "C2as"): ("Comment construire le cercle circonscrit à un triangle ?", "Tracer deux médiatrices de côtés ; leur intersection est le centre du cercle passant par les trois sommets"),
    ("obj", "A3au"): ("Calculer 8,4 ÷ 4.", "2,1"),
    ("obj", "A3av"): ("2,4 kg de pommes sont répartis dans 6 sacs identiques. Quelle masse par sac ?", "0,4 kg"),
    ("obj", "A3ao"): ("Calculer 3,7 × 0,01.", "0,037"),
    ("obj", "A3ap"): ("Compléter : 4 500 ÷ 100 = ...", "45 ; diviser par 100 revient à déplacer la virgule de deux rangs vers la gauche"),
    ("obj", "A3aq"): ("Sans poser l'opération, 0,4 × 0,7 est-il supérieur ou inférieur à 0,4 ?", "Inférieur ; 0,4 × 0,7 = 0,28"),
    ("obj", "A3ar"): ("Calculer 1,2 × 0,5.", "0,6"),
    ("obj", "A3as"): ("Le résultat de 19,8 × 4 est-il proche de 8, 80 ou 800 ?", "De 80 ; 19,8 est proche de 20 et 20 × 4 = 80"),
    ("obj", "A3at"): ("Un ruban coûte 2,40 € le mètre. Combien coûtent 3,5 m ?", "8,40 €"),
    ("obj", "D3aa"): ("Pour savoir quel fruit les élèves préfèrent, quelle donnée faut-il recueillir auprès de chacun ?", "Le fruit préféré de chaque élève"),
    ("obj", "D3ac"): ("Créer un tableau d'effectifs pour les réponses : pomme, poire, pomme, banane, pomme.", "Pomme : 3 ; poire : 1 ; banane : 1"),
    ("obj", "D3ab"): ("On mesure trois longueurs : 12 cm, 15 cm et 13 cm. Comment les consigner clairement ?", "Dans un tableau avec une ligne par objet et une colonne « longueur (cm) »"),
    ("obj", "D3ad"): ("Dans un tableau de notes, comment sélectionner les élèves ayant au moins 10/20 ?", "Garder les lignes dont la note est supérieure ou égale à 10"),
    ("obj", "A3ba"): ("Écrire 7/4 sous la forme d'une division puis donner le quotient décimal.", "7 ÷ 4 = 1,75"),
    ("obj", "A3bl"): ("Calculer 2/3 + 1/6.", "5/6"),
    ("obj", "A3bn"): ("Lina mange 1/4 d'une tarte et Sami 2/4. Quelle fraction de la tarte reste-t-il ?", "1/4"),
    ("obj", "A3bo"): ("Inventer une question dont la résolution nécessite de calculer 3/5 de 20.", "Exemple : « 3/5 des 20 élèves viennent à vélo. Combien sont-ils ? » Réponse : 12"),
    ("obj", "A3bk"): ("Calculer et simplifier : 3/4 × 2/3.", "1/2"),
    ("aut", "E3ab"): ("Un rectangle a une longueur 4 fois plus grande que sa largeur. Si sa largeur vaut 3 cm, quelle est sa longueur ?", "12 cm : multiplier par 4"),
    ("obj", "A3bg"): ("Calculer 3/4 de 20 en utilisant une multiplication.", "3/4 × 20 = 15"),
    ("obj", "A3bm"): ("Calculer 2/5 × 10.", "4"),
    ("obj", "E3aa"): ("Dans une situation de proportionnalité, le prix de 1 kg est 3 €. Quel lien entre la masse et le prix ?", "Prix = 3 × masse ; le coefficient de proportionnalité est 3"),
    ("obj", "E3ab"): ("Un taxi facture 4 € de prise en charge puis 2 € par kilomètre. Le prix est-il proportionnel à la distance ?", "Non, car le prix n'est pas nul pour 0 km"),
    ("obj", "E3ac"): ("4 cahiers coûtent 6 €. Combien coûtent 10 cahiers au même tarif ?", "15 € ; un cahier coûte 1,50 €"),
    ("obj", "E3ad"): ("Compléter le tableau de proportionnalité : 2 kg coûtent 5 € ; combien coûtent 6 kg ?", "15 €"),
    ("obj", "E3ae"): ("Sur une carte, 1 cm représente 5 km. Quelle distance réelle représentent 4 cm ?", "20 km"),
    ("aut", "B3aa"): ("Quelle unité obtient-on en divisant 1 km par 1 000 ?", "Le mètre"),
    ("aut", "B3ab"): ("Compléter : 1 m = ... cm.", "100 cm"),
    ("aut", "B3ac"): ("Convertir 2,5 m en centimètres.", "250 cm"),
    ("aut", "B3ae"): ("Un rectangle mesure 8 cm sur 3 cm. Calculer son périmètre.", "22 cm"),
    ("aut", "B3ad"): ("Avec le compas, comment reporter une longueur AB à partir du point C ?", "Ouvrir le compas à AB, piquer en C et marquer D : CD = AB"),
    ("obj", "B3aa"): ("Un disque a un diamètre de 6 cm. Son périmètre est-il proportionnel au diamètre ?", "Oui ; le quotient périmètre/diamètre est π"),
    ("obj", "B3ab"): ("Quelle formule donne le périmètre d'un disque de diamètre d ?", "P = πd"),
    ("obj", "B3ac"): ("Calculer le périmètre exact d'un disque de diamètre 8 cm.", "8π cm"),
    ("obj", "B3ad"): ("Une figure est formée de trois côtés de 4 cm et d'un côté de 7 cm. Calculer son périmètre.", "19 cm"),
    ("obj", "B3ae"): ("Un ruban de 2,4 m est coupé en morceaux de 30 cm. Combien obtient-on de morceaux ?", "8 morceaux"),
    ("obj", "A3bp"): ("Que signifie 25 % ?", "25 sur 100, soit un quart"),
    ("obj", "A3ae"): ("Écrire 12 % sous forme d'une fraction sur 100.", "12/100"),
    ("obj", "A3br"): ("Calculer 10 % de 70 €.", "7 €"),
    ("obj", "A3bq"): ("9 élèves sur 30 sont demi-pensionnaires. Quel pourcentage cela représente-t-il ?", "30 %"),
    ("aut", "B3ba"): ("Deux surfaces couvrent respectivement 8 et 6 carreaux identiques. Laquelle a la plus grande aire ?", "La première ; 8 carreaux contre 6"),
    ("aut", "B3bb"): ("Quelle est l'aire d'un carré de côté 1 cm ?", "1 cm²"),
    ("aut", "B3bc"): ("Une figure couvre 12 carreaux de 1 cm². Quelle est son aire ?", "12 cm²"),
    ("aut", "B3bd"): ("Convertir 2 m² en dm².", "200 dm²"),
    ("aut", "B3be"): ("Combien de cm² dans 1 dm² ?", "100 cm²"),
    ("aut", "B3bf"): ("Combien de dm² dans 1 m² ?", "100 dm²"),
    ("obj", "B3ba"): ("Convertir 3 m² en dm².", "300 dm²"),
    ("obj", "B3bb"): ("Calculer l'aire d'un rectangle de 7 cm sur 4 cm.", "28 cm²"),
    ("obj", "B3bc"): ("Calculer l'aire d'un carré de côté 6 cm.", "36 cm²"),
    ("obj", "D3ba"): ("Une probabilité peut-elle être égale à 1,2 ?", "Non ; elle est comprise entre 0 et 1"),
    ("obj", "D3bb"): ("Un sac contient 3 boules rouges et 1 bleue. Quelle est la probabilité de tirer une boule rouge ?", "3/4"),
    ("obj", "D3bc"): ("Une pièce équilibrée donne 48 fois pile sur 100 lancers. Cette fréquence est-elle proche de la probabilité théorique ?", "Oui ; 48 % est proche de 1/2 = 50 %"),
    ("aut", "B3da"): ("Une horloge digitale indique 14:35:08. Donner l'heure, les minutes et les secondes.", "14 heures, 35 minutes et 8 secondes"),
    ("aut", "B3db"): ("Dessiner les aiguilles indiquant 3 h 30.", "Grande aiguille sur le 6 ; petite aiguille à mi-chemin entre 3 et 4"),
    ("aut", "B3dc"): ("Convertir 2 h 15 min en minutes.", "135 min"),
    ("aut", "B3dd"): ("Combien de jours compte une année non bissextile ?", "365 jours"),
    ("aut", "B3de"): ("Combien de minutes dans trois quarts d'heure ?", "45 minutes"),
    ("aut", "E3aa"): ("Une boîte contient 6 crayons. Combien de crayons dans 4 boîtes identiques ?", "24 crayons ; 4 fois plus signifie multiplier par 4"),
    ("obj", "B3db"): ("Un film commence à 14 h 25 et dure 1 h 40. À quelle heure finit-il ?", "16 h 05"),
    ("obj", "B3da"): ("De 9 h 48 à 10 h 15, quelle durée s'écoule ?", "27 minutes"),
    ("obj", "B3dc"): ("Convertir 3 min 20 s en secondes.", "200 s"),
    ("obj", "B3ca"): ("Quelle unité correspond au volume d'un cube de 1 cm d'arête ?", "1 cm³"),
    ("obj", "B3cb"): ("Un pavé A contient 18 cubes unités et un pavé B en contient 24. Lequel a le plus grand volume ?", "Le pavé B"),
    ("obj", "B3cc"): ("Un pavé droit mesure 4 cm × 3 cm × 2 cm. Calculer son volume.", "24 cm³"),
    ("obj", "C2ba"): ("Un assemblage contient 2 cubes en bas et 1 cube posé sur l'un d'eux. Combien de cubes en tout ?", "3 cubes"),
    ("obj", "F3aa"): ("Dans un programme, quelle instruction vient après « avancer de 3 pas » : « tourner à droite » puis « avancer de 2 pas » ?", "Tourner à droite"),
    ("obj", "F3ab"): ("Exécuter : partir de 0, ajouter 4, puis ajouter 3.", "7"),
    ("obj", "F3ac"): ("Répéter deux fois la séquence « avancer de 3 pas, tourner à droite ». Combien de pas sont parcourus ?", "6 pas"),
    ("obj", "F3ad"): ("Un pion regarde vers le nord. Programmer un chemin de 2 pas vers le nord puis 1 pas vers l'est.", "Avancer 2 pas ; tourner à droite ; avancer 1 pas"),
}


def ecrire():
    chapitres = lire_chapitres()
    attendus = {(nature, code) for chapitre in chapitres for nature, code, _ in chapitre["items"]}
    manquants = sorted(attendus - Q.keys())
    supplementaires = sorted(Q.keys() - attendus)
    if manquants or supplementaires:
        raise ValueError(f"Questions manquantes : {manquants}; entrées hors séquençage : {supplementaires}")

    cours = lire_cours_6g2()
    lignes, controles, _, nombre_inclus = repartir(cours, chapitres)
    debut_annee, fin_annee = lire_annee_scolaire()
    premiere, derniere = semaine_iso(debut_annee), semaine_iso(fin_annee)
    sorties = [
        "QUESTIONS FLASH - 6e (groupe 6G2 / 6MATHS2)",
        "Version avec énoncé concret et réponse attendue ; une ligne de question par thème planifié.",
        "Format : id | niveau/compétence | question flash | réponse de référence.",
        "Les indications [FIGURE] signalent le petit schéma à projeter ou dessiner. Les questions de construction attendent une production graphique.",
        f"Séances planifiées : {len(lignes)} ; questions : {sum(len(l['questions']) for l in lignes)} ; compétences couvertes : {len(attendus)}/{len(attendus)}.",
        f"Semaines exclues : ISO {premiere[1]} (rentrée) et ISO {derniere[1]} (fin d'année). Créneaux contrôle retirés : {len(controles)} sur {nombre_inclus} créneaux de cours admissibles.",
        "",
    ]
    compte = defaultdict(int)
    for numero, ligne in enumerate(lignes, 1):
        jour = ligne["date"]
        sorties.append(f"{numero:03d} | {JOURS[jour.weekday()]} {jour:%d/%m/%Y} {ligne['heure']} | {ligne['titre']}")
        for (nature, code, _), statut in ligne["questions"]:
            cle = (nature, code)
            compte[cle] += 1
            question, reponse = Q[cle]
            sorties.append(f"  QF-{code}-{nature}-{compte[cle]:02d} | {code}/{nature} [{statut}] | {question} | Réponse : {reponse}")
        sorties.append("")
    sorties.extend(["COUVERTURE DU SÉQUENÇAGE", ""])
    for chapitre in chapitres:
        sorties.append(chapitre["titre"])
        for nature, code, _ in chapitre["items"]:
            sorties.append(f"  [x] {code}/{nature} - {compte[(nature, code)]} question(s)")
    OUTPUT.write_text("\n".join(sorties) + "\n", encoding="utf-8")
    assert len(compte) == len(attendus)
    assert all(compte[k] >= 1 for k in attendus)
    assert all(1 <= len(ligne["questions"]) <= 4 for ligne in lignes)
    assert all(semaine_iso(ligne["date"]) not in (premiere, derniere) for ligne in lignes)
    print(f"{len(attendus)} compétences couvertes, {len(lignes)} séances, {sum(compte.values())} questions générées : {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    ecrire()
