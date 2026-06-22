\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{thedocument}[2026/02/27]
\newif\ifafour
\DeclareOption{a4}{\afourtrue}
\DeclareOption{exercice}{%
    \AtEndOfClass{%
        \ifafour
        \geometry{%
            a4paper,
            portrait,
            hmargin=10pt,
            tmargin=20pt,
            bmargin=20pt,
            includefoot,
            includehead
            }
        \else
        \geometry{%
            a5paper,
            landscape,
            hmargin=10pt,
            tmargin=20pt,
            bmargin=20pt,
            includefoot,
            includehead
            }
        \fi
        \let\enonce\read@enonce@from@exercices
        \incataloguetrue
        \setanswerspace{squares}
    }
    \AtEndDocument{%
        \ifisdata
        \makeatletter
        \run@python{../../../}{write_exercice_packages \jobname}
        \makeatother
        \fi
    }
}
\DeclareOption{activite}{%
    \AtEndOfClass{%
        \geometry{%
            a5paper,
            portrait,
            hmargin=30pt,
            tmargin=20pt,
            bmargin=20pt,
            includefoot,
            includehead
            }
    }
}
\DeclareOption*{%
    \PassOptionsToClass{\CurrentOption}{article}%
}
\ProcessOptions\relax

\LoadClass{article}

\RequirePackage{geometry}
\RequirePackage{fancyhdr}
\RequirePackage{texmaths-metadata}
\RequirePackage{texmaths-symbols}
\RequirePackage{texmaths-spacing}
\RequirePackage{texmaths-variables}
\RequirePackage{texmaths-path}
\RequirePackage{texmaths-pytools}
% Le package hyperref est utilisé dans le main
% Il provoque un espace vertical positif
% des environment enumerate inclus dans une minipage
% L'insérer ici permet d'imiter le comportement du main
\RequirePackage{hyperref}%
% couleur par default dans les documents
\newif\ifisdata
\isdatatrue
\def\nodata{\incataloguefalse\isdatafalse}