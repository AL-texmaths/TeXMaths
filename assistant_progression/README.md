## Required project structure

- config.json must exist
- data/latex/catalogue must exist <path:code_index>
- data/katex must exist <path:katex>
- data/latex/progressions must exist <path:progression_import>
- data/texmf must exist <path:texmf>
- data/latex/codes_labels must exist <path:code_labels>
- data/latex/sequencages must exist <path:progression_export>

## Procedure adding new catalogue

- catalogues data are stored in "<path:texmf>/tex/latex/.../new_catalogue.sty"
- the catalogue is render by a LaTeX file "<path:code_index>/new_catalogue.tex>"
that use the package new_catalogue.sty.
- during the compilation, a file new_catalogue-data.txt must be generated : each
lines of the file is a keys:value as:
[key0(name_of_catalogue)|:|key1|:|...|:|value]
- update the config json in the key "catalogue"
--> to update the data the user must only modify the sty file and then click
" Mise à jour" in the menu.

## Architecture modulaire

|-- app

    |--- config.py

    |--- context.py

    |--- resolve.py

    |--- startup.py

|-- controllers

    |--- document_controller.py

    |--- search_controller.py

|-- models

    |--- document.py

    |--- search_filters.py

|-- services

    |--- database_service.py

    |--- document_repository.py

    |--- katex_service.py

    |--- preview_service.py

    |--- process_service.py

    |--- search_service.py

    |--- theme_service.py

|-- views

    |--- tabs

        |--- search_tab.py

        |--- settings_tab.py

    |--- widgets

        |--- filters_pannel.py

        |--- metadata_view.py

        |--- pdf_viewer.py

        |--- results_list.py

        |--- search_bar.py

|--workers

    |--- database_workers.py

## Structure du fichier JSON

- executables
  - lualatex
    - [list]
      - str
  - latexmk
    - [list]
      - str
- paths
  - cycle 3 BO 2026
    - [list]
      - str
  - cycle 4 BO 2026
    - [list]
      - str
  - katex
    - [list]
      - str
  - latex
    - [list]
      - str
  - code index
    - [list]
      - str
  - code labels
    - [list]
      - str
  - progression export path
    - [list]
      - str
  - progression import path
    - [list]
      - str
  - texmf
    - [list]
      - str
- catalogues
  - packages to check
    - BO_2026.tex
      - [list]
        - str
    - BO_competences_evaluees.tex
      - [list]
        - str
    - BO_competences-cycle3-BO_2020.tex
      - [list]
        - str
    - BO_competences-cycle4-BO_2020.tex
      - [list]
        - str
    - Sources.tex
      - [list]
        - str
  - codes
    - cmpsocle
      - str
    - cycle 3 BO 2020
      - str
    - cycle 4 BO 2020
      - str
    - cmp
      - str
    - cns
      - str
    - cycle 3 BO 2026
      - str
    - cycle 4 BO 2026
      - str
    - aut
      - str
    - obj
      - str
    - pro
      - str
    - src
      - str
    - sea
      - str
  - aut obj pro catalogues
    - [list]
      - str
- settings
  - main window title
    - str
  - themes
    - VSCode Dark
      - bg
        - str
      - fg
        - str
      - panel
        - str
      - accent
        - str
      - border
        - str
      - focus_bg
        - str
      - focus_border
        - str
      - font
        - str
    - Soothing
      - bg
        - str
      - fg
        - str
      - panel
        - str
      - accent
        - str
      - border
        - str
      - focus_bg
        - str
      - focus_border
        - str
      - font
        - str
    - Obsidian Dark
      - bg
        - str
      - fg
        - str
      - panel
        - str
      - accent
        - str
      - border
        - str
      - focus_bg
        - str
      - focus_border
        - str
      - font
        - str
    - Nord Dark
      - bg
        - str
      - fg
        - str
      - panel
        - str
      - accent
        - str
      - border
        - str
      - focus_bg
        - str
      - focus_border
        - str
      - font
        - str
    - Fusion
      - bg
        - str
      - fg
        - str
      - panel
        - str
      - accent
        - str
      - border
        - str
      - focus_bg
        - str
      - focus_border
        - str
      - font
        - str
    - Fusion Crimson
      - bg
        - str
      - fg
        - str
      - panel
        - str
      - accent
        - str
      - border
        - str
      - focus_bg
        - str
      - focus_border
        - str
      - font
        - str
  - current
    - theme
      - str
    - code
      - str
