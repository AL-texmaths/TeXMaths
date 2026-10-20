"""Génère une répartition annuelle de questions flash pour le groupe 6MATHS2."""
import re
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parent.parent
ICS = ROOT / "data/emploi_du_temps/emploi_du_temps.ics"
SEQUENCAGE = ROOT / "data/latex/sequencages/sequencage-Cycle_3_BO_2026-progression-6eme-structure.tex"
LABELS = ROOT / "data/latex/codes_labels/BO_2026-data.txt"
OUTPUT = ROOT / "repartition_qf_6e.txt"
PARIS = ZoneInfo("Europe/Paris")
REVISIONS_JOURS = (3, 10, 30)
JOURS = ("lun", "mar", "mer", "jeu", "ven", "sam", "dim")


def lire_annee_scolaire():
    texte = ICS.read_text(encoding="utf-8")
    debut = re.search(r"^X-CALSTART:(\d{8})T", texte, re.M).group(1)
    fin = re.search(r"^X-CALEND:(\d{8})T", texte, re.M).group(1)
    return date(int(debut[:4]), int(debut[4:6]), int(debut[6:8])), date(
        int(fin[:4]), int(fin[4:6]), int(fin[6:8])
    )


def lire_cours_6g2():
    texte = ICS.read_text(encoding="utf-8").replace("\r\n ", "").replace("\n ", "")
    cours = {}
    for evenement in re.findall(r"BEGIN:VEVENT(.*?)END:VEVENT", texte, re.S):
        resume = re.search(r"SUMMARY[^:]*:(.*)", evenement)
        categories = re.search(r"CATEGORIES:(.*)", evenement)
        debut = re.search(r"DTSTART:(\d{8}T\d{6})Z?", evenement)
        if not resume or "6MATHS2" not in resume.group(1) or not debut:
            continue
        if categories and any(mot in categories.group(1).lower() for mot in ("annul", "abs personnelle")):
            continue
        instant = datetime.strptime(debut.group(1), "%Y%m%dT%H%M%S").replace(tzinfo=timezone.utc)
        local = instant.astimezone(PARIS)
        cours[local] = resume.group(1)
    return sorted(cours)


def lire_chapitres():
    source = SEQUENCAGE.read_text(encoding="utf-8")
    descriptions = defaultdict(list)
    for ligne in LABELS.read_text(encoding="utf-8").splitlines():
        trouve = re.match(r"cycle_3_BO_2026\|:\|(aut|obj)\|:\|([^|]+)\|:\|(.*)", ligne)
        if trouve:
            descriptions[(trouve.group(1), trouve.group(2))].append(trouve.group(3).strip())

    chapitres = []
    for titre, corps in re.findall(r"\\sequence\{([^}]+)\}(.*?)\\endsequence", source, re.S):
        elements = []
        for nature, code in re.findall(r"\\use(aut|obj)\[([^]]+)\]", corps):
            choix = descriptions.get((nature, code), [])
            if not choix:
                raise ValueError(f"Code BO introuvable : {nature} {code}")
            # Certains codes du BO sont réutilisés avec des formulations différentes.
            description = choix[0] if nature == "aut" else choix[-1]
            item = (nature, code, description)
            if item not in elements:
                elements.append(item)
        chapitres.append({"titre": titre, "items": elements})
    if not chapitres:
        raise ValueError("Aucun chapitre lu dans le séquençage")
    return chapitres


def semaine_iso(jour):
    iso = jour.isocalendar()
    return iso.year, iso.week


def repartir(cours, chapitres):
    debut_annee, fin_annee = lire_annee_scolaire()
    premiere_semaine, derniere_semaine = semaine_iso(debut_annee), semaine_iso(fin_annee)
    inclus = [c for c in cours if semaine_iso(c.date()) not in (premiere_semaine, derniere_semaine)]

    semaines = defaultdict(list)
    for c in inclus:
        semaines[semaine_iso(c.date())].append(c)
    semaines_actives = sorted(semaines)
    controles = set()
    for numero, semaine in enumerate(semaines_actives):
        if numero % 2 == 1:
            controles.add(semaines[semaine][-1])
    seances = [c for c in inclus if c not in controles]

    poids = [max(2, len(chapitre["items"])) for chapitre in chapitres]
    poids_total = sum(poids)
    cumul = []
    somme = 0
    for valeur in poids:
        somme += valeur
        cumul.append(somme)

    derniere_vue = {}
    prochaine_revision = {}
    passages = defaultdict(int)
    lignes = []
    for numero, cours_du_jour in enumerate(seances):
        fraction = (numero + 0.5) * poids_total / len(seances)
        chapitre_index = next(i for i, total in enumerate(cumul) if fraction <= total)
        chapitre = chapitres[chapitre_index]
        session_chapitre = sum(1 for ligne in lignes if ligne["chapitre"] == chapitre_index)
        capacite = 1 if numero < 8 else 2 if numero < 24 else 3 if numero < 48 else 4
        choix = []

        def ajouter(item, type_passage):
            nature, code, _ = item
            cle = (nature, code)
            if len(choix) < capacite and cle not in {x[0][:2] for x in choix}:
                choix.append((item, type_passage))
                passages[cle] += 1
                derniere_vue[cle] = cours_du_jour.date()
                if type_passage.startswith("Rappel espacé"):
                    ancien_ecart = prochaine_revision[cle][1]
                    ecart_suivant = REVISIONS_JOURS[min(REVISIONS_JOURS.index(ancien_ecart) + 1, len(REVISIONS_JOURS) - 1)]
                else:
                    ecart_suivant = prochaine_revision.get(cle, (None, REVISIONS_JOURS[0]))[1]
                prochaine_revision[cle] = (cours_du_jour.date() + timedelta(days=ecart_suivant), ecart_suivant)

        if chapitre["items"]:
            item = chapitre["items"][session_chapitre % len(chapitre["items"])]
            cle = item[:2]
            ajouter(item, "Nouveau" if passages[cle] == 0 else "Réactivation du chapitre")

        rappels = []
        for ancien_index in range(chapitre_index):
            for item in chapitres[ancien_index]["items"]:
                cle = item[:2]
                if cle not in derniere_vue:
                    continue
                date_rappel, cible = prochaine_revision[cle]
                if cours_du_jour.date() >= date_rappel:
                    retard = (cours_du_jour.date() - date_rappel).days
                    rappels.append((retard / cible, -derniere_vue[cle].toordinal(), item, f"Rappel espacé ~{cible} j"))
        for _, _, item, type_passage in sorted(rappels, reverse=True):
            ajouter(item, type_passage)

        # Si les rappels ne remplissent pas la séance, poursuivre les objectifs du chapitre.
        for decalage in range(1, len(chapitre["items"])):
            if len(choix) >= capacite:
                break
            item = chapitre["items"][(session_chapitre + decalage) % len(chapitre["items"])]
            cle = item[:2]
            ajouter(item, "Nouveau" if passages[cle] == 0 else "Réactivation du chapitre")

        lignes.append({
            "date": cours_du_jour.date(),
            "heure": cours_du_jour.strftime("%H:%M"),
            "chapitre": chapitre_index,
            "titre": chapitre["titre"],
            "capacite": capacite,
            "questions": choix,
        })

    return lignes, controles, semaines_actives, len(inclus)


def ecrire(lignes, chapitres, controles, semaines, nombre_inclus):
    debut_annee, fin_annee = lire_annee_scolaire()
    premiere, derniere = semaine_iso(debut_annee), semaine_iso(fin_annee)
    sorties = [
        "QUESTIONS FLASH - Répartition annuelle 6e (groupe 6G2 / 6MATHS2)",
        "",
        "Base : créneaux du groupe 6MATHS2 dans data/emploi_du_temps/emploi_du_temps.ics ; ordre des chapitres et compétences repris du séquençage Cycle 3 BO 2026 en 6e.",
        f"Semaines exclues : semaine ISO {premiere[1]} (rentrée) et semaine ISO {derniere[1]} (fin d'année). Contrôles : dernier créneau 6MATHS2 d'une semaine d'enseignement sur deux, à partir de la deuxième semaine active.",
        f"Créneaux 6MATHS2 disponibles après exclusion des semaines de rentrée/fin : {nombre_inclus} ; contrôles retirés : {len(controles)} ; séances planifiées : {len(lignes)}.",
        "Progression : 1 thème/question par séance pendant 8 séances, puis 2 pendant 16, 3 pendant 24, puis 4 au maximum. Les thèmes nouveaux suivent l'ordre du séquençage ; les rappels portent uniquement sur des compétences déjà abordées.",
        "Repères pédagogiques : récupération active sans support, retours espacés indicatifs (~3, 10 et 30 jours), puis entretien ; augmenter la difficulté et varier les représentations. Si une séance saute, déplacer son contenu au prochain cours et ne pas compresser les rappels.",
        "Les codes entre crochets renvoient aux compétences du BO Cycle 3 2026. « Nouveau » indique le premier passage dans ce planning ; les formulations d'objectifs sont des cibles de questions, pas des questions rédigées.",
        "",
    ]
    sorties.append("Créneaux réservés aux contrôles (retirés du planning) :")
    sorties.extend(f"  - {JOURS[c.date().weekday()]} {c:%d/%m/%Y %H:%M}" for c in sorted(controles))
    sorties.append("")
    for numero, ligne in enumerate(lignes, 1):
        jour = ligne["date"]
        sorties.append(f"{numero:>3} | {JOURS[jour.weekday()]} {jour:%d/%m/%Y} {ligne['heure']} | {ligne['titre']} | {len(ligne['questions'])}/{ligne['capacite']} thèmes")
        for (type_competence, code, description), nature in ligne["questions"]:
            sorties.append(f"      - [{nature}] {code}/{type_competence} : {description}")
    OUTPUT.write_text("\n".join(sorties) + "\n", encoding="utf-8")

    assert all(semaine_iso(ligne["date"]) not in (premiere, derniere) for ligne in lignes)
    assert all(1 <= len(ligne["questions"]) <= 4 for ligne in lignes)
    assert all(len({item[0][:2] for item in ligne["questions"]}) == len(ligne["questions"]) for ligne in lignes)
    assert len(lignes) == len({(ligne["date"], ligne["heure"]) for ligne in lignes})
    return sum(len(ligne["questions"]) for ligne in lignes)


def main():
    chapitres = lire_chapitres()
    cours = lire_cours_6g2()
    lignes, controles, semaines, nombre_inclus = repartir(cours, chapitres)
    total = ecrire(lignes, chapitres, controles, semaines, nombre_inclus)
    print(f"{len(chapitres)} chapitres, {len(lignes)} séances, {total} questions flash ; {len(controles)} créneaux de contrôle retirés.")
    print(f"Fichier généré : {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()