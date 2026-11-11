# Idées d'amélioration

## Python

### Global

- Vérifier la possibilité d'utiliser nativement Linux pour remplacer SumatraPDF (commande `lp`).
- Vérifier la possibilité de connecter Linux à une imprimante via Wi-Fi.

### Assistant

- API : clarifier le lien entre progression et BO.
  - Une progression peut-elle utiliser des items venant de plusieurs catalogues ?
  - Sinon, ajouter un attribut « catalogue » à chaque progression et empêcher l'ajout d'un item dont le catalogue ne correspond pas.
- Se renseigner sur une manière professionnelle de créer des liens de dépendance verticales entre les items, ainsi qu'une manière de les visualiser.
- Déléguer les responsabilités du script assistant de progression.
- Trouver un moyen de savoir si un exercice a été traité en classe cette année-là.

## Java / HTML

### Exerciseur

- Feedback rapide.
- Indices en cas d'échecs répétés.
- Lien vers la leçon, un exemple, etc.
- Système de niveaux : la réussite de plusieurs exercices d'affilée permet le passage au niveau suivant.
- Le thème VS Code Dark a des tailles de box plus élevées (ancien bug), mais les autres thèmes n'ont pas cette correction.

### Assistant de progression

- Que se passe-t-il si l'on ajoute un item dans le BO ? La progression sauvegardée devient obsolète puisque le code de chaque item change.
- Il faudrait que la progression sauvegardée soit indépendante du code (A1ab, B3ca, etc.) de chaque item.

### Genially

## LaTeX

- Mettre des GIF/animations dans les questions flash ?
- Revoir la macro `\videoManim` de `texmaths-path`.
- Revoir le code avec LuaLaTeX/Expl3 pour l'améliorer.

### Mise à jour de la base de données (fichiers LaTeX)

- Utiliser `\mathpoints` (Maj+MP) et `\currentcolor` (CC).
- Insérer les espaces de réponse dans les exercices.
- Supprimer les overfull/underfull des exercices (voir le log).
- Écrire les métadonnées.

## Pédagogique

- Activité destinée à faire assimiler la notion de surface :
  - Pour calculer l'aire, préparer des petits carreaux en carton. L'élève devra mesurer différentes surfaces à l'aide de ces petits carreaux.
  - Chaque groupe a différents petits carreaux.
  - En classe entière, constater la différence et en détecter la cause.
  - La solution est donc de se mettre d'accord sur une unité d'aire en particulier.
  - Le centimètre carré.
  - Demander s'il existe d'autres unités d'aire connues (cm, dm, ...).
  - Qu'est-ce qui est commun à ces unités ? Réponse : le mètre.
  - Le mètre carré est l'unité de référence. Selon les cas, on choisit différentes unités multiples ou sous-multiples de l'unité de référence.
- Animation qui permet de créer des images mentales pour faciliter la lecture graphique :
  - Problèmes :
    - On connaît l'image, on cherche l'antécédent.
    - On veut l'image de 0 ou l'antécédent de 0.
  - Animation (GIF) qui cache les axes non nécessaires au moment des lectures.
  - Une vidéo Manim serait peut-être plus intéressante.
  - GIF issu des vidéos Manim ?
- Exercice de trigonométrie : démontrer que les angles aigus d'un triangle rectangle isocèle valent 45 degrés avec la tangente.
- Réfléchir à des chapitres centrés sur une action plutôt que sur un thème (« calculer », « représenter les nombres », ...).
- Chaque exercice travaille une compétence. Après correction, l'élève doit s'auto-évaluer. Au moment de réviser, il pourra s'appuyer sur ses autoévaluations.
- Réfléchir a fournir des supports pour les questions flash. Trop de supports à coller font perdre du temps mais on peut imaginer une feuille a4 contenant *tout les supports nécessaires aux question flash* du chapitre. 
- Dans les questions flash, laisser la question précédente en plus petit
afin de permettre au éléves en retard de quand même répondre.