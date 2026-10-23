"""Génère le planning annuel de questions flash de 5e pour le groupe 5G2."""
import json
import re
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parent.parent
DOSSIER = ROOT / "data/flash_5e"
ICS = ROOT / "data/emploi_du_temps/emploi_du_temps.ics"
PROGRESSION = ROOT / "data/progressions/progression-cycle4-26_27.json"
CODE_INDEX = ROOT / "data/latex/catalogues/code_index.json"
CONFIG = DOSSIER / "config_planning.json"
OUTPUT = ROOT / "repartition_qf_5e.txt"
OUTPUT_JSON = DOSSIER / "planning_flash_5e.json"
PARIS = ZoneInfo("Europe/Paris")
JOURS = ("lun", "mar", "mer", "jeu", "ven", "sam", "dim")


def lire_banque():
    competences = {}
    for chemin in sorted(DOSSIER.glob("banque_*.txt")):
        competence = None
        for numero, ligne in enumerate(chemin.read_text(encoding="utf-8").splitlines(), 1):
            if not ligne.strip() or ligne.startswith("//"):
                continue
            if ligne.startswith("## "):
                champs = [champ.strip() for champ in ligne[3:].split(" | ")]
                code = champs[0]
                competence = {"code": code, "questions": [], "source_file": chemin.name}
                for champ in champs[1:]:
                    cle, separateur, valeur = champ.partition("=")
                    if separateur:
                        competence[cle] = valeur
                competences[code] = competence
                continue
            champs = [champ.strip() for champ in ligne.split(" | ")]
            if competence is None or len(champs) != 4:
                raise ValueError(f"{chemin.name}:{numero}: ligne de question invalide")
            if not champs[0].startswith(competence["code"] + "-"):
                raise ValueError(f"{chemin.name}:{numero}: identifiant incompatible")
            competence["questions"].append({
                "id": champs[0], "temps": int(champs[1]),
                "enonce": champs[2], "reponse": champs[3],
            })
    return competences


def lire_chapitres(competences):
    progressions = json.loads(PROGRESSION.read_text(encoding="utf-8"))
    niveau = next((entree for entree in progressions if entree.get("text") == "5eme"), None)
    if niveau is None:
        raise ValueError("La branche 5eme est introuvable dans la progression cycle 4")

    ordre_codes = {}
    for chapitre in niveau["children"]:
        ordre = []
        for section in chapitre.get("children", []):
            if section.get("text") == "Objectifs d'apprentissage":
                for objectif in section.get("children", []):
                    code = objectif.get("text")
                    if code not in ordre:
                        ordre.append(code)
        ordre_codes[chapitre["text"]] = ordre

    chapitres = []
    for nom in ordre_codes:
        items = [comp for comp in competences.values() if comp.get("chapitre") == nom]
        rangs = {code: index for index, code in enumerate(ordre_codes[nom])}
        items.sort(key=lambda comp: (rangs.get(comp["code"], len(rangs)), comp["code"]))
        if not items:
            raise ValueError(f"Aucune question associée au chapitre : {nom}")
        chapitres.append({"nom": nom, "items": items})

    chapitres_banque = {comp.get("chapitre") for comp in competences.values()}
    manquants = set(ordre_codes) - chapitres_banque
    if manquants:
        raise ValueError(f"Chapitres sans question : {sorted(manquants)}")
    return chapitres


def verifier_automatismes(competences):
    index = json.loads(CODE_INDEX.read_text(encoding="utf-8"))["cycle_4_BO_2026"]["aut"]
    attendus = {code for code in index if re.fullmatch(r"C4[A-Z]1[a-z]+", code)}
    presents = {code for code in competences if code in attendus}
    if attendus != presents:
        raise ValueError(f"Automatismes manquants : {sorted(attendus - presents)}")
    if any(len(competences[code]["questions"]) < 3 for code in attendus):
        raise ValueError("Chaque automatisme officiel doit avoir au moins trois variantes")
    return attendus


def semaine_iso(jour):
    iso = jour.isocalendar()
    return iso.year, iso.week


def lire_seances(config):
    texte = ICS.read_text(encoding="utf-8").replace("\r\n ", "").replace("\n ", "")
    debut_annee = re.search(r"^X-CALSTART:(\d{8})T", texte, re.M).group(1)
    fin_annee = re.search(r"^X-CALEND:(\d{8})T", texte, re.M).group(1)
    debut = datetime.strptime(debut_annee, "%Y%m%d").date()
    fin = datetime.strptime(fin_annee, "%Y%m%d").date()
    premiere_semaine = debut - timedelta(days=debut.weekday())
    derniere_semaine = fin - timedelta(days=fin.weekday())
    semaines_exclues = {semaine_iso(premiere_semaine)}
    for decalage in range(config["semaines_fin_exclues"]):
        semaines_exclues.add(semaine_iso(derniere_semaine - timedelta(days=7 * decalage)))

    slots = {}
    for evenement in re.findall(r"BEGIN:VEVENT(.*?)END:VEVENT", texte, re.S):
        resume = re.search(r"SUMMARY[^:]*:(.*)", evenement)
        categorie = re.search(r"CATEGORIES:(.*)", evenement)
        if not resume or config["filtre_ics"] not in resume.group(1):
            continue
        if categorie and any(mot in categorie.group(1).lower() for mot in ("annul", "abs personnelle")):
            continue
        debut_event = re.search(r"DTSTART:(\d{8}T\d{6})Z?", evenement)
        fin_event = re.search(r"DTEND:(\d{8}T\d{6})Z?", evenement)
        if not debut_event or not fin_event:
            continue
        debut_utc = datetime.strptime(debut_event.group(1), "%Y%m%dT%H%M%S").replace(tzinfo=timezone.utc)
        fin_utc = datetime.strptime(fin_event.group(1), "%Y%m%dT%H%M%S").replace(tzinfo=timezone.utc)
        local = debut_utc.astimezone(PARIS)
        if semaine_iso(local.date()) in semaines_exclues:
            continue
        slots[(local, fin_utc.astimezone(PARIS))] = resume.group(1)

    par_semaine = defaultdict(list)
    for debut_local, fin_local in sorted(slots):
        par_semaine[semaine_iso(debut_local.date())].append((debut_local, fin_local))

    controles = set()
    for index, semaine in enumerate(sorted(par_semaine)):
        if index % 2 == config["controle_semaine_active_parite"]:
            controles.add(par_semaine[semaine][-1])

    restants = [(a, b) for semaine in sorted(par_semaine) for a, b in par_semaine[semaine] if (a, b) not in controles]
    debut_effectif = min(debut_slot for debut_slot, _ in restants).date()
    reunions = choisir_tampons_reunions(restants, debut_effectif, config["reunions_tampon_par_bimestre"])
    reunion_set = set(reunions)
    actifs = [(a, b) for a, b in restants if (a, b) not in reunion_set]
    return actifs, sorted(controles), sorted(reunions), semaines_exclues, len(slots)


def choisir_tampons_reunions(slots, debut_annee, heures_par_bimestre):
    groupes = defaultdict(list)
    for slot in slots:
        debut = slot[0]
        decalage_mois = (debut.year - debut_annee.year) * 12 + debut.month - debut_annee.month
        groupes[decalage_mois // 2].append(slot)
    tampons = []
    for indice in sorted(groupes):
        seances = groupes[indice]
        n = min(heures_par_bimestre, len(seances))
        # Répartir les créneaux de réserve dans le bimestre, sans les présenter comme des réunions confirmées.
        positions = sorted({round((i + 1) * (len(seances) - 1) / (n + 1)) for i in range(n)})
        tampons.extend(seances[position] for position in positions)
    return tampons


def repartition_chapitres(chapitres, nb_seances):
    poids = [max(2, len(chapitre["items"])) for chapitre in chapitres]
    total = sum(poids)
    quotas = [nb_seances * poids_chapitre / total for poids_chapitre in poids]
    allocation = [max(1, int(quota)) for quota in quotas]
    while sum(allocation) > nb_seances:
        candidats = [i for i, valeur in enumerate(allocation) if valeur > 1]
        index = min(candidats, key=lambda i: quotas[i] - allocation[i])
        allocation[index] -= 1
    while sum(allocation) < nb_seances:
        index = max(range(len(quotas)), key=lambda i: quotas[i] - allocation[i])
        allocation[index] += 1
    return [index for index, nombre in enumerate(allocation) for _ in range(nombre)]


def planifier(seances, chapitres, config):
    ordre = repartition_chapitres(chapitres, len(seances))
    gaps = config["ecarts_jours_rappel"]
    derniere_vue = {}
    prochaine_revision = {}
    nb_passages = defaultdict(int)
    programme = []

    for index, (debut, fin) in enumerate(seances):
        chapitre_index = ordre[index]
        chapitre = chapitres[chapitre_index]
        cap = (
            1 if index < config["nb_seances_1_theme"] else
            2 if index < config["nb_seances_1_theme"] + config["nb_seances_2_themes"] else
            3 if index < config["nb_seances_1_theme"] + config["nb_seances_2_themes"] + config["nb_seances_3_themes"] else 4
        )
        choisis = []
        themes = set()
        date_cours = debut.date()

        def ajouter(comp, statut):
            code = comp["code"]
            if len(choisis) >= cap or comp["theme"] in themes or code in {x[0]["code"] for x in choisis}:
                return False
            variante = nb_passages[code] % len(comp["questions"])
            question = comp["questions"][variante]
            choisis.append((comp, question, statut))
            themes.add(comp["theme"])
            nb_passages[code] += 1
            derniere_vue[code] = date_cours
            if statut.startswith("Rappel"):
                dernier_ecart = prochaine_revision[code][1]
                suivant = gaps[min(gaps.index(dernier_ecart) + 1, len(gaps) - 1)]
            else:
                suivant = prochaine_revision.get(code, (None, gaps[0]))[1]
            prochaine_revision[code] = (date_cours + timedelta(days=suivant), suivant)
            return True

        items_chapitre = chapitre["items"]
        nouveaux = [comp for comp in items_chapitre if nb_passages[comp["code"]] == 0]
        if nouveaux:
            ajouter(nouveaux[0], "Nouveau")

        rappels = []
        for code, (date_due, ecart) in prochaine_revision.items():
            if date_cours >= date_due and derniere_vue[code] < date_cours:
                comp = next(item for ch in chapitres for item in ch["items"] if item["code"] == code)
                retard = (date_cours - date_due).days
                rappels.append((retard / ecart, -derniere_vue[code].toordinal(), comp, ecart))
        for _, _, comp, ecart in sorted(rappels, key=lambda rappel: (rappel[0], rappel[1]), reverse=True):
            ajouter(comp, f"Rappel ~{ecart} j")

        for comp in sorted((item for ch in chapitres for item in ch["items"] if nb_passages[item["code"]]),
                           key=lambda item: (derniere_vue[item["code"]], -int(item.get("poids", 1)))):
            if len(choisis) >= cap:
                break
            if date_cours - derniere_vue[comp["code"]] >= timedelta(days=gaps[-1]):
                ajouter(comp, "Entretien")

        for comp in nouveaux[1:]:
            if len(choisis) >= cap:
                break
            ajouter(comp, "Nouveau")

        for comp in items_chapitre:
            if len(choisis) >= cap:
                break
            if nb_passages[comp["code"]] and date_cours - derniere_vue[comp["code"]] >= timedelta(days=3):
                ajouter(comp, "Réactivation du chapitre")

        programme.append({
            "numero": index + 1,
            "date": date_cours.isoformat(),
            "heure": debut.strftime("%H:%M"),
            "fin": fin.strftime("%H:%M"),
            "chapitre": chapitre["nom"],
            "capacite": cap,
            "questions": [{"code": comp["code"], "id": question["id"], "statut": statut,
                           "enonce": question["enonce"], "reponse": question["reponse"]}
                          for comp, question, statut in choisis],
        })
    return programme


def ecrire(programme, controles, reunions, nb_slots_bruts, nb_reunions_estime):
    sorties = [
        "QUESTIONS FLASH - Répartition annuelle 5e (groupe 5G2 / 5MATHS2)",
        "",
        "Sources : emploi_du_temps.ics ; data/progressions/progression-cycle4-26_27.json ; automatismes Cycle 4 BO 2026 dans data/latex/catalogues/code_index.json.",
        f"Périmètre : première semaine exclue, deuxième semaine incluse, deux dernières semaines exclues. Contrôle : un créneau hebdomadaire sur deux, retiré à titre d'estimation.",
        f"Créneaux admissibles avant pertes : {nb_slots_bruts} ; contrôles estimés : {len(controles)} ; marge de réunions : {len(reunions)} h ({nb_reunions_estime} h/bimestre) ; séances flash planifiées : {len(programme)}.",
        "La marge de réunions est une réserve de planification répartie dans chaque bimestre, pas une liste de réunions confirmées. Si une séance saute, déplacer son contenu au prochain cours sans comprimer les rappels.",
        "Pratique de récupération : tenter sans cours ni notes, puis correction immédiate. Rappels espacés indicatifs à environ 3, 10 puis 30 jours ; thèmes alternés sans répéter le même thème dans une séance.",
        "Charge : 1 question pendant 8 séances, 2 pendant 16, 3 pendant 24, puis 4 au maximum. Les codes C4[A-Z]1xx correspondent aux automatismes officiels de 5e ; les codes X5E complètent les contenus de chapitre.",
        "Les questions sont courtes ; [FIGURE], [TABLEAU] ou [GRAPHIQUE] indique le support à préparer.",
        "",
        "Contrôles estimés (créneaux retirés) :",
    ]
    sorties.extend(f"  - {JOURS[a.date().weekday()]} {a:%d/%m/%Y %H:%M}" for a, _ in controles)
    sorties += ["", "Réunions : créneaux réservés en marge (dates indicatives) :"]
    sorties.extend(f"  - {JOURS[a.date().weekday()]} {a:%d/%m/%Y %H:%M}" for a, _ in reunions)
    sorties.append("")
    for seance in programme:
        sorties.append(f"{seance['numero']:03d} | {JOURS[date.fromisoformat(seance['date']).weekday()]} {date.fromisoformat(seance['date']):%d/%m/%Y} {seance['heure']} | {seance['chapitre']} | {len(seance['questions'])}/{seance['capacite']} questions")
        for q in seance["questions"]:
            sorties.append(f"  {q['id']} [{q['statut']}] | {q['enonce']} | Réponse : {q['reponse']}")
        sorties.append("")
    OUTPUT.write_text("\n".join(sorties) + "\n", encoding="utf-8")
    OUTPUT_JSON.write_text(json.dumps({"seances": programme}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    competences = lire_banque()
    attendus = verifier_automatismes(competences)
    chapitres = lire_chapitres(competences)
    assert len(attendus) == 49

    seances, controles, reunions, _, nb_slots_bruts = lire_seances(config)
    if len(seances) < len(chapitres):
        raise ValueError("Il n'y a pas assez de créneaux pour attribuer chaque chapitre")
    programme = planifier(seances, chapitres, config)
    ecrire(programme, controles, reunions, nb_slots_bruts, config["reunions_tampon_par_bimestre"])

    utilisees = {q["code"] for seance in programme for q in seance["questions"]}
    non_introduites = set(competences) - utilisees
    couverture_chapitres = {s["chapitre"] for s in programme}
    if non_introduites:
        raise ValueError(f"Compétences jamais planifiées : {sorted(non_introduites)}")
    if couverture_chapitres != {chapitre["nom"] for chapitre in chapitres}:
        raise ValueError("Au moins un chapitre n'apparaît pas dans le planning")
    print(f"{len(attendus)} automatismes officiels ; {len(competences) - len(attendus)} compléments ; {len(programme)} séances effectives ; {sum(len(s['questions']) for s in programme)} questions planifiées.")
    print(f"Contrôles retirés : {len(controles)} ; tampon réunions : {len(reunions)} h.")
    print(f"Fichiers : {OUTPUT.relative_to(ROOT)} et {OUTPUT_JSON.relative_to(ROOT)}")


if __name__ == "__main__":
    main()