\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{flash}[2026/02/28]
\DeclareOption*{%
    \PassOptionsToClass{\CurrentOption}{beamer}%
}
\ProcessOptions\relax

\LoadClass{beamer}

\RequirePackage{animate}
\RequirePackage{xparse}
\RequirePackage{tikz}
\usetikzlibrary{calc}
\RequirePackage{texmaths-colors}
\RequirePackage{texmaths-metadata}
\RequirePackage{texmaths-symbols}
\RequirePackage{libertinus}
% =================
% GLOBAL PARAMETERS
% =================
\newif\ifadobe
\def\SPEEDRATIO{1.125}
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
\AtBeginDocument{
    \ifx\iftizknextcolor\undefined\else\tizknextcolorfalse\fi
}
% ==========================
% color used in tikz picture
% ==========================
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
% ==================================================
% global variables
% ==================================================
\def\FlashSetFirstColumnRatio#1{%
    \def\FirstColumnRatio{#1}%
    \pgfmathsetmacro{\SecondColumnRatio}{1-#1}%
}
\FlashSetFirstColumnRatio{0.75}
\newcommand{\FlashShowConsignes}[2][Consignes]{%
    \begin{frame}{#1}
        \begin{itemize}
            #2
        \end{itemize}
    \end{frame}
}
% ==================================================
% TON TIMER ANIMÉ
% ==================================================
\newif\ifflashvisibletimer
\def\flash@timer@scale{1}
\def\flash@qcm@font{\footnotesize}
\def\flash@qcm@vratio{0.75}
\def\FlashSetTimerScale#1{\def\flash@timer@scale{#1}}
\def\FlashSetQcmFont#1{\def\flash@qcm@font{#1}}
\def\FlashSetQcmVratio#1{\def\flash@qcm@vratio{#1}}
\makeatletter
\def\flash@qcm@visible#1{%
    \foreach[count=\ii]\answer in{#1}{%
        \draw node[anchor=north west]at($(B)+(0,-\ii*\flash@qcm@vratio+\flash@qcm@vratio)$){%
            \flash@qcm@font{\bfseries\@Alph\ii) }\answer
            };
    }
}
\def\flash@qcm@halfvisible#1{%
    \foreach[count=\ii]\answer in{#1}{%
        \ifnum\i>\halfFrame\relax
            \draw node[anchor=north west]at($(B)+(0,-\ii*\flash@qcm@vratio+\flash@qcm@vratio)$){%
                \flash@qcm@font{\bfseries\@Alph\ii) }\answer
                };
        \else
            \draw node[anchor=north west]at($(B)+(0,-\ii*\flash@qcm@vratio+\flash@qcm@vratio)$){%
                \flash@qcm@font{\bfseries\@Alph\ii) }\color{\colorbg}\answer
                };
        \fi
    }
}
\newcommand{\simpleTimerVisible}[2][]{%
    % #1 : durée en secondes
    \edef\frameNumber{\number\numexpr10*#2\relax}%
    \edef\halfFrame{\number\numexpr\frameNumber/2\relax}%
    \edef\increment{\number\numexpr3600/\frameNumber\relax}%
    \edef\NewFrameNumber{\number\numexpr\frameNumber+1\relax}%
    \edef\radius{.45\linewidth}
    \begin{animateinline}[autoplay]{10}%
        \multiframe{\NewFrameNumber}{i=0+1,rtheta=0+0.1*\increment}{%
        \begin{tikzpicture}[scale=\flash@timer@scale]
            \coordinate(O)at(0,0);
            \coordinate(A)at(90:\radius);
            \draw[\colorbg](O)circle[radius=\radius*1.1];
            \draw[vscode-blue, fill=vscode-blue](O)--(A)
                arc[start angle=90, end angle=90+\rtheta, radius=\radius] -- (O);
            \coordinate(B)at(-\radius,-\radius);
            \flash@qcm@halfvisible{#1}
        \end{tikzpicture}
        }%
    \end{animateinline}
}
\newcommand{\simpleTimerUnvisible}[1][]{%
    \edef\radius{.45\linewidth}
    \begin{tikzpicture}[scale=\flash@timer@scale]
        \coordinate(O)at(0,0);
        \draw[\colorbg](O)circle[radius=\radius*1.1];
        \draw[vscode-blue,fill=vscode-blue](O)circle[radius=\radius];
        \coordinate(B)at(-\radius,-\radius);
        \flash@qcm@visible{#1}
    \end{tikzpicture}
}

\ExplSyntaxOn

\seq_new:N \g_flash_seq
\int_new:N \l_flash_mid_int
\int_new:N \l_flash_count_int
% ===============
% Single question
% ===============
\seq_new:N \g_flash_single_seq
\cs_new_protected:Npn \flash_single_print:n #1
{
    \flash_single_extract:nn #1
}

\cs_new_protected:Npn \flash_single_extract:nn #1#2
{
    #2
}
\NewDocumentCommand{\flash}{m +m O{}}
{
    \seq_gclear:N \g_flash_single_seq
    \seq_gput_right:Nn \g_flash_single_seq
        {
            {#1}
            {#2}
        }
    \flash_frame:nnn {#1} {#2} {#3}
}

\NewDocumentCommand{\FlashCorrection}{}
{
    \begin{frame}{Correction}
    \vspace{\g_flash_vtop_dim}
    \seq_map_function:NN \g_flash_single_seq \flash_single_print:n
    \end{frame}
}
% ==================================================
% Ajout item
% ==================================================

\NewDocumentCommand{\flashitem}{mm O{}}
{
    \seq_gput_right:Nx \g_flash_seq
        {
            {#1}
            { \exp_not:n {#2} }
            { \exp_not:n {#3} }
        }
}

% ==================================================
% Commande principale
% ==================================================

\NewDocumentCommand{\flashlist}{+m}
{
    \seq_gclear:N \g_flash_seq
    #1
    \flash_build_all:
}

% ==================================================
% Construction
% ==================================================
\def\flash@at@correction{\relax}
\def\AtCorrection#1{\def\flash@at@correction{#1}}
\cs_new_protected:Nn \flash_build_all:
{
    \seq_map_function:NN \g_flash_seq \flash_build_one:
    \flash@at@correction
    \flash_build_correction:
}

\cs_new_protected:Npn \flash_build_one: #1
{
    \flash_frame:nnn #1
}

% ==================================================
% Frame individuelle
% ==================================================
\tl_new:N \g_flash_header_tl

\NewDocumentCommand{\flashheader}{m}
{
    \tl_gset:Nn \g_flash_header_tl {#1}
}

\cs_new_protected:Nn \flash_frame:nnn
{
    \begin{frame}{\g_flash_title_tl}
    \ifadobe
        \transduration{0.2}
    \else
        \pgfmathsetmacro{\VarTransduration}{#1*\SPEEDRATIO}
        \expandafter\transduration\expandafter{\VarTransduration}
    \fi
    \tl_if_empty:NF \g_flash_header_tl
    {
        \centering
        \large \g_flash_header_tl
        \par\vspace{1em}
    }

    \begin{columns}
    
    \column{\FirstColumnRatio\textwidth}
    \centering
    {\boldmath#2}
    
    \column{\SecondColumnRatio\textwidth}
    \raggedleft
    \ifflashvisibletimer
        \simpleTimerVisible[#3]{#1}%
    \else
        \simpleTimerUnvisible[#3]%
    \fi
    
    \end{columns}
    \end{frame}
}

% ==================================================
% Correction (questions seules)
% ==================================================

\cs_new_protected:Nn \flash_build_correction:
{
    \int_set:Nn \l_tmpa_int { \seq_count:N \g_flash_seq }
    \int_set:Nn \l_flash_mid_int
        { \int_div_truncate:nn { \l_tmpa_int + 1 } { 2 } }
    \begin{frame}{Correction}
    \begin{columns}[T]
    \column{0.5\textwidth}
    \vspace{\g_flash_vtop_dim}
    \begin{enumerate}
    \setlength{\itemsep}{\g_flash_itemsep_dim}
    \int_zero:N \l_flash_count_int
    \seq_map_function:NN \g_flash_seq \flash_left_item:
    \end{enumerate}
    \vfill
    \column{0.5\textwidth}
    \vspace{\g_flash_vtop_dim}
    \begin{enumerate}
        \setlength{\itemsep}{\g_flash_itemsep_dim}
    \setcounter{enumi}{\l_flash_mid_int}
    \int_zero:N \l_flash_count_int
    \seq_map_function:NN \g_flash_seq \flash_right_item:
    \end{enumerate}
    \end{columns}
    \vfill
    \end{frame}
}

\cs_new_protected:Npn \flash_left_item: #1
{
    \int_incr:N \l_flash_count_int
    \int_compare:nT { \l_flash_count_int <= \l_flash_mid_int }
        { \flash_print_question:nnn #1 }
}

\cs_new_protected:Npn \flash_right_item: #1
{
    \int_incr:N \l_flash_count_int
    \int_compare:nT { \l_flash_count_int > \l_flash_mid_int }
        { \flash_print_question:nnn #1 }
}

\cs_new_protected:Nn \flash_print_question:nnn
{
    \item #2
}
\keys_define:nn { flash }
{
    itemsep .dim_set:N = \g_flash_itemsep_dim,
    itemsep .initial:n = 0.5em,
    vtop .dim_set:N = \g_flash_vtop_dim,
    ctop .initial:n = 0em,
}
\dim_gset:Nn \g_flash_itemsep_dim { 0.5em }
\dim_gset:Nn \g_flash_vtop_dim { 0em }

\NewDocumentCommand{\FlashSetItemSep}{m}
{
    \dim_gset:Nn \g_flash_itemsep_dim { #1 }
}
\NewDocumentCommand{\FlashSetVtop}{m}
{
    \dim_gset:Nn \g_flash_vtop_dim { #1 }
}
\tl_new:N \g_flash_title_tl
\tl_gset:Nn \g_flash_title_tl { Question } % valeur par défaut

\NewDocumentCommand{\FlashSetTitle}{m}
{
  \tl_gset:Nn \g_flash_title_tl { #1 }
}

\ExplSyntaxOff
\makeatother