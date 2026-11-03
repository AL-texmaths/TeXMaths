# Sujet blanc de mathématiques

- Jour : Décembre 2026
- Durée : 2h
- Total : 20 points
- Présentation : 2 points
- Format : DNB

## Exercice 1

- Source : exercice-0938-data.tex
- Points : 6

```latex
\medskip

Cet exercice est un questionnaire à choix multiples (QCM).

Pour chaque question, \textbf{une seule} des trois réponses proposées est exacte.

\textbf{Sur la copie, indiquer le numéro de la question et la réponse A, B ou C choisie.}

\textbf{Aucune justification n'est demandée.}

Aucun point ne sera enlevé en cas de mauvaise réponse.

\begin{center}
\begin{tabularx}{\linewidth}{|c|m{5cm}|*{3}{>{\centering \arraybackslash}X|}}\hline
\multicolumn{2}{|c|}{Questions}&Réponse A&Réponse B&Réponse C\\ \hline
1&Dans un tableur, quelle formule faut-il saisir dans la cellule D1 pour afficher la somme des nombres des cellules A1, B1 et C1 ?

\begin{tabular}{|*{5}{c|}}\hline
	&A&B&C&D\\ \hline
1	&3&5&4&\\ \hline
\end{tabular}&=somme(A1:~C1)&=(A1:~C1)&somme(A1*C1)\\ \hline
2&Soit la série de nombres:

15 ; 10 ; 13 ; 9 ; 10 ; $x$.

La moyenne de la série est 11 pour $x$
égal à \ldots&9&10&11\\ \hline
3&Sur la Terre, l'équateur est:&un méridien&un demi-cercle&un parallèle\\ \hline
4&Le volume exact, en cm$^3$, d'une boule de $6$~cm de diamètre est :

{\footnotesize On rappelle le volume $V$ d'une boule de rayon $R$
: $V = \dfrac{4\pi R^3}{3}$}\rule[-3mm]{0mm}{9mm}&$36\pi$&\np{113,0973355}&$288\pi$\\ \hline
\end{tabularx}
\end{center}

\bigskip
```

## Exercice 2

- Source : exercice-0700-data.tex
- Points : 6

```latex
On s'intéresse au motif dessiné ci-dessous que l'on retrouve dans un pavage
recouvrant un mur du palais de l'Alhambra en Espagne.\par\noindent
Ce motif est partagé en douze losanges superposables numérotés de 1 à 12. Dans
chaque losange, les côtés ont pour longueur 5cm, les angles aigus mesurent
$60^\circ$ et les angles obtus mesurent $120^\circ$.
\begin{center}
    Le motif\par\vskip7pt
    \begin{tikzpicture}[line width=0.7pt, scale=1.5]
        \coordinate[label=below:\mathspoint{A}](A)at(0,0);
        \foreach\i in{0,...,5}{
            \coordinate(A\i)at(\i*60:1);
            \coordinate(B\i)at(\i*60+30:{sqrt(3)});
            \coordinate(C\i)at(\i*60:2);
        }
        \fill[\currentcolor!50](A)--(A0)--(B0)--(C1)--(B1)--(A2)--cycle;
        \foreach\i in{1,...,5}{
            \path(A\i)--(C\i)coordinate[midway](E\i);
            \draw(E\i)circle(3.5pt)node{\footnotesize\number\numexpr2*\i};
        }
        \path(A0)--(C0)coordinate[midway](E0);
        \draw(E0)circle(3.5pt)node{\footnotesize 12};
        \tkzMarkAngle[size=0.25](A0,A,A1)
        \tkzLabelAngle[pos=0.5](A0,A,A1){$60^\circ$}
        \tkzMarkAngle[size=0.2](B0,A0,A)
        \tkzLabelAngle[pos=0.35](B0,A0,A){$120^\circ$}
        \foreach\i in{0,...,4}{
            \edef\j{\number\numexpr\i+1}
            \draw(A)--(A\i)--(B\i)--(A\j);
            \path(A)--(B\j)coordinate[midway](D\j);
            \draw(D\j)circle(3.5pt)node{\footnotesize\number\numexpr2*\j+1};
        }
        \path(A)--(B0)coordinate[midway](D'0);
        \coordinate(D0)at($(D'0)+(-0.15,0.15)$);
        \draw(D0)circle(3.5pt)node{\footnotesize 1};
        \draw(A)--(A5)--(B5)--(A0);
        \draw[dotted,line width=1.5pt](C0)--(C1)--(C2)--(C3)--(C4)--(C5)--cycle;
        \draw (A0) node[right] {\mathspoint{B}};
        \draw (B0) node[above right] {\mathspoint{C}};
        \draw (C1) node[above right] {\mathspoint{D}};
        \draw (B1) node[above] {\mathspoint{E}};
        \draw (A2) node[above left] {\mathspoint{F}};
        \path(A)--(A0)node[midway,below]{5 cm};
    \end{tikzpicture}
\end{center}
\begin{flushleft}
    \textbf{Partie 1}\par\medskip\noindent
    Dans cette partie, aucune justification n'est demandée.
\end{flushleft}
\begin{enumerate}
    \item Quelle est l'image du losange \circled1 par la symétrie centrale
    de centre A~?
    \item Quelle est l'image du losange \circled3 par la symétrie axiale
    d'axe \mathspoint{(AF)}~?
    \item Quelle est l'image du losange \circled7 par la rotation
    de centre \mathspoint{A} que transforme le losange \circled3 en losange
    \circled{11}~?
    \item Quelle est l'image du losange \circled8 par la translation qui
    transforme \mathspoint{A} en \mathspoint{E}.
\end{enumerate}
\begin{flushleft}
    \textbf{Partie 2}\par\medskip\noindent
    Louis a remarqué que le motif donné sans l'énoncé s'obtient à partir de
    l'hexagone \mathspoint{ABCDE} en appliquant plusieurs fopis la même
    rotation de centre A.\par\noindent
    Il souhaite tracer le motif avec le logiciel Scratch en prenant 10 pas
    pour 1 cm.
\end{flushleft}
\noindent
\begin{minipage}[c]{.55\linewidth}
    Le bloc dont le script est proposé ci-contre permet de tracer la figure
    représentée ci-dessous sur laquelle la flèche indique l'orientation du
    lutin au début du programme~:
    \begin{center}
        \begin{tikzpicture}[scale=1.5]
            \coordinate[label=below left:\mathspoint{A}](A)at(-120:1);
            \coordinate[label=below right:\mathspoint{B}](B)at(-60:1);
            \coordinate[label=right:\mathspoint{C}](C)at(0:1);
            \coordinate[label=above right:\mathspoint{D}](D)at(60:1);
            \coordinate[label=above left:\mathspoint{E}](E)at(120:1);
            \coordinate[label=left:\mathspoint{F}](F)at(180:1);
            \draw[fill=\currentcolor!50](A)--(B)--(C)--(D)--(E)--(F)--cycle;
            \path(A)--(B)coordinate[pos=0.45](A');
            \path(A)--(B)coordinate[pos=2](B');
            \draw[line width=1.5 pt,-latex](A)--(A');
            \draw[dotted,line width=1pt](B)--(B');
        \end{tikzpicture}
    \end{center}
\end{minipage}\hfill
\begin{minipage}[c]{.4\linewidth}
    \begin{scratch}[num blocks]
        \initmoreblocks{définir \namemoreblocks{hexagone ABCDEF}}
        \blockpen{stylo en position d'écriture}
        \blockrepeat{répéter \ovalnum{...} fois}{
            \blockmove{avancer de \ovalnum{...} pas}
            \blockmove{tourner \turnleft\ de \ovalnum{...} degrés}
        }
        \blockpen{relever le stylo}
    \end{scratch}
\end{minipage}
\begin{enumerate}
    \item Sur l'ANNEXE, à rendre avec la copie, compléter les lignes 3, 4
    et 5 afin que le bloc \guillemets{hexagone ABCDEF} trace l'hexagone
    ABCDEF de côté 5 cm en partant du point A.\par\medskip\noindent
    Aucune justification n'est attendue.
    \item Parmi les trois scripts proposés ci-dessous, lequel permet de
    tracer le motif en utilisant le bloc hexagone ABCDEF précédent.\par\medskip\noindent
    Aucune justification n'est attendue.
\end{enumerate}
\begin{flushleft}
    \textit{On rappelle que l'instruction }\begin{scratch}
    \blockmove{s'orienter à \ovalnum{90} degrés}\end{scratch}
    \textit{ signifie que le lutin se dirige vers la droite.}
\end{flushleft}\noindent\medskip
\begin{tblr}{colspec=*{3}{Q[c,m]},hlines,vlines,row{1}={font=\bfseries}}
    Script A&Script B&Script C\\
    \begin{scratch}
        \blockinit{quand \greenflag est cliqué}
        \blockmove{s'orienter à \ovalnum{90} degrés}
        \blockrepeat{répéter \ovalnum{2} fois}{
            \blockmoreblocks{Hexagone}
            \blockmove{tourner \turnleft\ de \ovalnum{120} degrés}
        }
    \end{scratch}&
    \begin{scratch}
        \blockinit{quand \greenflag est cliqué}
        \blockmove{s'orienter à \ovalnum{90} degrés}
        \blockrepeat{répéter \ovalnum{4} fois}{
            \blockmoreblocks{Hexagone}
            \blockmove{tourner \turnleft\ de \ovalnum{90} degrés}
        }
    \end{scratch}&
    \begin{scratch}
        \blockinit{quand \greenflag est cliqué}
        \blockmove{s'orienter à \ovalnum{90} degrés}
        \blockrepeat{répéter \ovalnum{6} fois}{
            \blockmoreblocks{Hexagone}
            \blockmove{tourner \turnleft\ de \ovalnum{60} degrés}
        }
    \end{scratch}
\end{tblr}
```

## Exercice 3

- Source : exercice-0615-data.tex
- Points : 6

```latex
Pour chaque nombre, écrire trois de ses multiples.
\begin{enumerate}
    \item 7
    \item 13
    \item 10
    \item 25
\end{enumerate}
```
