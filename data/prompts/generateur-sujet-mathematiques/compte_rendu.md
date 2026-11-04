# Compte rendu des vérifications (exemple 0938 / 0700 / 0615)

## Structure retenue

| Exercice | Source | Points | Structure |
| --- | --- | --- | --- |
| 1 | 0938 | 6 | QCM en `tabularx` : aucun `enumerate`, donc pas de `parts` |
| 2 | 0700 | 6 | `parts` pour « Partie 1 » / « Partie 2 » (convention de l'exercice 3 du modèle), `subparts` pour les deux `enumerate` ; `itemize`, figures TikZ, Scratch et `tblr` inchangés |
| 3 | 0615 | 6 | `enumerate` de 4 questions indépendantes → `parts`, intitulés « Question n » dans un `\begingroup…\endgroup`, `\answerspace\answerspacelg` |

Répartition indicative si un barème détaillé est souhaité (non codée, pour éviter la double
comptabilisation) : exercice 1 : 4 × 1,5 ; exercice 2 : 4 × 0,75 + 2 × 1,5 (Parties 1 et 2) ;
exercice 3 : 4 × 1,5.

## Fidélité

`python3 verifier_fidelite.py exemple_entree.md exemple_sujet.tex` : exercices 1, 2 et 3 identiques.
Test négatif (« fopis » changé en « fois » dans le `.tex`) : différence détectée.
La faute « fopis » et le texte « sans l'énoncé » de la source sont conservés.

## Structure et barème

- Un seul `\begin{questions}`, trois `\question[6]`, environnements équilibrés.
- Présentation 2 + 6 + 6 + 6 = 20 (`\totpoints{20}`, `\presentationpoints{2}`).
- Le tableau de points généré par `commun.cls` indique « Total 18 » : il ne somme que les
  `\question`, la présentation est affichée à part (comportement identique aux devoirs communs).

## Compilation

`latexmk -lualatex` : succès, 4 pages, aucune erreur. pdfLaTeX échoue (conflit `inputenc` dans la
classe) : utiliser LuaLaTeX. Un seul avertissement `Overfull \hbox` (≈ 30 pt) pour le tableau
`tblr` des scripts de l'exercice 2, dont le code est celui de la source et n'a pas été modifié.

## Points d'attention

- Les enoncés mentionnent une « ANNEXE » (exercice 2) qui n'existe pas dans ce sujet ; conservée telle quelle.
- Dans le sujet de référence, `\degres` est défini en préambule ; non nécessaire ici (non utilisé).
- Les paramètres `\jour` et `\duree` (Décembre 2026, 2h) sont repris du modèle : à adapter.
