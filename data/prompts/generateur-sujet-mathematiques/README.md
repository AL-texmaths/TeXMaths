# Générateur de sujet de mathématiques

Agent Copilot : `.github/agents/generateur-sujet-mathematiques.agent.md`
Conventions permanentes : `.github/instructions/latex-mathematiques.instructions.md`

## Utilisation

1. Préparer un Markdown sur le modèle de [exemple_entree.md](exemple_entree.md) : métadonnées, puis
   un `## Exercice n` par exercice, avec `Points` et le LaTeX dans un bloc ```latex.
2. Dans le chat Copilot, choisir l'agent `generateur-sujet-mathematiques` et demander par exemple :
   « Génère le sujet à partir de data/prompts/mon_sujet.md ».
3. Récupérer le `.tex` produit, puis compiler : `latexmk -lualatex fichier.tex`.
4. Contrôle de fidélité à tout moment :
   `python3 verifier_fidelite.py source.md sujet.tex`.

## Fichiers

| Fichier | Rôle |
| --- | --- |
| [exemple_entree.md](exemple_entree.md) | Markdown d'entrée (exercices 0938, 0700, 0615) |
| [exemple_sujet.tex](exemple_sujet.tex) | Sujet généré (20 points) |
| [verifier_fidelite.py](verifier_fidelite.py) | Compare source et sortie en ignorant les seules transformations structurelles |
| [compte_rendu.md](compte_rendu.md) | Vérifications réalisées sur l'exemple |

## Transformations autorisées

`enumerate` de questions → `parts`/`subparts` ; `\question[N]` ; intitulés « Question n » ;
espaces de réponse ; `\newpage` ; préambule et paramètres du sujet. Tout le reste est recopié tel quel.
