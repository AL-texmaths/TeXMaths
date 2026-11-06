Ce dépôt git est placé dans :
MiKTeX\texmfs\data\tex\latex\local

## Choix de la police

Avec la classe `themain`, choisir une des options `NewCenturySchoolbook`,
`Comfortaa`, `Verdana` ou `ComicSansMS`, par exemple :

```latex
\documentclass[ComicSansMS]{themain}
```

Avec une autre classe, charger le package après les autres packages de polices :

```latex
\usepackage[ComicSansMS]{texmaths-fonts}
```

Les mêmes quatre options sont disponibles pour le package. Sans option de police,
`themain` conserve son comportement par défaut. `Verdana` et `ComicSansMS`
nécessitent LuaLaTeX ou XeLaTeX ainsi que les polices correspondantes installées.
Le glossaire utilise LuaLaTeX pour sa génération.