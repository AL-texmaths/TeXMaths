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