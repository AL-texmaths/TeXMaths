# Pictogrammes proposés pour les verbes du glossaire

## Méthode

- Source : *The Comprehensive LaTeX Symbol List* (`symbols-a4.pdf`, CTAN), texte extrait avec `pdftotext`.
- Le PDF contient 1664 icônes du paquet **lucide-icons** (`\lucideicon{nom}`), déjà utilisé dans le glossaire (`drafting-compass`, `calculator`, `search`…). Les propositions se limitent à ce jeu pour garder un style cohérent (traits fins, monochrome) et une seule macro. Les noms ont été vérifiés dans la liste extraite du PDF.
- Critères : l'icône doit évoquer **l'action** (outil, geste, résultat) et rester lisible en petite taille. Les verbes abstraits (Justifier, Interpréter…) reçoivent une métaphore (bulle de dialogue, loupe, ampoule…) ; les synonymes renvoyant à un autre verbe (« Voir **Justifier** ») reprennent la même icône pour que l'élève fasse le lien.
- Format dans `glossaire.yaml` : `pictogramme: "\\lucideicon{nom}"`.
- ✅ = déjà présent dans le YAML ; ⚠️ = choix peu évident, à valider.

## Propositions

| Verbe | Pictogramme principal | Alternatives | Justification |
|---|---|---|---|
| Ajouter | `plus` | `circle-plus` | Symbole $+$ |
| Soustraire | `minus` | `circle-minus` | Symbole $-$ |
| Multiplier | `x` | `asterisk` | Croix = $\times$ |
| Diviser | `divide` | `circle-divide`, `square-divide` | Symbole $\div$ |
| Appliquer (un programme de calcul) | `play` | `workflow`, `circle-play` | Exécuter pas à pas |
| Argumenter | `message-square-quote` | `message-circle-more`, `speech` | Prise de parole |
| Arrondir (un nombre) | `equal-approximately` | `weight-tilde` | $\simeq$ (remplace le `\simeq` actuel dans le YAML) |
| Associer | `link` | `git-compare-arrows`, `waypoints` | Relier deux éléments |
| Calculer ✅ | `calculator` | `square-sigma` | Calculatrice |
| Classer ✅ | `arrow-down-0-1` | `list-ordered` | Ordre croissant |
| Coder (une figure) | `tally-2` | `tags`, `square-equal` | Marques de codage |
| Comparer (deux nombres) | `scale` | `git-compare`, `arrow-left-right` | Balance / mise en regard |
| Construire ✅ | `drafting-compass` | `pencil-ruler`, `ruler` | Compas |
| Convertir | `arrow-right-left` | `refresh-cw`, `replace` | Passage d'une unité à l'autre |
| Décomposer (un nombre) | `split` | `ungroup`, `table-cells-split` | Séparer en morceaux |
| Décrire une figure | `text-align-start` | `file-text`, `shapes` | Écrire des lignes de texte (`shapes` pour le côté figure) |
| Déduire | `corner-down-right` | `arrow-big-down`, `git-merge` | Conséquence de ce qui précède |
| Démontrer (par le calcul) | `square-sigma` | `file-check`, `badge-check` | Calcul menant à une preuve |
| Détailler | `list-tree` | `list`, `zoom-in` | Étapes successives |
| Déterminer | `target` | `crosshair`, `locate-fixed` | Viser la valeur exacte |
| Développer un produit | `expand` | `unfold-horizontal`, `maximize-2` | Ouvrir / étaler |
| Donner | `hand-helping` | `message-square-text`, `pencil-line` | Fournir une réponse (⚠️) |
| Effectuer (une opération) | `calculator` | `square-function`, `circle-equal` | Même idée que Calculer |
| Encadrer | `brackets` | `square-dashed`, `between-horizontal-start` | Valeur entre deux bornes |
| Évaluer | `gauge` | `circle-gauge`, `scale` | Mesurer la valeur obtenue |
| Expliquer | `message-circle-question-mark` | `message-square-text`, `megaphone` | Mettre en mots |
| Exprimer ($a$ en fonction de $x$) ✅ | `circle-equal` | `variable`, `square-function` | Égalité littérale |
| Exprimer (sous la forme d'une expression numérique) | `square-equal` | `parentheses`, `equal` | Une seule expression |
| Factoriser une somme | `parentheses` | `group`, `combine` | Mettre en facteur (parenthèses) |
| Indiquer | `pointer` | `arrow-big-right` | Montrer du doigt |
| Intercaler | `between-horizontal-start` | `between-vertical-start`, `arrow-left-right` | Insérer entre deux éléments |
| Interpréter | `lightbulb` | `glasses`, `languages` | Comprendre le sens |
| Justifier | `message-square-text` | `scroll-text`, `badge-question-mark` | Donner une raison écrite |
| Mesurer ✅ | `ruler-dimension-line` | `ruler`, `diameter` | Règle graduée |
| Montrer | `eye` | `presentation`, `badge-check` | Voir *Démontrer* ; aussi `file-check` pour rester proche |
| Nommer un objet géométrique | `tag` | `case-upper`, `type` | Étiquette / lettre majuscule |
| Noter | `pencil-line` | `notebook-pen`, `signature` | Écrire une notation |
| Ordonner | `arrow-up-0-1` | `arrow-down-1-0`, `list-ordered` | Même famille que Classer |
| Placer (un point) | `map-pin` | `crosshair`, `locate` | Poser un repère |
| Préciser | `zoom-in` | `text-search`, `search-check` | Affiner la réponse |
| Prouver | `badge-check` | `shield-check`, `circle-check` | Voir *Démontrer* |
| Réaliser (un programme) | `play` | `circle-play`, `pencil-ruler` | Suivre les instructions |
| Rédiger (un programme) | `file-pen` | `square-terminal`, `list-todo` | Écrire des instructions |
| Réduire (une expression littérale) | `shrink` | `minimize-2`, `fold-horizontal` | Raccourcir l'expression |
| Remplir | `table-properties` | `clipboard-pen-line`, `square-pen` | Compléter un tableau |
| Représenter (des données) | `chart-column` | `table`, `chart-pie` | Graphique / tableau |
| Représenter (graphiquement une fonction) | `chart-line` | `chart-spline`, `axis-3d` | Courbe |
| Représenter (un objet géométrique) | `slash` | `pencil-ruler`, `triangle` | Voir *Tracer* |
| Résoudre (un triangle) | `triangle` | `triangle-right`, `ruler-dimension-line` | Triangle à compléter (⚠️ `triangle-right` si triangle rectangle) |
| Résoudre (une équation) | `equal` | `square-equal`, `variable` | Chercher l'inconnue (⚠️) |
| Simplifier une expression littérale | `eraser` | `delete`, `minimize-2` | Supprimer des symboles |
| Simplifier une fraction | `ratio` | `percent`, `divide` | Fraction / rapport |
| Tester (une égalité) | `equal-not` | `circle-check`, `circle-x` | Vrai ou faux |
| Tracer ✅ | `slash` | `pencil`, `pen-line` | Trait ; `pencil` est plus parlant pour un élève |
| Tracer (à main levée) | `pencil` | `pen-tool`, `spline-pointer` | Crayon seul, sans outil |
| Traduire (en notation mathématiques) | `languages` | `pi`, `sigma` | Changement de langage (`pi` pour un côté mathématique) |
| Traduire (un programme de calcul) | `languages` | `variable`, `square-function` | Même icône, ou `variable` pour « lettre » |
| Trouver ✅ | `search` | `telescope` | Loupe |

## Remarques et choix à arbitrer

1. **Cohérence par famille** : `play` (Appliquer / Réaliser), `languages` (Traduire ×2), `arrow-*-0-1` (Classer / Ordonner), `badge-check` (Prouver) et `eye` (Montrer) permettent de regrouper visuellement les synonymes.
2. **Tracer vs Tracer (à main levée)** : `slash` (trait) est déjà dans le YAML pour *Tracer* ; je propose `pencil` pour la main levée afin de bien les distinguer de `drafting-compass` (*Construire*).
3. **Verbes difficiles à représenter** (Donner, Déterminer, Interpréter, Résoudre une équation) : les icônes sont des métaphores ; il vaut mieux les tester auprès d'élèves avant de les figer.
4. **Doublons volontaires** : *Effectuer* et *Calculer* partagent `calculator`.
5. **Arrondir** : remplacer `\simeq` par `"\\lucideicon{equal-approximately}"` homogénéise le style avec les autres pictogrammes.
6. **Lisibilité** : les icônes lucide sont très détaillées ; vérifier le rendu à la taille réelle dans le glossaire (en particulier `message-square-quote`, `table-properties`, `list-tree`).
