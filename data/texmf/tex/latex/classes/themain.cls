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

\ExplSyntaxOn
\cs_new:Npn \main@schoolyear_str:
    {
        \int_compare:nNnTF { \month } > { 6 }
            { \int_to_arabic:n { \year } - \int_to_arabic:n { \year + 1 } }
            { \int_to_arabic:n { \year - 1 } - \int_to_arabic:n { \year } }
    }
\edef\main@date{\main@schoolyear_str:}
\ExplSyntaxOff
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
\def\main@sequence@key{undefined}
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
\def\main@set@page@format=#1-#2;{\main@page@set@format@expl{#1-#2}}

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
    \main@eval@startfont
    \main@eval@head
    \main@eval@apply@fontsize@expl
    \main@apply@eval@baselineskip
    \global\leftskip0pt%
    \setlength{\footskip}{40pt}%
    \baremetrue
    \exercicevboxtrue
    \exercicemdframedtrue
}
\def\endevaluationstyle{\main@eval@endfont\enddoc\newpage\baremefalse\exercicevboxfalse\exercicemdframedfalse}

\newif\ifmulticols
\ExplSyntaxOn
\tl_new:N \l__main_page_format_tl
\tl_new:N \l__main_page_orientation_tl
\seq_new:N \l__main_page_parts_seq
\tl_new:N \l__main_eval_format_tl
\tl_new:N \l__main_eval_duree_tl
\tl_new:N \l__main_eval_calculatrice_tl
\tl_new:N \l__main_eval_consignes_tl
\tl_new:N \l__main_eval_sujet_tl
\tl_new:N \l__main_eval_font_tl
\tl_new:N \l__main_eval_skippageid_tl
\tl_new:N \l__main_eval_second_skippageid_tl
\tl_new:N \l__main_eval_colbreak_tl
\tl_new:N \l__main_eval_second_colbreak_tl
\tl_new:N \l__main_eval_endspace_tl
\tl_new:N \l__main_eval_baselineskip_tl
\tl_new:N \l__main_eval_fontsize_tl
\tl_new:N \l__main_eval_presentation_tl
\tl_new:N \l__main_eval_multicols_tl
\tl_new:N \l__main_eval_first_group_tl
\tl_new:N \l__main_eval_second_group_tl
\tl_new:N \l__main_eval_third_group_tl
\tl_new:N \l__main_eval_answer_space_tl
\tl_new:N \l__main_eval_answer_space_id_tl
\tl_new:N \l__main_eval_answer_space_type_tl
\tl_new:N \l__main_eval_items_tl
\tl_new:N \l__main_eval_exercice_id_tl
\tl_new:N \l__main_eval_bareme_tl
\tl_new:N \l__main_eval_name_tl
\seq_new:N \l__main_eval_split_seq
\prop_new:N \l__main_eval_answer_spaces_prop
\bool_new:N \l__main_eval_grouped_bool
\int_new:N \l__main_eval_group_index_int
\seq_new:N \l__main_chapter_cmp_seq
\seq_new:N \l__main_table_competences_seq
\tl_new:N \l__main_table_competences_tl

\cs_new_protected:Npn \main@page@apply@dimensions:nn #1#2
    {
        \tl_set:Ne \l_tmpa_tl
            { \tl_trim_spaces:n {#1} / \tl_trim_spaces:n {#2} }
        \str_case:VnF \l_tmpa_tl
            {
                {a5/portrait}
                    {
                        \global\pdfpageheight=\main@default@width
                        \global\pdfpagewidth=.5\main@default@height
                    }
                {a5/landscape}
                    {
                        \global\pdfpageheight=.5\main@default@height
                        \global\pdfpagewidth=\main@default@width
                    }
                {a4/portrait}
                    {
                        \global\pdfpageheight=\main@default@height
                        \global\pdfpagewidth=\main@default@width
                    }
                {a4/landscape}
                    {
                        \global\pdfpageheight=\main@default@width
                        \global\pdfpagewidth=\main@default@height
                    }
            }
            {
                \PackageWarning{themain}
                    {Format de page inconnu~: \tl_use:N \l_tmpa_tl}
            }
    }

\cs_new_protected:Npn \main@page@parse@format:n #1
    {
        \seq_set_split:Nnn \l__main_page_parts_seq { - } {#1}
        \seq_pop_left:NN \l__main_page_parts_seq \l__main_page_format_tl
        \seq_pop_left:NN \l__main_page_parts_seq \l__main_page_orientation_tl
        \tl_trim_spaces:N \l__main_page_format_tl
        \tl_trim_spaces:N \l__main_page_orientation_tl
    }

\cs_new_protected:Npn \main@page@set_format:n #1
    {
        \main@page@parse@format:n {#1}
        \newpage
        \exp_args:NVV \main@page@apply@dimensions:nn
            \l__main_page_format_tl \l__main_page_orientation_tl
        \main@set@page@geometry
    }

\cs_new_protected:Npn \main@page@set@format@expl #1
    { \main@page@set_format:n {#1} }

\cs_new_protected:Npn \main@sequence@set_key:n #1
    {
        \group_begin:
            \cs_set_eq:NN \' \use:n
            \cs_set_eq:NN \` \use:n
            \cs_set_eq:NN \^ \use:n
            \cs_set_eq:NN \" \use:n
            \cs_set_eq:NN \~ \use:n
            \cs_set:Npn \  { \c_underscore_str }
            \cs_gset:Npx \main@sequence@key {#1}
        \group_end:
    }

\cs_new_protected:Npn \main@sequence@set@key@expl #1
    { \main@sequence@set_key:n {#1} }

\cs_new_protected:Npn \main@addtomacro@expl #1#2
    {
        \cs_set:Npx #1 { \exp_not:V #1 \exp_not:n {#2} }
    }

\keys_define:nn { themain / evaluation }
    {
        format .tl_set:N = \l__main_eval_format_tl,
        type .code:n = { },
        duree .tl_set:N = \l__main_eval_duree_tl,
        calculatrice .tl_set:N = \l__main_eval_calculatrice_tl,
        consignes .tl_set:N = \l__main_eval_consignes_tl,
        competences .code:n = { },
        sujet .tl_set:N = \l__main_eval_sujet_tl,
        font .tl_set:N = \l__main_eval_font_tl,
        skip~page~id .tl_set:N = \l__main_eval_skippageid_tl,
        second~skip~page~id .tl_set:N = \l__main_eval_second_skippageid_tl,
        column~break~id .tl_set:N = \l__main_eval_colbreak_tl,
        second~column~break~id .tl_set:N = \l__main_eval_second_colbreak_tl,
        endspace .tl_set:N = \l__main_eval_endspace_tl,
        baselineskip .tl_set:N = \l__main_eval_baselineskip_tl,
        fontsize .tl_set:N = \l__main_eval_fontsize_tl,
        presentation .tl_set:N = \l__main_eval_presentation_tl,
        multicols .tl_set:N = \l__main_eval_multicols_tl,
        first~group .tl_set:N = \l__main_eval_first_group_tl,
        second~group .tl_set:N = \l__main_eval_second_group_tl,
        third~group .tl_set:N = \l__main_eval_third_group_tl,
        answer~space .tl_set:N = \l__main_eval_answer_space_tl,
        answerspaces .code:n = { \main@eval@set@answer_spaces:n {#1} }
    }

\keys_define:nn { themain / evaluation / answerspace }
    {
        id .tl_set:N = \l__main_eval_answer_space_id_tl,
        type .tl_set:N = \l__main_eval_answer_space_type_tl
    }

\cs_new_protected:Npn \main@eval@restore@expl
    {
        \tl_set:Nn \l__main_eval_format_tl { DS }
        \tl_set:Nn \l__main_eval_duree_tl { 50 min }
        \tl_set:Nn \l__main_eval_calculatrice_tl { autorisée }
        \tl_set:Nn \l__main_eval_consignes_tl { \relax }
        \tl_set:Nn \l__main_eval_sujet_tl { 0 }
        \tl_set:Nn \l__main_eval_font_tl { \normalfont }
        \tl_set:Nn \l__main_eval_skippageid_tl { none }
        \tl_set:Nn \l__main_eval_second_skippageid_tl { none }
        \tl_set:Nn \l__main_eval_colbreak_tl { none }
        \tl_set:Nn \l__main_eval_second_colbreak_tl { none }
        \tl_set:Nn \l__main_eval_endspace_tl { 0pt }
        \tl_set:Nn \l__main_eval_baselineskip_tl { none }
        \tl_set:Nn \l__main_eval_fontsize_tl { \normalsize }
        \tl_set:Nn \l__main_eval_presentation_tl { 0 }
        \tl_set:Nn \l__main_eval_multicols_tl { \multicolsfalse }
        \tl_set:Nn \l__main_eval_first_group_tl { \relax }
        \tl_set:Nn \l__main_eval_second_group_tl { \relax }
        \tl_set:Nn \l__main_eval_third_group_tl { \relax }
        \tl_set:Nn \l__main_eval_answer_space_tl { none }
        \prop_clear:N \l__main_eval_answer_spaces_prop
        \tl_clear:N \l__main_eval_name_tl
    }

\cs_new_protected:Npn \main@eval@set@keys #1
    {
        \keys_set:nn { themain / evaluation } {#1}
    }

\cs_new_protected:Npn \main@eval@set@answer_spaces:n #1
    {
        \prop_clear:N \l__main_eval_answer_spaces_prop
        \seq_clear:N \l_tmpa_seq
        \regex_extract_all:nnN
            {
                id \s* = \s* ([[:alnum:]-]+)
                \s* , \s*
                type \s* = \s* ([[:alpha:]-]+)
            }
            {#1}
            \l_tmpa_seq
        \int_step_inline:nnnn { 1 } { 3 } { \seq_count:N \l_tmpa_seq }
            {
                \prop_put:Nee \l__main_eval_answer_spaces_prop
                    { \seq_item:Nn \l_tmpa_seq { \int_eval:n {##1 + 1} } }
                    { \seq_item:Nn \l_tmpa_seq { \int_eval:n {##1 + 2} } }
            }
    }

\cs_new_protected:Npn \main@eval@apply@baselineskip@expl
    {
        \tl_if_eq:NnF \l__main_eval_baselineskip_tl { none }
            { \setlength{\baselineskip}{\tl_use:N \l__main_eval_baselineskip_tl} }
    }

\cs_new_protected:Npn \main@eval@set@format@name@expl
    {
        \str_case:VnF \l__main_eval_format_tl
            {
                {CC}{\tl_set:Nn \l__main_eval_name_tl {Contrôle~de~connaissances}}
                {DS}{\tl_set:Nn \l__main_eval_name_tl {Devoir~Surveillé}}
                {DM}{\tl_set:Nn \l__main_eval_name_tl {Devoir~Maison}}
            }
            { \tl_set:Nn \l__main_eval_name_tl {Format~inconnu} }
    }

\cs_new_protected:Npn \main@eval@use@settings@expl
    {
        \exp_args:NV \setanswerspace \l__main_eval_answer_space_tl
        \tl_if_eq:NnT \l__main_eval_font_tl { sf }
            { \everymath{\sf}\renewcommand{\familydefault}{\sfdefault}\sf }
        \tl_if_eq:NnT \l__main_eval_font_tl { dys }
            { \dysfont }
        % Si la valeur n'est ni 'sf' ni 'dys' ni le \normalfont par défaut,
        % tenter d'appliquer une police avec \fontspec (seulement sous LuaTeX).
        \tl_if_eq:NnF \l__main_eval_font_tl { sf }
            {
                \tl_if_eq:NnF \l__main_eval_font_tl { dys }
                    {
                        \tl_if_eq:NnF \l__main_eval_font_tl { \normalfont }
                            {
                                \tl_if_blank:VTF \l__main_eval_font_tl
                                    { }
                                    {
                                        \ifLuaTeX
                                            \cs_gset:Npx \main@eval@startfont { \begingroup \fontspec{\tl_use:N \l__main_eval_font_tl} }
                                            \cs_gset:Npn \main@eval@endfont { \endgroup }
                                        \else
                                            % non-LuaTeX : on ignore la valeur personnalisée
                                            \cs_gset:Npn \main@eval@startfont {}
                                            \cs_gset:Npn \main@eval@endfont {}
                                        \fi
                                    }
                            }
                    }
            }
        \tl_use:N \l__main_eval_multicols_tl
    }

\cs_new_protected:Npn \main@eval@apply@fontsize@expl
    { \tl_use:N \l__main_eval_fontsize_tl }

\cs_new:Npn \main@eval@note@label@expl #1
    { \tl_use:N \l__main_eval_format_tl #1 }

\cs_new:Npn \main@eval@sujet@value@expl
    { \tl_use:N \l__main_eval_sujet_tl }

\cs_new:Npn \main@eval@duree@value@expl
    { \tl_use:N \l__main_eval_duree_tl }

\cs_new:Npn \main@eval@consignes@value@expl
    { \tl_use:N \l__main_eval_consignes_tl }

\cs_new:Npn \main@eval@presentation@value@expl
    { \tl_use:N \l__main_eval_presentation_tl }

\cs_new_protected:Npn \main@eval@maybe@newline@expl
    {
        \tl_if_eq:NnF \l__main_eval_font_tl { dys }
            { \newline }
    }

\cs_new_protected:Npn \main@eval@calculator@label@expl
    {
        \str_if_eq:VnF \l__main_eval_format_tl { DM }
            { Calculatrice~\tl_use:N \l__main_eval_calculatrice_tl }
    }

\cs_new_protected:Npn \main@eval@skip@page@expl
    {
        \str_if_eq:eeT { \@exerciceID } { \tl_use:N \l__main_eval_skippageid_tl }
            { \newpage }
        \str_if_eq:eeT { \@exerciceID } { \tl_use:N \l__main_eval_second_skippageid_tl }
            { \newpage }
    }

\cs_new_protected:Npn \main@eval@break@column@expl
    {
        \str_if_eq:eeT { \@exerciceID } { \tl_use:N \l__main_eval_colbreak_tl }
            { \columnbreak }
        \str_if_eq:eeT { \@exerciceID } { \tl_use:N \l__main_eval_second_colbreak_tl }
            { \columnbreak }
    }

\cs_new_protected:Npn \main@eval@run@current@expl #1
    { \exp_args:NV \SetEval \l__main_eval_sujet_tl {#1} }

\cs_new_protected:Npn \main@eval@apply@answer_space@expl
    {
        \prop_get:NVNTF \l__main_eval_answer_spaces_prop
            \l__main_eval_exercice_id_tl
            \l_tmpa_tl
            { \exp_args:NV \setanswerspace \l_tmpa_tl }
            { \exp_args:NV \setanswerspace \l__main_eval_answer_space_tl }
    }

\cs_new_protected:Npn \main@eval@insert@exercise #1#2#3
    {
        \tl_if_blank:nTF {#2}
            {
                \tl_set:Ne \l_tmpa_tl { exercices/exercice-#1-\tl_use:N \l__main_eval_sujet_tl.tex }
                \exp_args:NV \file_if_exist:nTF \l_tmpa_tl
                    {
                        \tl_set:Ne \l_tmpa_tl { #1-\tl_use:N \l__main_eval_sujet_tl }
                        \exp_args:NV \exercice \l_tmpa_tl {#3}
                    }
                    { \exercice{#1-c}{#3} }
            }
            { \exercice{\@exerciceID}{#3} }
    }

\cs_new_protected:Npn \main@eval@apply@group@options #1
    {
        \int_case:nnF {#1}
            {
                {1}{\tl_use:N \l__main_eval_first_group_tl}
                {2}{\tl_use:N \l__main_eval_second_group_tl}
                {3}{\tl_use:N \l__main_eval_third_group_tl}
            }
            { }
    }

\cs_new_protected:Npn \main@eval@process@entry #1
    {
        \seq_set_split:Nnn \l__main_eval_split_seq { / } {#1}
        \seq_pop_left:NN \l__main_eval_split_seq \l__main_eval_exercice_id_tl
        \tl_trim_spaces:N \l__main_eval_exercice_id_tl
        \tl_set:Nx \l__main_eval_bareme_tl
            { \seq_use:Nn \l__main_eval_split_seq { / } }
        \cs_set:Npx \@exerciceID { \exp_not:V \l__main_eval_exercice_id_tl }
        \main@eval@apply@answer_space@expl
        \exp_args:NV \set@eval@exercices \l__main_eval_bareme_tl
    }

\cs_new_protected:Npn \main@eval@process@list #1
    {
        \ifmulticols\begin{multicols}{2}\fi
        \clist_map_inline:nn {#1}
            { \main@eval@process@entry{##1} }
        \ifmulticols\end{multicols}\fi
    }

\cs_new_protected:Npn \main@eval@process@groups #1
    {
        \int_zero:N \l__main_eval_group_index_int
        \clist_map_inline:nn {#1}
            {
                \int_incr:N \l__main_eval_group_index_int
                \begingroup
                        \exp_args:Ne \main@eval@apply@group@options
                            { \int_use:N \l__main_eval_group_index_int }
                        \main@eval@process@list{##1}
                \endgroup
            }
    }

\cs_new_protected:Npn \main@eval@run@lists #1
    {
        \bool_if:NTF \l__main_eval_grouped_bool
            { \main@eval@process@groups{#1} }
            { \main@eval@process@list{#1} }
    }

\cs_new_protected:Npn \main@eval@prepare@items #1#2
    {
        \main@eval@set@keys {#1}
        \main@eval@use@settings@expl
        \main@eval@set@format@name@expl
        \tl_set:Nx \l__main_eval_items_tl { \tl_trim_spaces:n {#2} }
        \exp_args:NV \tl_if_head_is_group:nTF \l__main_eval_items_tl
            {
                \bool_set_true:N \l__main_eval_grouped_bool
                \isgrouptrue
            }
            {
                \bool_set_false:N \l__main_eval_grouped_bool
                \isgroupfalse
            }
    }

\cs_new_protected:Npn \main@eval@set@sujet@title #1
    {
        \main@eval@set@keys { sujet=#1 }
        \tl_if_eq:NnTF \l__main_eval_sujet_tl { 0 }
            {
                \cs_set:Npx \main@eval@sujet@title
                    { \exp_not:V \l__main_eval_name_tl }
            }
            {
                \cs_set:Npx \main@eval@sujet@title
                    {
                        \exp_not:V \l__main_eval_name_tl
                        \exp_not:n { ~ (sujet ~ }
                        \exp_not:V \l__main_eval_sujet_tl
                        \exp_not:n {)}
                    }
            }
    }

\cs_new_protected:Npn \main@map@exercices #1
    {
        \clist_map_inline:nn {#1}
            { \exercice{##1}\relax }
    }

\cs_new_protected:Npn \main@process@activite #1
    {
        \global\advance\main@activite@count1\relax
        \edef\tmp{\the\main@activite@count}%
        \main@note{A\tmp}%
        \main@toc@addsubsubsection{Activité\ \tmp}%
        \subfile{activites/activite-#1.tex}%
        \newpage
    }

\cs_new_protected:Npn \main@map@activites #1
    {
        \clist_map_inline:nn {#1}
            { \main@process@activite{##1} }
    }

\cs_new_protected:Npn \main@process@questionflash #1
    {
        \global\advance\sequence@count@qfs1\relax
        \immediate\write\QFcanal{%
        \main@level-%
        \the\main@sequence@count-%
        \main@sequence@key-QF\the\sequence@count@qfs/#1}%
    }

\cs_new_protected:Npn \main@map@questionsflash #1
    {
        \clist_map_inline:nn {#1}
            { \main@process@questionflash{##1} }
    }

\cs_new_protected:Npn \main@process@diaporama #1
    {
        \global\advance\sequence@count@diapos1\relax
        \immediate\write\DIAPOcanal{%
        \main@level-%
        \the\main@sequence@count-%
        \main@sequence@key-Diapo\the\sequence@count@diapos/#1}%
    }

\cs_new_protected:Npn \main@map@diaporamas #1
    {
        \clist_map_inline:nn {#1}
            { \main@process@diaporama{##1} }
    }

\cs_new_protected:Npn \main@chapter@cmp@append@expl #1
    {
        \advance\chapter@cmp@count1\relax
        \seq_put_right:Nn \l__main_chapter_cmp_seq {#1}
    }

\cs_new:Npn \main@chapter@cmp@get@expl #1
    {
        \int_compare:nNnTF { \int_eval:n {#1 + 1} } > { \seq_count:N \l__main_chapter_cmp_seq }
            { \relax }
            { \seq_item:Nn \l__main_chapter_cmp_seq { \int_eval:n {#1 + 1} } }
    }

\cs_new_protected:Npn \main@chapter@cmp@reset@expl
    {
        \global\chapter@cmp@count=-1\relax
        \seq_clear:N \l__main_chapter_cmp_seq
        \main@table@competences@reset@expl
        \cs_if_exist:NT \chapter@cmp@expand
            { \cs_undefine:N \chapter@cmp@expand }
    }

\cs_new:Npn \main@chapter@cmp@all_items@expl
    {
        \int_compare:nNnT { \seq_count:N \l__main_chapter_cmp_seq } > { 0 }
            {
                \int_step_inline:nnnn { 0 } { 1 }
                    { \int_eval:n { \seq_count:N \l__main_chapter_cmp_seq - 1 } }
                    { \cmpItem{##1} }
            }
    }

\cs_new_protected:Npn \main@chapter@cmp@show@all@expl
    {
        \begingroup
            \tl_clear:N \l_tmpa_tl
            \int_step_inline:nnnn { 0 } { 1 }
                { \int_eval:n { \seq_count:N \l__main_chapter_cmp_seq - 1 } }
                {
                    \tl_put_right:Nx \l_tmpa_tl
                        {
                            \exp_not:N \\
                            \main@chapter@cmp@get@expl{##1}
                            &&&&
                        }
                }
            \let \chapter@cmp@expand \l_tmpa_tl
            \chapter@cmp@tblr
        \endgroup
    }

\cs_new_protected:Npn \main@chapter@cmp@show@default@expl
    {
        \int_compare:nNnTF { \seq_count:N \l__main_chapter_cmp_seq } > { 0 }
            { \main@chapter@cmp@show@all@expl }
            { \show@cmp@table }
    }

\cs_new_protected:Npn \main@table@competences@refresh@expl
    {
        \tl_clear:N \l__main_table_competences_tl
        \seq_map_inline:Nn \l__main_table_competences_seq
            { \tl_put_right:Nn \l__main_table_competences_tl {##1} }
    }

\cs_new_protected:Npn \main@table@competences@reset@expl
    {
        \seq_clear:N \l__main_table_competences_seq
        \tl_clear:N \l__main_table_competences_tl
    }

\cs_new_protected:Npn \main@table@competences@append@expl #1#2
    {
        \seq_put_right:Nn \l__main_table_competences_seq {#1&#2&&&\\}
        \main@table@competences@refresh@expl
    }

\cs_new:Npn \main@table@competences@body@expl
    { \tl_use:N \l__main_table_competences_tl }

\cs_new_protected:Npn \main@table@competences@parse@entry@expl #1
    {
        \seq_set_split:Nnn \l__main_eval_split_seq { / } {#1}
        \seq_pop_left:NN \l__main_eval_split_seq \l_tmpa_tl
        \tl_trim_spaces:N \l_tmpa_tl
        \tl_set:Nx \l_tmpb_tl { \seq_use:Nn \l__main_eval_split_seq { / } }
        \main@table@competences@append@expl {\l_tmpa_tl} {\l_tmpb_tl}
    }

\cs_new_protected:Npn \main@table@competences@from@semicolon@expl #1
    {
        \seq_set_split:Nnn \l_tmpa_seq { ; } {#1}
        \seq_map_inline:Nn \l_tmpa_seq
            {
                \tl_if_blank:nF {##1}
                    { \main@table@competences@parse@entry@expl {##1} }
            }
    }

\main@eval@restore@expl
\main@table@competences@reset@expl
\ExplSyntaxOff

% Macros de démarrage/fin de police pour les évaluations (par défaut vides)
\def\main@eval@startfont{}
\def\main@eval@endfont{}

\def\restoreDevoirVariables{%
        \main@eval@restore@expl
\normalsize\normalfont}

\def\setDevoirVariables#1{\main@eval@set@keys{#1}}

\def\main@apply@eval@baselineskip{\main@eval@apply@baselineskip@expl}

\def\skip@page{%
    \main@eval@skip@page@expl
}
\def\break@column{%
    \main@eval@break@column@expl
}

\def\setDevoirMaison{%
    \main@eval@set@keys{format=DM}%
    \main@eval@set@format@name@expl
    \main@eval@set@sujet@title{\main@eval@sujet@value@expl}%
}
    
\def\set@eval@format@name{\main@eval@set@format@name@expl}
\def\testif@exercice@ID@containsdash#1-#2\END#3{%
    \main@eval@insert@exercise{#1}{#2}{#3}%
}
\def\set@eval@exercices#1{%
    \noindent
    \expandafter\testif@exercice@ID@containsdash\@exerciceID-\END{#1}%
    \medskip\par
    \break@column
    \skip@page
}

\def\SetEval#1#2{%
    \main@eval@set@sujet@title{#1}%
    \main@toc@addsubsubsection{\main@eval@sujet@title}%
    \sequence@exercice@count0\relax%
    \beginevaluationstyle
    \main@note{\main@eval@note@label@expl{#1}}%
    \main@eval@run@lists{#2}%
    \endevaluationstyle
}
\def\main@eval@top#1#2{%
    \main@eval@prepare@items{#1}{#2}%
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
    \main@eval@run@current@expl{#2}%
    \endgroup
}
    
\def\main@eval@head{%
    \begin{mdframed}[roundcorner=7pt,backgroundcolor=\maintblrbgcolor]\noindent
        \begin{tblr}{colspec={Q[l]X[0.7,l]X[2,c]X[1,r]}}%
            {\baselineskip15pt Nom\\Prénom\\Classe}&{\baselineskip15pt :\\:\\:}%
            &{\baselineskip15pt\main@eval@sujet@title\\\hskip10pt\\\main@eval@duree@value@expl}%
            &{\baselineskip15pt Date~:\kern82pt\\\hskip10pt\main@eval@maybe@newline@expl{\bfseries \main@eval@calculator@label@expl}}%
        \end{tblr}%
    \end{mdframed}\par\noindent
    \ifx\chapter@cmp@expand\undefined\main@chapter@cmp@show@default@expl\else\chapter@cmp@tblr\fi
    \par\vskip10pt\noindent
    {\itshape\main@eval@consignes@value@expl}\par
    \ifnum\main@eval@presentation@value@expl>0\relax
        \main@eval@presentation@message\main@eval@presentation@value@expl
        \hfill{\bfseries /\main@eval@presentation@value@expl}%
    \fi
    \par\vskip5pt\noindent
}
% --------------
% Exercice input
% --------------
\def\main@set@exercice@layout@default{%
    \page@horizontal@margin=25pt%
    \page@vtop@sep=6pt%
    \page@head@height=12pt%
    \page@top@margin=10pt%
    \page@bmargin=20pt%
    \main@set@page@format=a5-landscape;%
}
\def\main@set@exercice@layout@fullpage{%
    \page@horizontal@margin=25pt%
    \page@vtop@sep=6pt%
    \page@head@height=12pt%
    \page@top@margin=10pt%
    \page@bmargin=51pt%
    \main@set@page@format=a4-portrait;%
}
\def\main@sheet@map@if@notblank#1{%
    \if\relax\detokenize{#1}\relax
    \else
        \main@map@exercices{#1}%
    \fi
}
\def\main@doubleexercicesheet#1#2{%
    \noindent
    \begin{minipage}[t]{.48\linewidth}%
        \main@sheet@map@if@notblank{#1}%
    \end{minipage}\kern.04\linewidth
    \begin{minipage}[t]{.48\linewidth}%
        \main@sheet@map@if@notblank{#2}%
    \end{minipage}}
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
    \main@sheet@map@if@notblank{#1}%
    }
\def\doublesheet#1#2{%
    \newexercicesheet
    \main@doubleexercicesheet{#1}{#2}}

\def\afoursheet#1{%
    \main@set@exercice@layout@fullpage
    \setlength{\footskip}{40pt}%
    \newexercicesheet\main@sheet@map@if@notblank{#1}%
    \main@set@exercice@layout@default
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
    \main@set@exercice@layout@default
    \global\advance\main@documents1
    \edef\main@doc@real@first@page{\thepage}%
    \pagestyle{exercice}%
    \xdef\main@page@style{exercice}%
    \global\leftskip0pt%
}
\def\endexercicestyle{\enddoc\newpage}
% ----------------
% Questions flashs
% ----------------
\def\questionsFlash#1{%
    \sequence@count@qfs=0\relax
    \main@map@questionsflash{#1}%
    }
% -------------------------
% Diaporamas cours dialogué
% -------------------------
\def\diaporamas#1{%
    \sequence@count@diapos=0\relax
    \main@map@diaporamas{#1}%
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
\long\def\sequence#1#2#3\endsequence{%
    #2%
    \main@chapter@cmp@reset@expl
    \def\main@sequence@name{#1}%
    \main@sequence@set@key@expl{#1}%
    \advance\main@sequence@count1\relax
    \sequence@example@count0\relax
    \sequence@exercice@count0\relax
    \label{\main@level:\the\main@sequence@count}%
    \def\main@toc@chapter{\bfseries Chapitre \the\main@sequence@count\ : \main@sequence@name}%
    \ifhidden\main@note{hidden}%
        {\bfseries\noindent\main@level : \main@toc@chapter(hidden)\par}%
        \main@toc@addhiddensubsection\main@toc@chapter
    \else
        \main@toc@addsubsection\main@toc@chapter
        \begingroup#3\endgroup
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
    nobreak=true,
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
    \main@chapter@cmp@append@expl{#1}%
    }
\let\addEvalCmp\chapter@cmp@append
\def\chapter@cmp[#1]{\main@chapter@cmp@get@expl{#1}}
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
\long\def\addtomacro#1#2{\main@addtomacro@expl#1{#2}}
\def\reset@table@competences{\main@table@competences@reset@expl}
\def\add@table@cmp#1/#2;{\main@table@competences@append@expl{#1}{#2}}
\def\stop@addtablecmp{\relax/0;}
\def\addtablecmp#1/#2;{\ifx#1\relax\else\main@table@competences@append@expl{#1}{#2}\fi}
\def\add@multiple@table@competences#1\relax/0;{\main@table@competences@from@semicolon@expl{#1}}
\def\addmultipletablecmp#1{\expandafter\add@multiple@table@competences#1\relax/0;}
\def\definechaptercompetences#1{%
    \PackageWarning{main.cls}{Utilisation obsolète \string\definechaptercompetences}%
    \main@table@competences@reset@expl
    \main@table@competences@from@semicolon@expl{#1}%
}

\def\show@cmp@table{\noindent
    \begin{tblr}[expand=\main@table@competences@body@expl]%
            {colspec=|*1{X[l,m]}*1{Q[r]}*4{|Q[c,m]}|,
            hlines,row{1}={bg=\maintblrbgcolor},column{2}={font=\bfseries}}%
        COMPETENCES&&A&B&C&D\\
        \main@table@competences@body@expl
    \end{tblr}\par
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
    \main@map@activites{#1}%
    \endactivitestyle
    }
% ===============
% Export examples
% ===============
\long\def\writeExemple#1{\immediate\write\exportedCanal{\detokenize{#1}}}

\pgfkeys{%
        exportedKeys/.cd,
        scale/.store in=\exportedKeys@scale,
        scale=1,
        vmargins/.store in=\exportedKeys@vmargins,
        vmargins=30,
        lmargin/.store in=\exportedKeys@lmargin,
        lmargin=30
    }

\def\toComplete@version{1}
\def\setCompleteVersion#1{\def\toComplete@version{#1}}
\def\toComplete#1{\ifnum\toComplete@version=0\relax\phantom{#1}\else#1\fi}

\long\def\exported@command<<#1>>{%
    \ifSubfilesClassLoaded{\begingroup#1\endgroup}{\begingroup
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
        \immediate\closeout\exportedCanal
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
\let\endsequence\relax
\long\def\SHOW#1\endsequence{\begingroup#1\endgroup}
\long\def\HIDE#1\endsequence{\begingroup\endgroup}

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
        }%
        % Cleaning exemples dir before compilation
        \run@python{../../}{clean_dir data/latex/exemples}
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