\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{diapo}[2012/18/06]
\DeclareOption*{%
    \PassOptionsToClass{\CurrentOption}{beamer}%
}
\ProcessOptions\relax

\LoadClass{beamer}

\RequirePackage{texmaths-symbols}
\RequirePackage{texmaths-colors}
\colortotal=5
\def\currentcolor{%
    \ifcase\colorindex
        Rainbow1-violet\or
        Rainbow1-bleu\or
        Rainbow1-vert\or
        Rainbow1-orange\or
        Rainbow1-rouge%
    \fi
}
\RequirePackage{texmaths-metadata}

% ==================================================
% STYLE DEFINITION
% ==================================================
\def\colorbg{CalmSerenity-1}
\def\colorfg{CalmSerenity-3!50!black}

\renewcommand\mathfamilydefault{\rmdefault}
\setbeamersize{text margin left=10pt, text margin right=10pt}
\setbeamercolor{frametitle}{fg=\colorfg, bg=\colorbg!80!vscode-blue}
\setbeamercolor{background canvas}{bg=\colorbg}
\setbeamercolor{normal text}{fg=vscode-gray}
\setbeamerfont{normal text}{size=\normalsize}
\setbeamerfont{frametitle}{size=\normalsize}
\setbeamertemplate{enumerate item}{\color{\colorfg}\bfseries\alph{enumi})}
\setbeamerfont{itemize/enumerate body}{size=\normalsize}
\setbeamercolor{itemize item}{fg=\colorfg}
\setbeamertemplate{navigation symbols}{}
\usefonttheme{serif}
