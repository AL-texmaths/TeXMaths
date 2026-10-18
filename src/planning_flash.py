"""Planifie les questions flash 3e (banque data/flash_3e) sur les séances d'un groupe de l'emploi du temps.

Usage : python -m src.planning_flash [--depuis AAAA-MM-JJ] [--saute AAAA-MM-JJ[THH:MM] ...]
Avec --depuis, les séances antérieures du planning JSON existant sont conservées (séances déjà faites).
Avec --saute, la séance (ou le jour entier) est retirée définitivement via config_planning.json.
"""
import argparse
import json
import re
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

RACINE = Path(__file__).resolve().parent.parent
DOSSIER = RACINE / "data" / "flash_3e"
ICS = RACINE / "data" / "emploi_du_temps" / "emploi_du_temps.ics"
CONFIG = DOSSIER / "config_planning.json"
PLANNING_JSON = DOSSIER / "planning_flash_3e.json"
PLANNING_TXT = RACINE / "repartition_questions_flash_v4.txt"
PARIS = ZoneInfo("Europe/Paris")
JOURS = ["lun", "mar", "mer", "jeu", "ven", "sam", "dim"]


def lire_banque():
    micros = {}
    for fichier in sorted(DOSSIER.glob("banque_*.txt")):
        rang, cur = 0, None
        for num, ligne in enumerate(fichier.read_text(encoding="utf-8").splitlines(), 1):
            if not ligne.strip() or ligne.startswith("//"):
                continue
            if ligne.startswith("## "):
                champs = [c.strip() for c in ligne[3:].split(" | ")]
                cur = {"code": champs[0], "questions": [], "domaine": fichier.stem, "rang": rang}
                for c in champs[1:]:
                    cle, _, val = c.partition("=")
                    cur[cle] = val
                cur["poids"] = int(cur["poids"])
                micros[cur["code"]] = cur
                rang += 1
                continue
            champs = [c.strip() for c in ligne.split(" | ")]
            if cur is None or len(champs) not in (4, 5):
                raise ValueError(f"{fichier.name}:{num} : ligne invalide")
            q = {"id": champs[0], "temps": int(champs[1]), "enonce": champs[2], "reponse": champs[3]}
            if len(champs) == 5:
                q["consigne"] = champs[4]
            if not q["id"].startswith(cur["code"] + "-"):
                raise ValueError(f"{fichier.name}:{num} : id {q['id']} incohérent avec {cur['code']}")
            cur["questions"].append(q)
    for code, m in micros.items():
        if len(m["questions"]) < 3:
            raise ValueError(f"{code} : moins de 3 questions")
    return micros


def lire_seances(filtre):
    texte = ICS.read_text(encoding="utf-8").replace("\r\n ", "").replace("\n ", "")
    seances = set()
    for ev in re.findall(r"BEGIN:VEVENT(.*?)END:VEVENT", texte, re.S):
        resume = re.search(r"SUMMARY[^:]*:(.*)", ev).group(1)
        categorie = re.search(r"CATEGORIES:(.*)", ev).group(1).lower()
        if filtre not in resume or "annul" in categorie or "abs" in categorie:
            continue
        debut = re.search(r"DTSTART:(\d{8}T\d{6})", ev).group(1)
        seances.add(datetime.strptime(debut, "%Y%m%dT%H%M%S").replace(tzinfo=timezone.utc).astimezone(PARIS))
    return sorted(seances)


def correspond(debut, cibles):
    cle = debut.strftime("%Y-%m-%dT%H:%M")
    return any(cle.startswith(c) for c in cibles)


def retirer_controles(seances, cfg):
    """Retire une séance toutes les deux semaines (contrôle), sauf si des dates explicites sont données."""
    c = cfg["controle"]
    if "dates" in c:
        retirees = [s for s in seances if correspond(s, c["dates"])]
    else:
        lundi0 = seances[0].date() - timedelta(days=seances[0].weekday())
        par_semaine = {}
        for s in seances:
            par_semaine.setdefault((s.date() - lundi0).days // 7, []).append(s)
        retirees = [(l[-1] if c["seance"] == "derniere" else l[0])
                    for k, l in par_semaine.items() if k % 2 == c["parite_semaine"]]
    return [s for s in seances if s not in retirees], retirees


def planifier(seances, micros, cfg, gele):
    ecarts = cfg["ecarts_jours"]
    deblocage = {k: date.fromisoformat(v) for k, v in cfg["deblocages"].items()}
    domaines = {d: i for i, d in enumerate(sorted({m["domaine"] for m in micros.values()}))}
    etat = {c: {"n": 0, "dernier": None} for c in micros}
    for ligne in gele:
        for q in ligne["questions"]:
            etat[q["micro"]]["n"] += 1
            etat[q["micro"]]["dernier"] = date.fromisoformat(ligne["date"])
    total = len(gele) + len(seances)
    plan = list(gele)

    for i, debut in enumerate(seances, start=len(gele)):
        jour = debut.date()
        bilan = i >= total - cfg["nb_bilans"]
        if bilan:
            cap = cfg["capacite_bilan"]
        elif i < cfg["nb_seances_debut"]:
            cap = cfg["capacite_debut"]
        else:
            cap = cfg["capacite"] if i < cfg["nb_seances_plein"] else cfg["capacite_plein"]

        def debloque(c):
            return jour >= deblocage.get(micros[c]["chapitre"], date.min)

        def precedent_vu(c):
            if c[3] == "a":
                return True
            e = etat.get(c[:3] + chr(ord(c[3]) - 1))
            return e is None or (e["n"] > 0 and (jour - e["dernier"]).days >= cfg["ecart_intro_theme"])

        choix, themes = [], set()

        def ajouter(c, type_):
            if len(choix) < cap and c[:3] not in themes and c not in [x[0] for x in choix]:
                choix.append((c, type_))
                themes.add(c[:3])

        nouveaux = sorted((c for c in micros if etat[c]["n"] == 0 and debloque(c) and precedent_vu(c)),
                          key=lambda c: (micros[c]["rang"] + 8 * (3 - micros[c]["poids"]), domaines[micros[c]["domaine"]]))
        if bilan:
            cands = []
            for c, e in etat.items():
                if not debloque(c):
                    continue
                if e["n"] == 0:
                    cands.append((10**6, c, "Nouveau"))
                elif (jour - e["dernier"]).days >= 3:
                    cands.append((micros[c]["poids"] * (jour - e["dernier"]).days, c, "Bilan"))
            for _, c, t in sorted(cands, reverse=True):
                ajouter(c, t)
        else:
            arriere = sum(1 for c in micros if etat[c]["n"] == 0 and debloque(c))
            max_nouveaux = min(3 if arriere > 12 else 2 if arriere > 4 else 1, max(1, cap - 1))
            cands = [(1.3, c, "Nouveau") for c in nouveaux]
            for c, e in etat.items():
                if 0 < e["n"] <= len(ecarts):
                    echeance = e["dernier"] + timedelta(days=ecarts[e["n"] - 1])
                    if jour >= echeance:
                        cands.append((1 + (jour - echeance).days / ecarts[e["n"] - 1], c, f"Rappel {e['n']}"))
            nb_nouveaux = 0
            for _, c, t in sorted(cands, key=lambda x: -x[0]):
                if t == "Nouveau":
                    if nb_nouveaux >= max_nouveaux:
                        continue
                    nb_nouveaux += 1
                ajouter(c, t)
            for c in nouveaux:
                ajouter(c, "Nouveau")
            vus = sorted((c for c, e in etat.items()
                          if e["n"] > len(ecarts) and (jour - e["dernier"]).days >= cfg["ecart_entretien"]),
                         key=lambda c: -micros[c]["poids"] * (jour - etat[c]["dernier"]).days)
            for c in vus:
                ajouter(c, "Entretien")

        questions = []
        for c, t in choix:
            m, e = micros[c], etat[c]
            questions.append({"micro": c, "id": m["questions"][e["n"] % len(m["questions"])]["id"], "type": t})
            e["n"] += 1
            e["dernier"] = jour
        plan.append({"n": i + 1, "date": jour.isoformat(), "heure": debut.strftime("%H:%M"), "questions": questions})
    return plan


def ecrire_txt(plan, micros, cfg, nb_total, controles, sautees):
    out = [
        "QUESTIONS FLASH (automatismes) - Planning 3e, version 4 (généré par src/planning_flash.py)",
        "",
        f"Séances 5G2 retenues : {len(plan)} ; contrôles retirés : {len(controles)} ; séances sautées : {len(sautees)} (sur {nb_total}).",
        "Banque : data/flash_3e/banque_*.txt (une micro-compétence = 3 variantes de questions LaTeX).",
        "Réglages (contrôles, séances sautées, dates de déblocage) : data/flash_3e/config_planning.json.",
        "Légende : Nouveau = première rencontre ; Rappel n = retour espacé (+3 puis +12 jours) ; Entretien = ancien item remis en jeu après 30 jours ; Bilan = révision DNB.",
        "",
    ]
    for ligne in plan:
        d = date.fromisoformat(ligne["date"])
        out.append(f"{ligne['n']:>3} | {JOURS[d.weekday()]} {d:%d/%m/%Y} {ligne['heure']} | {len(ligne['questions'])} questions")
        for q in ligne["questions"]:
            out.append(f"      - {q['id']} [{q['type']}] {micros[q['micro']]['titre']}")
    out += ["", "Passages par micro-compétence :"]
    compte = {c: 0 for c in micros}
    for ligne in plan:
        for q in ligne["questions"]:
            compte[q["micro"]] += 1
    for c, n in compte.items():
        out.append(f"  {c} : {n} passage(s) - {micros[c]['titre']}")
    PLANNING_TXT.write_text("\n".join(out) + "\n", encoding="utf-8")
    return compte


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--depuis", help="conserver les séances du planning JSON antérieures à cette date")
    ap.add_argument("--saute", nargs="*", default=[], help="séances ou jours à retirer (AAAA-MM-JJ ou AAAA-MM-JJTHH:MM)")
    args = ap.parse_args()

    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    if args.saute:
        cfg["seances_sautees"] = sorted(set(cfg["seances_sautees"]) | set(args.saute))
        CONFIG.write_text(json.dumps(cfg, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    micros = lire_banque()
    toutes = lire_seances(cfg["filtre_ics"])
    restantes, controles = retirer_controles(toutes, cfg)
    sautees = [s for s in restantes if correspond(s, cfg["seances_sautees"])]
    restantes = [s for s in restantes if s not in sautees]

    gele = []
    if args.depuis:
        gele = [l for l in json.loads(PLANNING_JSON.read_text(encoding="utf-8"))["seances"] if l["date"] < args.depuis]
        restantes = [s for s in restantes if s.date().isoformat() >= args.depuis]

    plan = planifier(restantes, micros, cfg, gele)
    PLANNING_JSON.write_text(json.dumps({"seances": plan}, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    compte = ecrire_txt(plan, micros, cfg, len(toutes), controles, sautees)
    faibles = [c for c, n in compte.items() if n < 3]
    print(f"{len(plan)} séances, {sum(compte.values())} questions, {len(micros)} micro-compétences ; < 3 passages : {faibles}")


if __name__ == "__main__":
    main()
