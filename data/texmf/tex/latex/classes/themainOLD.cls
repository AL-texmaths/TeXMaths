\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{themain}

\makeatletter

\newif\ifcoloroption
\DeclareOption{Rainbow1}{%
    \AtEndOfClass{%
        \definecolor{beige}{HTML}{fff7e6}
        \def\mainbgcolor{Rainbow1-jaune!20!white}%
        \def\mainthmbgcolor{Rainbow1-rouge!50!white}%
        \def\maintblrbgcolor{Rainbow1-vert!30!white}%
        \def\maincodagecolor{red!80!black}
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
    }
}
\DeclareOption{NewCenturySchoolbook}{
    \AtEndOfClass{
        \usepackage[T1]{fontenc}
        \usepackage{pxfonts}
        \usepackage{newcent}
        \usepackage[symbolgreek,defaultmathsizes]{mathastext}
    }
}
\DeclareOption{Comfortaa}{
    \AtEndOfClass{
        \usepackage[default]{comfortaa}
        \usepackage[LGRgreek,defaultmathsizes,noasterisk]{mathastext}
        \let\varphi\phi
        \linespread{1.06}
    }
}
\DeclareOption{Verdana}{
    \AtEndOfClass{
        \usepackage[no-math]{fontspec}
        \setmainfont[Mapping=tex-text]{Verdana}
        \usepackage[defaultmathsizes,italic]{mathastext}
    }
}
\DeclareOption{ComicSansMS}{
    \AtEndOfClass{
        \usepackage[no-math]{fontspec}
        \setmainfont[Ligatures=TeX]{Comic Sans MS}
        \usepackage[defaultmathsizes]{mathastext}
    }
}
\let\main@tableofcontents\relax
\DeclareOption{toc}{%
\AtEndOfClass{%
    \let\main@tableofcontents\tableofcontents
  }
}
\DeclareOption*{%
\PassOptionsToClass{\CurrentOption}{article}%
}
\ProcessOptions\relax
\LoadClass{article}
% ==================
% NECESSARY PACKAGES
% ==================
\RequirePackage{geometry}
\RequirePackage{fancyhdr}
\RequirePackage{refcount}
\RequirePackage{subfiles}
\RequirePackage{texmaths-main}
% ----------------------
\RequirePackage{hyperref}%
\hypersetup{
    colorlinks=true,
    linkcolor=vscode-crimson,
    urlcolor=vscode-blue,       % exemple pour les URLs
    citecolor=vscode-green      % exemple pour les citations
}
% ----------------------
% global constant macros
% ----------------------

\ifLuaTeX
  \let\pdfpageheight\pageheight
  \let\pdfpagewidth\pagewidth
\fi

\edef\main@date{\expandafter\ifnum\the\month>6\relax
    \the\year-\number\numexpr\the\year+1\relax
    \else
    \number\numexpr\the\year-1\relax-\the\year
    \fi}
\def\main@school{Collège Victor Hugo, Sarcelles}
\def\main@teacher{M. Longelin}
\def\main@DM{DM}
\def\main@DS{DS}
\def\main@CC{CC}
\def\main@none{none}
\def\main@zero{0}
\def\main@eval@fontsf{sf}
\def\main@eval@fontdys{dys}
\def\main@eval@presentation@message#1{%
    {\noindent\itshape La présentation et la qualité de la rédaction comptera
    pour #1 points dans la note finale.}%   
}
% ----------------------
% global variable macros
% ----------------------
\def\main@level{undefined}
\def\main@sequence@name{undefined}
\def\main@doc@type{undefined}
\def\main@doc@even{undefined}
\def\main@sequence@key{undefined}
\def\main@doc@numbered{undefined}
\newif\ifdocnumbered
\newif\ifdoceven
\def\main@eval@sujet@title{undefined}
% --------
% counters
\newcount\main@documents
\newcount\main@activite@count
\newcount\main@sequence@count
\newcount\cours@definition
\newcount\cours@propriete
\newcount\cours@methode
\newcount\cours@regle
\newcount\cours@theoreme
\newcount\sequence@example@count
\newcount\@bigpart@count
\newcount\@subpart@count
\newcount\sequence@exercice@count
\newcount\sequence@count@qfs
\newcount\sequence@count@diapos
% ------------------------
% Definition of skip amount
\def\main@skip@coeff{1}
\smallskipamount\number\numexpr\main@skip@coeff*3pt
    plus\number\numexpr\main@skip@coeff*1pt
    minus\number\numexpr\main@skip@coeff*1pt
\medskipamount\number\numexpr\main@skip@coeff*6pt
    plus\number\numexpr\main@skip@coeff*2pt
    minus\number\numexpr\main@skip@coeff*2pt
\bigskipamount\number\numexpr\main@skip@coeff*12pt
    plus\number\numexpr\main@skip@coeff*4pt
    minus\number\numexpr\main@skip@coeff*4pt
% ------------------------
% page geometry dimensions
% ------------------------
\newdimen\main@default@width
\newdimen\main@default@height
\main@default@width=210mm
\main@default@height=297mm

\newdimen\page@horizontal@margin% left and right margins dimension
\newdimen\page@vtop@sep
\newdimen\page@head@height
\newdimen\page@top@margin
\newdimen\page@bmargin
\newdimen\page@textheight
\newdimen\page@width
% ----------------------
% global geometry macros
\def\@portrait{portrait}
\def\@landscape{landscape}

% ORIGINAL
\def\page@format#1{%
    \ifnum\expandafter\@gobone#1=5\relax
        \ifx\page@orientation\@portrait
            \pdfpageheight=\main@default@width
            \pdfpagewidth=.5\main@default@height
        \else
            \ifx\page@orientation\@landscape
                \pdfpageheight=.5\main@default@height
                \pdfpagewidth=\main@default@width
            \fi
        \fi
    \else
        \ifnum\expandafter\@gobone#1=4\relax
            \ifx\page@orientation\@portrait
                \pdfpageheight=\main@default@height
                \pdfpagewidth=\main@default@width
            \else
                \ifx\page@orientation\@landscape
                    \pdfpageheight=\main@default@width
                    \pdfpagewidth=\main@default@height
                \fi
            \fi
        \fi
    \fi
    }

% ORIGINAL
\def\main@set@page@format=#1-#2;{%
    \def\page@orientation{#2}\newpage
    \page@format{#1}\main@set@page@geometry}

% ORIGINAL
\def\main@set@page@geometry{%
    \page@textheight\dimexpr\pdfpageheight-\page@top@margin-\page@vtop@sep
        -\page@head@height-2\page@vtop@sep-\page@bmargin\relax
    \page@width\dimexpr\pdfpagewidth-2\page@horizontal@margin\relax
    \newgeometry{%
        includehead,
        includefoot,
        lmargin=\page@horizontal@margin,
        textwidth=\page@width,
        top=\page@top@margin,
        headsep=\page@vtop@sep,
        headheight=\page@head@height,
        textheight=\page@textheight,
        footskip=2\page@vtop@sep
    }%
    \headwidth=\page@width
}
% --------------------------------------
% global documents style and page macros
\def\main@doc@page{%
    \number\numexpr\thepage-\main@doc@real@first@page+1\relax
    }
\def\main@doc@last@page{%
    \number\numexpr
    \getpagerefnumber{maindoc\the\main@documents}-\main@doc@real@first@page+1\relax
}
% ==========
% TOC macros
% ==========
\def\main@toc@addsubsubsection#1{%
    \phantomsection
    \addcontentsline{toc}{subsubsection}{#1}%
}
\def\main@toc@addsubsection#1{%
    \phantomsection
    \addcontentsline{toc}{subsection}{#1}%
}
\def\main@toc@addhiddensubsection#1{%
    \begingroup
        \hypersetup{hidelinks}%
        \addtocontents{toc}{\protect\contentsline{subsection}{#1}{}{}}%
    \endgroup
}
% ==========
% DOC STYLES
% ==========
% -------------------------------------
% Cours
% -------------------------------------
\fancypagestyle{cours}{%
    \fancyhf{}%
    \fancyhead[L]{\ifodd\main@doc@page\relax\main@level\fi}%
    \fancyhead[C]{\ifodd\main@doc@page\relax Séquence
        \the\main@sequence@count\kern5pt--\kern5pt\main@sequence@name\fi}%
    \fancyhead[R]{\ifodd\main@doc@page\relax\main@doc@type\fi}%
    \fancyfoot[L]{\ifodd\main@doc@page\relax\main@date\fi}%
    \fancyfoot[C]{\main@doc@page/\main@doc@last@page}%
    \fancyfoot[R]{\ifodd\main@doc@page\relax\main@teacher\fi}%
    \renewcommand{\headrulewidth}{0pt}%
    \renewcommand{\footrulewidth}{0pt}%
    }
\def\begincoursstyle{%
    \def\main@doc@type{Cours}%
    \doceventrue
    \page@horizontal@margin=30pt%
    \page@vtop@sep=15pt%
    \page@head@height=20pt%
    \page@top@margin=5pt%
    \page@bmargin=20pt%
    \begindoc a5-portrait;cours;%
    \main@toc@addsubsubsection{Leçon}%
    \ifSubfilesClassLoaded{}{\main@note{cours}}%
}
\def\endcoursstyle{\enddoc}
% -------------------------------------
% Activite
% -------------------------------------
\def\font@activite{\small}
\fancypagestyle{activite}{%
    \fancyhf{}%
    \fancyhead[L]{\font@activite\main@level}%
    \fancyhead[C]{\font@activite Séquence \the\main@sequence@count\kern5pt--\kern5pt\main@sequence@name}%
    \fancyhead[R]{\font@activite\main@doc@type\ifdocnumbered\ \the\main@activite@count\fi}%
    \fancyfoot[L]{\font@activite\main@date}%
    \fancyfoot[R]{\font@activite\main@teacher}%
    \renewcommand{\headrulewidth}{0pt}%
    \renewcommand{\footrulewidth}{0pt}%
    }
\def\beginactivitestyle{%
    \def\main@doc@type{Activité}%
    \main@activite@count=0\relax
    \docevenfalse
    \docnumberedtrue
    \page@horizontal@margin=30pt%
    \page@vtop@sep=15pt%
    \page@head@height=20pt%
    \page@top@margin=5pt%
    \page@bmargin=20pt%
    \begindoc a5-portrait;activite;%
    \global\leftskip0pt%
}
\def\endactivitestyle{\enddoc\newpage}
% ----------
% Evaluation
% ----------
\def\font@evaluation{\small}
\fancypagestyle{evaluation}{%
    \fancyhf{}%
    \fancyhead[L]{\font@evaluation\ifodd\main@doc@page\relax\main@level\fi}%
    \fancyhead[C]{\font@evaluation\ifodd\main@doc@page\relax Séquence
        \the\main@sequence@count\kern5pt--\kern5pt\main@sequence@name\fi}%
    \fancyhead[R]{\font@evaluation\ifodd\main@doc@page\relax\main@doc@type\fi}%
    \fancyfoot[L]{\font@evaluation\ifodd\main@doc@page\relax\main@date\fi}%
    \fancyfoot[C]{\font@evaluation\main@doc@page/\main@doc@last@page}%
    \fancyfoot[R]{\font@evaluation\ifodd\main@doc@page\relax\main@teacher\fi}%
    \renewcommand{\headrulewidth}{0pt}%
    \renewcommand{\footrulewidth}{0pt}%
    }
\def\beginevaluationstyle{%
    \def\main@doc@type{Évaluation}%
    \docevenfalse
    \page@horizontal@margin=30pt%
    \page@vtop@sep=10pt%
    \page@head@height=20pt%
    \page@top@margin=15pt%
    \page@bmargin=51pt%
    \begindoc a4-portrait;evaluation;%
    \main@eval@head
    \main@eval@fontsize
    \main@apply@eval@baselineskip
    \global\leftskip0pt%
    \setlength{\footskip}{40pt}%
    \baremetrue
    \exercicevboxtrue
    \exercicemdframedtrue
}
\def\endevaluationstyle{\enddoc\newpage\baremefalse\exercicevboxfalse\exercicemdframedfalse}

\newif\ifmulticols
\pgfkeys
{%
    /devoirvariables/.cd,
    format/.store in=\main@eval@format,
    format = DS,
    type/.store in=\main@eval@type,
    type = none,
    duree/.store in=\main@eval@duree,
    duree = 50 min,
    calculatrice/.store in=\main@eval@calculatrice,
    calculatrice = autorisée,
    consignes/.store in=\main@eval@consignes,
    consignes = \relax,
    competences/.store in=\main@eval@competences,
    competences = none,
    sujet/.store in=\main@eval@sujet,
    sujet=0,
    font/.store in=\main@eval@font,
    font=\normalfont,
    skip page id/.store in=\main@eval@skippageid,
    skip page id=none,
    second skip page id/.store in=\main@eval@secondskippageid,
    second skip page id=none,
    column break id/.store in=\main@eval@colbreak,
    column break id=none,
    second column break id/.store in=\main@eval@secondcolbreak,
    second column break id=none,
    endspace/.store in=\main@eval@endspace,
    endspace=0pt,
    baselineskip/.store in=\main@eval@baselineskip,
    baselineskip=none,
    fontsize/.store in=\main@eval@fontsize,
    fontsize=\normalsize,
    presentation/.store in=\main@eval@presentation,
    presentation=0,
    multicols/.store in=\main@eval@multicols,
    multicols=\multicolsfalse,
    first group/.store in=\main@fisrtgroup@options,
    first group=\relax,
    second group/.store in=\main@secondgroup@options,
    second group=\relax,
    third group/.store in=\main@thirdgroup@options,
    third group=\relax,
    answer space/.store in=\main@eval@answer@space,
    answer space=none
}

\def\restoreDevoirVariables{%
    \pgfkeys{%
        /devoirvariables/.cd,
        format = DS,
        type = none,
        duree = 50 min,
        calculatrice = autorisée,
        consignes = \relax,
        competences = none,
        sujet=0,
        font=\normalfont,
        fontsize=\normalsize,
        skip page id=none,
        second skip page id=none,
        column break id=none,
        second column break id=none,
        endspace=0pt,
        baselineskip=none,
        presentation=0,
        multicols=\multicolsfalse,
        first group=\relax,
        second group=\relax,
        third group=\relax,
        answer space=none%
        }%
\normalsize\normalfont}

\def\setDevoirVariables#1{\pgfkeys{/devoirvariables/.cd,#1}}

\def\main@apply@eval@baselineskip{%
    \ifx\main@eval@baselineskip\main@none\else
        \setlength{\baselineskip}{\main@eval@baselineskip}%
    \fi
}

\def\skip@page{%
    \ifx\@exerciceID\main@eval@skippageid\newpage\fi
    \ifx\@exerciceID\main@eval@secondskippageid\newpage\fi
}
\def\break@column{%
    \ifx\@exerciceID\main@eval@colbreak\columnbreak\fi
    \ifx\@exerciceID\main@eval@secondcolbreak\columnbreak\fi
}

\def\setDevoirMaison{%
    \def\main@eval@sujet@title{ (sujet \main@eval@sujet)}%
    \def\main@eval@type{Devoir Maison}%
    }
    
\def\set@eval@format@name{%
    \ifx\main@eval@format\main@CC\def\main@eval@name{Contrôle de connaissances}%
    \else
    \ifx\main@eval@format\main@DS\def\main@eval@name{Devoir Surveillé}%
    \else
    \ifx\main@eval@format\main@DM\def\main@eval@name{Devoir Maison}
    \else\def\main@eval@name{Format inconnu}%
    \fi\fi\fi
}
\def\testif@exercice@ID@containsdash#1-#2\END#3{%
    \ifx\relax#2\relax
        \IfFileExists{exercices/exercice-#1-\main@eval@sujet.tex}{%
        \exercice{#1-\main@eval@sujet}{#3}%
    }{%
        \exercice{#1-c}{#3}%
    }%
    \else
        \exercice{\@exerciceID}{#3}%
    \fi
}
\def\set@eval@exercices#1{%
    \noindent
    \expandafter\testif@exercice@ID@containsdash\@exerciceID-\END{#1}%
    \medskip\par
    \break@column
    \skip@page
}

\def\SetEval#1#2{%
    \setDevoirVariables{sujet=#1}% set the options defined in #1 argument
    \ifx\main@eval@sujet\main@zero\relax
        \def\main@eval@sujet@title{\main@eval@name}%
    \else
        \def\main@eval@sujet@title{\main@eval@name\ (sujet \main@eval@sujet)}%
    \fi
    \main@toc@addsubsubsection{\main@eval@sujet@title}% add to toc
    \sequence@exercice@count0\relax% reset exercices count
    \beginevaluationstyle
    \main@note{\main@eval@format#1}%
    \ifisgroup
    \foreach[count=\i from 1]\exoIDS in{#2}{%
    \begingroup% MAX GROUP 3
    \ifnum\i=1\relax
    \main@fisrtgroup@options
                \else\ifnum\i=2\relax
                    \main@secondgroup@options
                    \else\ifnum\i=3\relax
                    \main@thirdgroup@options
                    \fi\fi\fi
            \ifmulticols\begin{multicols}{2}\fi
            \foreach\@exerciceID/\bareme in\exoIDS{%
                \set@eval@exercices\bareme
                }%
            \ifmulticols\end{multicols}\fi\endgroup
        }%
    \else
        \ifmulticols\begin{multicols}{2}\fi
        \foreach\@exerciceID/\bareme in{#2}{%
            \set@eval@exercices\bareme
        }%
        \ifmulticols\end{multicols}\fi
    \fi
    \endevaluationstyle
}
\def\main@eval@top#1#2{%
    \setDevoirVariables{#1}%
    \setanswerspace{\main@eval@answer@space}
    \ifx\main@eval@font\main@eval@fontsf
    \everymath{\sf}\renewcommand{\familydefault}{\sfdefault}\sf
    \else
        \ifx\main@eval@font\main@eval@fontdys
            \dysfont
        \fi
    \fi
    \main@eval@multicols%            set the multicols option (default false)
    \set@eval@format@name%           set the format of the eval
    \expandafter\@testisgroup{#2}%
}
\def\evaluationAB#1#2{%
    \begingroup
    \main@eval@top{#1}{#2}
    \SetEval A{#2}%
    \SetEval B{#2}%
    \endgroup
}

\def\evaluation#1#2{%
    \begingroup
    \main@eval@top{#1}{#2}
    \expandafter\SetEval\main@eval@sujet{#2}%
    \endgroup
}
    
\def\main@eval@head{%
    \begin{mdframed}[roundcorner=7pt,backgroundcolor=\maintblrbgcolor]\noindent
        \begin{tblr}{colspec={Q[l]X[0.7,l]X[2,c]X[1,r]}}%
            {\baselineskip15pt Nom\\Prénom\\Classe}&{\baselineskip15pt :\\:\\:}%
            &{\baselineskip15pt\main@eval@sujet@title\\\hskip10pt\\\main@eval@duree}%
            &{\baselineskip15pt Date~:\kern82pt\\\hskip10pt\ifx\main@eval@font\main@eval@fontdys\relax\else\newline\fi{\bfseries \ifx\main@eval@format\main@DM\else Calculatrice \main@eval@calculatrice\fi}}%
        \end{tblr}%
    \end{mdframed}\par\noindent
    \ifx\chapter@cmp@expand\undefined\show@cmp@table\else\chapter@cmp@tblr\fi
    \par\vskip10pt\noindent
    {\itshape\main@eval@consignes}\par
    \ifnum\main@eval@presentation>0\relax
        \main@eval@presentation@message\main@eval@presentation
        \hfill{\bfseries /\main@eval@presentation}%
    \fi
    \par\vskip5pt\noindent
}
% --------------
% Exercice input
% --------------
\let\enonce\read@enonce@from@data
\let\readexercice\read@exercice@from@data
\def\noversion#1-#2{#1}
\def\rating#1=#2{}
\def\newexercicesheet{\newpage
    \edef\tmp{\main@doc@page}%
    \main@toc@addsubsubsection{Feuille d'exercice \tmp}%
    \main@note{E\tmp}%
    }
\newif\ifbareme
\newif\ifexercicevbox
\newif\ifexercicemdframed
\long\def\exercice@vbox@identity#1{#1}
\def\exercice#1#2{%
    \global\advance\sequence@exercice@count1\relax
    \ifexercicevbox\let\exercice@vbox\vbox\else\let\exercice@vbox\exercice@vbox@identity\fi
    \exercice@vbox{% la vbox permet d'empecher le découpage d'un exercice
        \ifexercicemdframed\begin{mdframed}[%
            innertopmargin=5pt,
            innerbottommargin=5pt,
            innerleftmargin=5pt,
            skipabove=0.5em,
            backgroundcolor=\maintblrbgcolor
        ]\fi\noindent
        {\bfseries Exercice \the\sequence@exercice@count\ :\hfill\ifbareme/#2\fi}%
        \ifexercicemdframed
            \end{mdframed}\vspace{-5pt}%
        \else
            \par
        \fi
        \noindent\readexercice{#1}\medskip\par
        }%
    }
\def\simplesheet#1{%
    \newexercicesheet
    \foreach\exercice@id in{#1}{\exercice\exercice@id\relax}%
    }
\def\doublesheet#1#2{%
    \newexercicesheet
    \noindent
    \begin{minipage}[t]{.48\linewidth}%
        \foreach\exercice@id in{#1}{\exercice\exercice@id\relax}%
    \end{minipage}\kern.04\linewidth
    \begin{minipage}[t]{.48\linewidth}%
        \foreach\exercice@id in{#2}{\exercice\exercice@id\relax}%
    \end{minipage}}

\def\afoursheet#1{%
    \page@top@margin=10pt%
    \page@bmargin=51pt%
    \main@set@page@format=a4-portrait;%
    \begingroup\setlength{\footskip}{40pt}%
    \newexercicesheet\foreach\exercice@id in{#1}{\exercice\exercice@id\relax}%
    \endgroup
    \page@top@margin=10pt%
    \page@bmargin=20pt%
    \main@set@page@format=a5-landscape;%
}
\newenvironment{exercices}{%
    \beginexercicestyle
    \baremefalse
    \exercicevboxfalse
    \setanswerspace{none}
    }{\endexercicestyle}
\mdfdefinestyle{exercice}{%
    innertopmargin=4pt,
    innerbottommargin=4pt,
    skipabove=0pt,
    skipbelow=0pt%
    }
% --------------
% Exercice style
% --------------
\def\font@exercice{\small}
\fancypagestyle{exercice}{%
    \fancyhf{}%
    \fancyhead[L]{\font@exercice\main@level}%
    \fancyhead[C]{\font@exercice Séquence \the\main@sequence@count\kern5pt--\kern5pt\main@sequence@name}%
    \fancyhead[R]{\font@exercice\main@doc@type\ifdocnumbered\ \main@doc@page\fi}%
    \fancyfoot[L]{\font@exercice\main@date}%
    \fancyfoot[R]{\font@exercice\main@teacher}%
    \renewcommand{\headrulewidth}{0pt}%
    \renewcommand{\footrulewidth}{0pt}
    }
\def\beginexercicestyle{%
    \def\main@doc@type{Feuille d'exercice}%
    \docevenfalse
    \docnumberedtrue
    \page@horizontal@margin=25pt%
    \page@vtop@sep=6pt%
    \page@head@height=12pt%
    \page@top@margin=10pt%
    \page@bmargin=20pt%
    \begindoc a5-landscape;exercice;%
    \global\leftskip0pt%
}
\def\endexercicestyle{\enddoc\newpage}
% ----------------
% Questions flashs
% ----------------
\def\questionsFlash#1{%
    \sequence@count@qfs=0%
    \foreach\questionFlash in{#1}{%
        \global\advance\sequence@count@qfs1%
        \immediate\write\QFcanal{%
        \main@level-%
        \the\main@sequence@count-%
        \main@sequence@key-QF\the\sequence@count@qfs/\questionFlash}%
        }%
    }
% -------------------------
% Diaporamas cours dialogué
% -------------------------
\def\diaporamas#1{%
    \sequence@count@diapos0%
        \foreach\Diaporama in{#1}{%
            \global\advance\sequence@count@diapos1%
            \immediate\write\DIAPOcanal{%
            \main@level-%
            \the\main@sequence@count-%
            \main@sequence@key-Diapo\the\sequence@count@diapos/\Diaporama}%
            }%
    }
% ===========================================================================
% theorems insertion (definitions, proprietes, theoremes, methodes, règles)
% ===========================================================================
\def\definition#1{\advance\cours@definition1\byheart{Définition \number
    \cours@definition}{\input{enonces/definitions/#1.tex}}}
\def\propriete#1{\advance\cours@propriete1\byheart{Propriété \number
    \cours@propriete}{\input{enonces/proprietes/#1.tex}}}
\def\methode#1{\advance\cours@methode1\byheart{Méthode \number
    \cours@methode}{\input{enonces/methodes/#1.tex}}}
\def\regle#1{\advance\cours@regle1\byheart{Règle \number
    \cours@regle}{\input{enonces/regles/#1.tex}}}
\def\theoreme#1{\advance\cours@theoreme1\byheart{Théorème \number
    \cours@theoreme}{\input{enonces/theoremes/#1.tex}}}
\let\proposition\propriete
% -------------------------------------
\def\begindoc#1;#2;{%
    \main@set@page@format=#1;%
    \global\advance\main@documents1
    \edef\main@doc@real@first@page{\thepage}%
    \pagestyle{#2}%
    \xdef\main@page@style{#2}%
}

\def\enddoc{\par
    \ifdoceven\ifodd\number\numexpr\thepage-\main@doc@real@first@page+1\relax
        \newpage\pagestyle{\main@page@style}\hbox{}\fi\fi
    \label{maindoc\the\main@documents}%
    }

\def\level#1{%
    \clearpage\def\main@level{#1}\main@sequence@count0%
    \label{\main@level}%
    \addcontentsline{toc}{section}{\main@level}%
    }
\def\@underscore{\string_}
\def\sequence#1#2{%
    #2%
    \def\main@sequence@name{#1}%
    \begingroup
        \let\'\@firstofone
        \let\`\@firstofone
        \let\ \@underscore
        \xdef\main@sequence@key{#1}%
    \endgroup
    \advance\main@sequence@count1\relax
    \sequence@example@count0\relax
    \sequence@exercice@count0\relax
    \label{\main@level:\the\main@sequence@count}%
    \def\main@toc@chapter{\bfseries Chapitre \the\main@sequence@count\ : \main@sequence@name}%
    \ifhidden\main@note{hidden}
        {\bfseries\noindent\main@level : \main@toc@chapter(hidden)\par}%
        \main@toc@addhiddensubsection\main@toc@chapter\HIDE
    \else
        \main@toc@addsubsection\main@toc@chapter\SHOW
    \fi
    }
% ==============
% MDFRAMED BOXES
% ==============
\global\mdfdefinestyle{byheart}{%
    backgroundcolor=\mainthmbgcolor,
    linecolor=\mainbgcolor,
    roundcorner=5pt,
    leftmargin=\parindent,
    innertopmargin=8pt,
    innerbottommargin=8pt,
}
% ------
% Macros
% ------
% =================
% NEW TABLE CMP
% =================
\newcount\chapter@cmp@count
\chapter@cmp@count=-1\relax
\def\chapter@cmp@append#1{%
    \advance\chapter@cmp@count1\relax
    \expandafter\def\csname chapter@cmp[\the\chapter@cmp@count]\endcsname{#1}%
    }
\let\addEvalCmp\chapter@cmp@append
\def\chapter@cmp[#1]{\csname chapter@cmp[#1]\endcsname}
\def\cmpItem#1{\unexpanded{\\}\chapter@cmp[#1]&&&&}
\def\setEvalCmp#1{\edef\chapter@cmp@expand{#1}}
\def\chapter@cmp@tblr{%
    \noindent
    \begin{tblr}[expand=\chapter@cmp@expand]%
            {colspec=|*1{X[l,m]}*1{Q[r]}*4{|Q[c,m]}|,
            hlines,row{1}={bg=\maintblrbgcolor},column{2}={font=\bfseries}}%
        COMPETENCES&&A&B&C&D\chapter@cmp@expand
    \end{tblr}\par
}
% ------------------
% Competences macros
% -------------------------------------
\long\def\addtomacro#1#2{%
    \expandafter\def\expandafter#1\expandafter{#1#2}%
}
\def\expand@table@competences{}
\def\reset@table@competences{\def\expand@table@competences{}}
\def\add@table@cmp#1/#2;{\addtomacro\expand@table@competences{#1&#2&&&\\}}
\def\stop@addtablecmp{\relax/0;}
\def\addtablecmp#1/#2;{\ifx#1\relax\else\add@table@cmp#1/#2;\fi}
\def\add@multiple@table@competences#1/#2;{\ifx#1\relax\else\add@table@cmp#1/#2;\expandafter\add@multiple@table@competences\fi}
\def\addmultipletablecmp#1{\add@multiple@table@competences#1\relax/0;}
\def\definechaptercompetences#1{%
    \PackageWarning{main.cls}{Utilisation obsolète \string\definechaptercompetences}%
    \reset@table@competences\addmultipletablecmp{#1}%
}

\def\show@cmp@table{\noindent
    \begin{tblr}[expand=\expand@table@competences]%
            {colspec=|*1{X[l,m]}*1{Q[r]}*4{|Q[c,m]}|,
            hlines,row{1}={bg=\maintblrbgcolor},column{2}={font=\bfseries}}%
        COMPETENCES&&A&B&C&D\\
        \expand@table@competences
    \end{tblr}\par
}
% ---------------------------------
\def\diagnum#1{%
    \begin{tikzpicture}[baseline=(O.base)]
        \coordinate(O)at(0,-0.12);
        \draw(-0.12,-0.12)--(0.12,0.12);
        \node at(0,0){#1};
    \end{tikzpicture}%
}
\def\circlenum#1{%
    \begin{tikzpicture}[baseline=(O.base)]
        \draw(0,0)circle(.25);
        \draw node at(0,0){#1};
    \end{tikzpicture}%
}
% ============
% TITLE MACROS
% ============

\def\bigpart#1{%
    \@subpart@count0\relax
    \advance\@bigpart@count1\bigbreak\global\leftskip0pt\noindent{\Large\bfseries
    \expandafter\@Roman\expandafter{\the\@bigpart@count}) #1\par\kern
    5pt\global\leftskip\parindent}%
}
\def\subpart#1{%
    \advance\@subpart@count1\smallbreak\global\leftskip0pt\noindent{\large\bfseries
    \the\@subpart@count) #1\par\kern
    10pt\global\leftskip2\parindent}%
}
\long\def\byheart#1#2{%
    \begin{mdframed}[style=byheart]
        \noindent{\bfseries #1 :}\par
        \kern.2\baselineskip
        \leftskip\parindent
        % \rightskip0pt plus 1fil\relax
        \noindent
        #2%
    \end{mdframed}%
}
% =======================
% DOCTYPE IN-MAIN COMMAND
% =======================
\def\cours{%
    \begincoursstyle
        \subfile{cours/\main@level-\main@sequence@key.tex}%
    \endcoursstyle
}
\def\activites#1{%
    \beginactivitestyle
    \foreach\activite in{#1}{%
        \global\advance\main@activite@count1
        \edef\tmp{\the\main@activite@count}%
        \main@note{A\tmp}%
        \main@toc@addsubsubsection{Activité\ \tmp}%
        \subfile{activites/activite-\activite.tex}%
        \newpage}%
    \endactivitestyle
    }
% ===============
% Export examples
% ===============
\long\def\writeExemple#1{\immediate\write\exportedCanal{\unexpanded{#1}}}

\pgfkeys{%
        exportedKeys/.cd,
        scale/.store in=\exportedKeys@scale,
        scale=1,
        vmargins/.store in=\exportedKeys@vmargins,
        vmargins=30,
        lmargin/.store in=\exportedKeys@lmargin,
        lmargin=30,
        active/.store in=\exported@active,
        active=0%
    }

\def\toComplete@version{1}
\def\setCompleteVersion#1{\def\toComplete@version{#1}}
\def\toComplete#1{\ifnum\toComplete@version=0\relax\phantom{#1}\else#1\fi}

\long\def\exported@command<<#1>>{%
    \ifSubfilesClassLoaded{\begingroup#1\endgroup}{\begingroup
        \ifnum\exported@active=0\relax\else
        \global\advance\sequence@example@count1\relax
        \immediate\openout\exportedCanal=exemples/\main@level
        -Ch\the\main@sequence@count-cours_exemple_\the\sequence@example@count.tex%
        \writeExemple{\documentclass[varwidth]{standalone}}%
        \immediate\write\exportedCanal{\@percentchar scale[\exportedKeys@scale]}%
        \immediate\write\exportedCanal{\@percentchar lmargin[\exportedKeys@lmargin]}%
        \immediate\write\exportedCanal{\@percentchar vmargins[\exportedKeys@vmargins]}%
        \writeExemple{\usepackage{texmaths-main}}%
        \writeExemple{\begin{document}}%
        \writeExemple{\setCompleteVersion{0}#1}%
        \writeExemple{\end{document}}%
        \immediate\closeout\exportedCanal\fi
        #1\endgroup
        }%
    }
  
\newcommand{\exported}[1][]{%
    \pgfkeys{exportedKeys/.cd,#1}\exported@command%
    }
% ==============
% GLOBALS MACROS
% ==============
\def\defined#1{{\bfseries #1}}
\def\main@note#1{\immediate\write\canal{%
    \thepage-%
    \main@level-%
    \the\main@sequence@count-%
    \main@sequence@key-#1}}
% Permet de cacher les chapitres souhaités
\newif\ifhidden
\let\endsequence\endgroup
\long\def\SHOW#1\endsequence{\begingroup#1}
\long\def\HIDE#1\endsequence{\begingroup}

\def\contentsname{\centering Table des matières}
\def\delexemples#1{%
    \immediate\write18{powershell -Command "Get-ChildItem exemples/*.#1 | Remove-Item"}%
}

\AtBeginDocument{%
    \pagecolor\mainbgcolor
    \ifSubfilesClassLoaded{}{%
        \main@tableofcontents
        \newwrite\canal
        \newwrite\QFcanal
        \newwrite\DIAPOcanal
        \newwrite\exportedCanal
        \immediate\openout\canal=\jobname-structure.txt%
        \immediate\openout\QFcanal=\jobname-QF.txt%
        \immediate\openout\DIAPOcanal=\jobname-diapo.txt%
        \delexemples{tex}%
        \delexemples{log}%
        \delexemples{aux}%
        \delexemples{pdf}%0
        }%
    }
\AtEndDocument{%
    \ifSubfilesClassLoaded{}{%
        \immediate\closeout\canal
        \immediate\closeout\QFcanal
        \immediate\closeout\DIAPOcanal
        \immediate\closeout\exportedCanal
        }%
    }
\makeatother