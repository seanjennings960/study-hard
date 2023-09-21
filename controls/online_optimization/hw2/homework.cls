
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{homework}[2023/09/12 Homework]
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
\ProcessOptions\relax
\LoadClass{article}
\RequirePackage[margin=1in]{geometry}
\RequirePackage{fancyhdr}
\RequirePackage[sf,compact,small,uppercase]{titlesec}
\RequirePackage{enumitem}
\RequirePackage{graphicx}
\RequirePackage{listings, xcolor}
\RequirePackage{mathsymb}


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Add codeword command to write code in blue color.
\newcommand{\codeword}[1]{
    \texttt{\textcolor{blue}{#1}}
}
\lstset{language=C,keywordstyle={\bfseries \color{blue}}}
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


% Load images from Images folder by default.
\graphicspath{{Images/}}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Custom environments for shorthand
\newenvironment{letterenum}{\begin{enumerate}[label=\alph*)]}{\end{enumerate}}
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Use fancyhdr to implement custom homework-specific header.
\gdef\@author{\empty}
\gdef\@title{\empty}
\gdef\@class{\empty}
\newcommand{\class}[1]{\gdef\@class{#1}}
\renewcommand{\author}[1]{\gdef\@author{#1}}
\renewcommand{\title}[1]{\gdef\@title{#1}}
\renewcommand{\maketitle} {%
    \pagestyle{fancy}
    \fancyhead[LO,L]{\@author}
    \fancyhead[CO,C]{{\@class} - \@title}
    \fancyhead[RO,R]{\@date}
    \fancyfoot[LO,L]{}
    \fancyfoot[CO,C]{\thepage}
    \fancyfoot[RO,R]{}
    \renewcommand{\headrulewidth}{0.4pt}
    \renewcommand{\footrulewidth}{0.4pt}
}
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

