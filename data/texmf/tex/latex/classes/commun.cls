\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{commun}[23/10/2021]

\RequirePackage{kvoptions}
\SetupKeyvalOptions{family=commun,prefix=commun@}

    \DeclareStringOption[DNB]{format}
    \DeclareDefaultOption{%
        \PassOptionsToClass{\CurrentOption}{exam}%
    }
    \ProcessKeyvalOptions*
    \LoadClass[12pt,french,a4paper]{exam}
    \addpoints

\def\@jour{none}\newcommand{\jour}[1]{\def\@jour{#1}}
\def\@duree{none}\newcommand{\duree}[1]{\def\@duree{#1}}
\def\@totpoints{none}\newcommand{\totpoints}[1]{\def\@totpoints{#1}}
\def\@presentationpoints{none}\newcommand{\presentationpoints}[1]{\def\@presentationpoints{#1}}
\def\@presentation{true}\newcommand{\presentation}[1]{\def\@presentation{#1}}
\def\@consignes{false}\newcommand{\consignes}[1]{\def\@consignes{#1}}
\def\@sujetarendre{false}\newcommand{\sujetarendre}[1]{\def\@sujetarendre{#1}}
\def\@false{false}
\def\@true{true}

\RequirePackage{iftex}
\ifPDFTeX
    \RequirePackage[french]{babel}
    \RequirePackage{inputenc}
    \RequirePackage[T1]{fontenc}
    \RequirePackage{lmodern}
\fi
\ifLuaTeX
    \RequirePackage[french]{babel}
    \RequirePackage{fontspec}
    \setmainfont{Latin Modern Roman}
\fi
\RequirePackage{geometry}
\geometry{a4paper}
\geometry{top=1cm,bottom=2.5cm,left=1.5cm,right=1.5cm,marginparwidth=2cm}
\linespread{1.25}
\RequirePackage{mdframed}
\RequirePackage{xcolor}
\RequirePackage{tcolorbox}


% \RequirePackage{fancyhdr}

% \RequirePackage{pifont}

%% Sets page size and margins

%%Color packages
% \RequirePackage{xcolor}

% \RequirePackage[svgnames,dvipsnames]{xcolor}
% \RequirePackage{colorpack}
% \RequirePackage[colorinlistoftodos]{todonotes}
% \RequirePackage[colorlinks=true, allcolors=blue]{hyperref}
% \RequirePackage{tkz-tab}
% \RequirePackage{colortbl}
% \RequirePackage{tikzpack}

%% Useful packages
% \RequirePackage{amsmath}
% \RequirePackage{enumitem}
% \RequirePackage{scratch3}
% \RequirePackage{tabularray}
% \RequirePackage{tkz-euclide}
% \usetikzlibrary{babel}


% \RequirePackage{pst-all}
% \RequirePackage{picturesdir}
% \RequirePackage{pict2e}
% \setlength{\unitlength}{1cm}
% \RequirePackage{amsthm}
% \RequirePackage{indentfirst}
% \RequirePackage{amsfonts}
% \RequirePackage{multicol}
% \RequirePackage{textcomp}
% \RequirePackage{gensymb}
% \RequirePackage{boxpack}
% \RequirePackage{pgf-pie}
%%\RequirePackage[nosolutionfiles]{answers}

\ifthenelse{\equal{\commun@format}{DNB}}
{\def\@titre{Brevet Blanc \@jour}}{}
\ifthenelse{\equal{\commun@format}{DS}}
{\def\@titre{Devoir commun \@jour}}{}


%%Pour interro
%%\addtolength\headheight{-3\baselineskip}

%%\pagestyle{headandfoot}
%%\firstpageheadrule
%%\runningheadrule
%%\firstpageheader{Nom : \\ Prénom :}{}{Classe : \texttt{\@class}\phantom{\Large A} \\Date : \phantom{ \texttt{\@class}}\phantom{.\Large A}}

\pagestyle{foot}

\usepackage{lastpage}
\lfoot{}
\cfoot{Page \textbf{\thepage} sur \textbf{\numpages}}
\rfoot{\ifthenelse{\equal{\thepage}{\pageref{LastPage}}}{\scriptsize{Fin !}}{\scriptsize{Tournez, SVP !}}}

%%\qformat{\textbf{Question \thequestion \ :} \ }
\qformat{
\begin{tcolorbox}[colback=white,boxrule=0.5pt]
    \textbf{Exercice \thequestion \ : (\thepoints)} \hfill
\end{tcolorbox}
}
%\begin{simplebox}
%\textbf{Exercice \thequestion \ :} \hfill \
%\end{simplebox}
%} %%pour les interrogations
%\bonuspointname{ points bonus}
%\bonusqformat{\textbf{Question bonus \thebonusquestion (\thepoints): }\hfill} %pour les questions bonus
\renewcommand{\solutiontitle}{\noindent}
\bonusqformat{
    \begin{tcolorbox}[colback=white,boxrule=0.5pt]
        \textbf{Exercice \thequestion \ : \hfill BONUS}
    \end{tcolorbox}
}
%%\renewcommand{\solutiontitle}{\noindent\textbf{Réponse \thequestion \ :}\enspace}

%\newtheoremstyle{gray}{\topsep}{\topsep}{}{0pt}{\bfseries}{}{ }{\fcolorbox{gray}{white}{\gray{\thmname{#1}\thmnumber{}\thmnote{(#3)}}}}
%\theoremstyle{gray}
%\newtheorem{exo}{Exercice \theexo}
%\renewcommand{\theexo}{}

%%Answers and questions
\shadedsolutions
\definecolor{cettecouleur}{rgb}{0.9,0.17,0.31}
\definecolor{SolutionColor}{rgb}{1.0,0.94,0.96}
\SolutionEmphasis{\color{cettecouleur}}

\hqword{Exercice}
%\chqword{Exercice}
\hpword{Points}
%\chbpword{Points bonus}
%\chsword{Score}

\renewcommand\partlabel{\textbf{\thepartno.}}
\renewcommand\subpartlabel{\textbf{\thesubpart.}}

\renewcommand\thepartno{\arabic{partno}}
\renewcommand\thesubpart{\alph{subpart}}

\def\addtopresentation{\relax}
\def\presentationfont{}
\AtBeginDocument{
    \begin{mdframed}
        \begin{center}
            {\Huge \textbf{\@titre}} \\ \bigskip
            {\Huge \textbf{Mathématiques}} \\ \bigskip
            {\large Durée de l'épreuve : \@duree \ - \@totpoints \ points}
        \end{center}
    \end{mdframed}
    \ifx\@presentation\@true\presentationfont L'orthographe, le soin, la qualité, la clarté et la précision des raisonnements seront pris en compte dans l'évaluation de la copie. \addtopresentation\hfill / \@presentationpoints \ points \\ \noindent \fi
    \ifx\@consignes\@false\else\@consignes\fi
    %\if\@consignes\@false\else\begingroup\it\@consignes\endgroup\fi
    \par %\bigskip
    \begin{center}
        \pointtable[h]
    \end{center}
    %  \par \bigskip
    %  \bonusgradetable[h]
    \begingroup\large
    \ifx\@sujetarendre\@true
        \par\noindent
        \ifthenelse{\equal{\commun@format}{DNB}}
        {Numéro de candidat~:\par\noindent Date de naissance~:\par\noindent}
        {Nom~:\par\noindent Prénom~:\par\noindent Classe~:\par}
    \fi
    \endgroup\vskip10pt
}
\endinput
