\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{compte-rendu}[23/10/2021]
\LoadClass{article}

\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage[french]{babel}
\usepackage{mdframed}
\usepackage{enumitem}

\makeatletter
\def\setDate#1{\def\lienCL@date{#1}}
\def\setPlace#1{\def\lienCL@place{#1}}
\def\setTeachers#1{\def\lienCL@teachers{#1}}

\def\newunivar#1{\def#1[##1]{\csname\string#1[##1]\endcsname}}
\def\defunivar#1[#2]{\expandafter\def\csname\string#1[#2]\endcsname}

\newunivar\KF
\defunivar\KF[nom]{Kévin FRANÇOIS}
\defunivar\KF[établisement]{Lycée Jean-Jacques Rousseau}

\newunivar\ALA
\defunivar\ALA[nom]{Aymen LANDOLSI}
\defunivar\ALA[établisement]{Lycée Jean-Jacques Rousseau}

\newunivar\ALO
\defunivar\ALO[nom]{Antoine LONGELIN}
\defunivar\ALO[établisement]{Collège Victor Hugo}

\newunivar\LV
\defunivar\LV[nom]{Laetitia VALENTE}
\defunivar\LV[établisement]{Collège Victor Hugo}

\AtBeginDocument{
    \begin{mdframed}[innertopmargin=15pt,innerbottommargin=15pt]
        \begin{center}
            \bfseries\LARGE Lien Collège-Lycée (Sarcelles)
            \vskip10pt\normalfont\Large Réunion du \lienCL@date\
            (\lienCL@place)
        \end{center}\vskip30pt
    \end{mdframed}\vskip80pt minus 60pt
    \begin{flushright}
        \@for\key:={\lienCL@teachers}\do{
        {\bfseries\csname\key\endcsname[nom]}\par
        \csname\key\endcsname[établisement]\vskip10pt
        }
    \end{flushright}
    \vskip50pt minus 30pt
    {\bfseries Objetifs :}\vskip10pt
}
\makeatother

\def\gm#1{\og#1\fg}