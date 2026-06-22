\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{flash}[2012/18/06]
\LoadClass[aspectratio=169,t]{beamer}

\usepackage{tkz-euclide}
\usepackage{animate}
\usepackage{enumitem}
% \usepackage{xcolor}
\usepackage{pgffor}
\usepackage{pgfkeys}
% \usepackage{multicol}
\usepackage{colorpack}
% \usepackage{thepackage}

\gdef\FPS{10}
\makeatletter
\def\qf@title{Titre}
\def\setTitle#1{\def\qf@title{#1}}
\def\frac@timer@visible#1#2#3#4{%
    % #1 : duration of the timer
    % #2 : fraction of circle at the end of the timer
    % #3 : color of the circle
    % #4 : Start angle
    % #5 : initial angle
    \edef\frameNumber{\number\numexpr\FPS*#1\relax}
    \edef\increment{\number\numexpr3600/\frameNumber\relax}
    \edef\NewFrameNumber{\number\numexpr\frameNumber+1\relax}
            \begin{animateinline}[autoplay]{\FPS}
                \multiframe{\NewFrameNumber}{rtheta=0+0.1*\increment}{%
                \begin{tikzpicture}
                    \coordinate(O)at(0,0);
                    \coordinate(A)at(90:1.5);
                    \draw[#3, fill=#3](O)--(A)arc(90:{90+#4+\rtheta*#2}:1.5)--(O);
                    \draw[vscode-gray](O)circle(1.6);
                \end{tikzpicture}
                }
            \end{animateinline}
    }

\def\frac@timer@unvisible#1#2#3#4{%
    % #1 : duration of the timer
    % #2 : fraction of circle at the end of the timer
    % #3 : color of the circle
    % #4 : Start angle
    % #5 : initial angle
    % \edef\frameNumber{\number\numexpr\FPS*#1\relax}
    % \edef\increment{\number\numexpr3600/\frameNumber\relax}
    % \edef\NewFrameNumber{\number\numexpr\frameNumber+1\relax}
    %         \begin{animateinline}[autoplay]{\FPS}
                % \multiframe{\NewFrameNumber}{rtheta=0+0.1*\increment}{%
                \begin{tikzpicture}
                    \coordinate(O)at(0,0);
                    \coordinate(A)at(90:1.5);
                    \draw[#3, fill=#3](O)--(A)arc(90:{90}:1.5)--(O);
                    \draw[vscode-gray](O)circle(1.6);
                \end{tikzpicture}
                % }
            % \end{animateinline}
    }
\newif\ifvisible
\def\FracTimer#1#2#3#4{%
    \ifvisible
        \frac@timer@visible{#1}{#2}{#3}{#4}%
    \else
        \frac@timer@unvisible{#1}{#2}{#3}{#4}%
    \fi
    }
\def\addTimer#1{\FracTimer{#1}{1}{vscode-crimson}{0}}

\AtBeginDocument{%
    \rmfamily\color{vscode-yellow}\Huge%
    \setlength\columnsep{20pt}%
    }

\renewcommand\mathfamilydefault{\rmdefault}

\setbeamersize{text margin left=50pt}
\setbeamercolor{frametitle}{fg=vscode-green, bg=vscode-gray}
\setbeamercolor{background canvas}{bg=vscode-gray}
\setbeamertemplate{navigation symbols}{}

\long\def\calcTimedFrame[#1]#2{%
    \begin{frame}\transduration{0.25}
        \frametitle{\rmfamily\Large\qf@title}
        \par
        \begin{minipage}[c]{.65\linewidth}
            \item #2
        \end{minipage}\hspace{0.02\linewidth}
        \begin{minipage}[c]{.3\linewidth}
            \addTimer{#1}
        \end{minipage}
    \end{frame}
}
\long\def\timedFrame[#1]#2{%
    \begin{frame}\transduration{0.25}
        \frametitle{\rmfamily\Large\qf@title}
        \par
        \begin{minipage}[c]{.65\linewidth}%
            #2%
        \end{minipage}\hspace{0.02\linewidth}
        \begin{minipage}[c]{.3\linewidth}
            \addTimer{#1}
        \end{minipage}
    \end{frame}
}

\long\def\twoTimedFrame#1#2#3{%
    \begin{frame}\transduration{0.25}
        \frametitle{\rmfamily\Large\qf@title}
        \par
        \begin{minipage}[c]{.65\linewidth}%
            #2{\color{vscode-gray}\par#3}
        \end{minipage}\hspace{0.02\linewidth}
        \begin{minipage}[c]{.3\linewidth}
            \FracTimer{#1}{0.5}{vscode-crimson}{0}
        \end{minipage}
    \end{frame}
    \begin{frame}\transduration{0.25}
        \frametitle{\rmfamily\Large Test}
        \par
        \begin{minipage}[c]{.65\linewidth}%
            #2{\par\color{vscode-blue}#3}
        \end{minipage}\hspace{0.02\linewidth}
        \begin{minipage}[c]{.3\linewidth}
            \FracTimer{#1}{0.5}{vscode-blue}{180}
        \end{minipage}
    \end{frame}}

\long\def\ABCFrame#1#2[A=#3,B=#4,C=#5]{%
\twoTimedFrame{#1}{#2}{\bigskip
    A = #3\par\smallskip\noindent
    B = #4\par\smallskip\noindent
    C = #5}}

\newenvironment{calclist}[1][vscode-blue]{%
    \begin{enumerate}[label=\textbf{\color{#1}\alph*)}]%
    }{%
    \end{enumerate}
}

\pgfkeys{%
    /columnsvspace/.cd,%
    vspace/.store in=\columnsvspace,
    vspace = 50pt}

\newcommand{\setCalcList}[2][]{%
    \pgfkeys{/columnsvspace/.cd,#1}
    \begin{calclist}
        \foreach\duration/\calcul in {#2}{%
            \calcTimedFrame[\duration]{\calcul}
        }
    \end{calclist}
    \begingroup
    \color{vscode-gray}
    \setbeamercolor{background canvas}{bg=vscode-yellow}
    \begin{frame}
        \begin{calclist}[vscode-crimson]
            \begin{multicols}{2}\large
                \foreach\duration/\calcul in {#2}{%
                    \item\calcul\vspace{\columnsvspace}
                    }
            \end{multicols}
        \end{calclist}
    \end{frame}
    \endgroup
}
\long\def\consignes#1{%
    \begin{frame}\frametitle{\rmfamily\Large\qf@title}
        #1
    \end{frame}
}
\newenvironment{flashframe}{\begin{frame}\frametitle{\rmfamily\Large\qf@title}}{\end{frame}}


\def\twocolsenum#1#2{%
    \begingroup\newcounter{savedenumi}
    \begin{columns}
        \column{0.5\textwidth}
        \begin{enumerate}
            #1
            \setcounter{savedenumi}{\value{enumi}}
        \end{enumerate}
        \column{0.5\textwidth}
        \begin{enumerate}
            \setcounter{enumi}{\value{savedenumi}}
            #2
        \end{enumerate}
    \end{columns}
    \endgroup
}
\makeatother
