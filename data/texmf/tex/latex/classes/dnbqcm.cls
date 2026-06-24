\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{dnbqcm}

\DeclareOption*{%
    \PassOptionsToClass{\CurrentOption}{article}%
}
\DeclareOption{A5}{
    \AtEndOfClass{
        \RequirePackage[a5paper,portrait,hmargin=20pt]{geometry}
    }
}
\DeclareOption{A4}{
    \AtEndOfClass{
        \RequirePackage[portrait,hmargin=20pt]{geometry}
    }
}
\ProcessOptions\relax
\LoadClass{article}

\RequirePackage{texmaths-metadata}
\RequirePackage{texmaths-symbols}
\RequirePackage{enumitem}

\setlist[enumerate,1]{font=\bfseries, label=\arabic*)}

\pagestyle{empty}

\AtBeginDocument{
    {\centering\bfseries\Large Entraînement au DNB~: QCM\par}\bigskip\noindent
}