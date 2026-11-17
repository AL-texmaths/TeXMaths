# Initialisation d'un projet VSCode avec synchronisation git

## arborescence du projet

root/  
├── programmes/  
│   ├── vscode/  
│   ├── python/  
│   ├── miktex/  
├── antoine/  
│   ├── TeXMaths/ `dossier racine du depot git`
│   │   ├── .vscode/
│   │   ├── .gitignore
│   │   └── texmaths.code-workspace
└── laetitia/  
│   ├── TonDossier/ `dossier racine du depot git`
│   │   ├── .vscode/
│   │   ├── .gitignore
│   │   └── tondossier.code-workspace

1. Créer l'arborescence
2. Initialisation du depot git
> `git init`  
> `git remote add github https://github.com/USERNAME/REPOSITORY.git`  
> `git branch -M main`

## installation et configuration des programmes
### vscode
1. Télécharger la dernière version de vscode portable
https://code.visualstudio.com/docs/setup/portable
2. Configurer la version portable en créant le dossier data
3. Installation des extensions :
- french --> French Language
- latex --> LaTeX Workshop
- python --> Python
4. settings :
- files.exclude
- latex-workshop.latex.tools
- latex-workshop.latex.recipes
- latex-workshop.latex.recipe.default
- latex-workshop.latex.autoBuild.run
5. Définir le chemin vers l'interpréteur python installé dans /root/programmes/
### python
1. Télécharger python 3.12
https://www.python.org/downloads/release/python-31216/
2. L'installer dans root/programmmes/python/
### miktex
1. Télécharger miktex portable
https://miktex.org/howto/portable-edition
2. L'installer dans root/programmes/miktex

### Création de snippet
- taper `ctrl + shift + P`
- taper `snippet`
- sélectionner `Extraits: Configurer des extraits de codes`
- le snippet à trois caractéristiques : `prefix`, `body` et `description`.
- pour l'utiliser, taper le début du prefix puis `ctrl + enter`

### Gestion du proxy
- voir les fichiers batch du dd exerne