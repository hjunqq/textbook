"""
智慧水利教材转换器 - LaTeX模板生成器
软件工程设计：模板方法模式
"""

from typing import List
from string import Template
from converter_config import ConverterConfig

class LaTeXTemplateGenerator:
    """LaTeX模板生成器"""
    
    def __init__(self, config: ConverterConfig):
        self.config = config
    
    def generate_main_template(self) -> str:
        """生成主LaTeX模板"""
        template = """\\documentclass[{self.config.font_size},{self.config.paper_size}]{{{self.config.documentclass}}}

% 基础包配置
\\usepackage[UTF8]{{ctex}}
\\usepackage{{xeCJK}}
\\setCJKmainfont{{{self.config.font_family}}}

% 页面设置
\\usepackage[a4paper,margin=2.5cm]{{geometry}}
\\usepackage{{setspace}}
\\onehalfspacing
% 高质量排版与英文字体
\\usepackage{{microtype}}
\\usepackage{{fontspec}}
\\setmainfont{{TeX Gyre Pagella}}
\\setsansfont{{TeX Gyre Heros}}
\\setmonofont{{TeX Gyre Cursor}}

% Pandoc兼容性包
\\usepackage{{longtable,booktabs,array}}
\\usepackage{{calc}}
\\usepackage{{etoolbox}}
\\usepackage{{footnotehyper}}
\\usepackage{{graphicx}}
\\usepackage{{grffile}}
\\usepackage[normalem]{{ulem}}

% 数学包
\\usepackage{{amsmath}}
\\usepackage{{amsfonts}}
\\usepackage{{amssymb}}

% 图片包
\\usepackage{{float}}
\\usepackage{{subfigure}}

% 代码高亮包
\\usepackage{{listings}}
\\usepackage{{xcolor}}
% 主题色彩（可按需调整）
\\definecolor{Primary}{HTML}{1F4E79}
\\definecolor{Secondary}{HTML}{2E7D32}
\\definecolor{Accent}{HTML}{E67E22}

% 告警框包
\\usepackage{{tcolorbox}}
\\tcbuselibrary{{breakable}}

% 标题、列表、图题与目录细节
\\usepackage{{titlesec}}
\\usepackage{{enumitem}}
\\usepackage[labelfont=bf]{{caption}}
\\usepackage{{tocloft}}
\\setlength{\\cftbeforechapskip}{8pt}

% 中文章节样式（更显书籍风）
\\ctexset{{
  chapter = {{format=\\bfseries\\Huge, name={{第,章}}, number=\\chinese{{chapter}}, aftername=\\quad, beforeskip=20pt, afterskip=28pt}},
  section = {{format=\\bfseries\\Large}},
  subsection = {{format=\\bfseries\\large}}
}}

% 列表与段落间距优化
\\setlength{\\parindent}{2em}
\\setlength{\\parskip}{0.5em}
\\setlist{nosep}
\\setlist[itemize]{leftmargin=2em}
\\setlist[enumerate]{leftmargin=2em}

% 定义Pandoc需要的命令
\\providecommand{{\\tightlist}}{{%
  \\setlength{{\\itemsep}}{{0pt}}\\setlength{{\\parskip}}{{0pt}}}}

% 页眉页脚
\\usepackage{{fancyhdr}}
\\pagestyle{{fancy}}
\\fancyhf{{}}
\\fancyhead[C]{{智慧水利平台架构与开发}}
\\fancyfoot[C]{{\\thepage}}
\\renewcommand{{\\headrulewidth}}{{0.4pt}}

% 超链接与URL断行（避免参考文献长URL溢出）
\\usepackage{{xurl}}
\\usepackage{{hyperref}}
% 打印/屏幕双模：若定义了 \PRINTMODE，则使用黑色链接
\\makeatletter
\\@ifundefined{PRINTMODE}{%% 屏幕模式
  \\hypersetup{{colorlinks=true, linkcolor=Primary, citecolor=Primary, urlcolor=Accent, pdfborder={{0 0 0}}}}
}{%% 打印模式
  \\hypersetup{{colorlinks=true, linkcolor=black, citecolor=black, urlcolor=black, pdfborder={{0 0 0}}}}
}
\\makeatother

% 缓解长行/参考文献溢出（适度放宽）
\\tolerance=1000
\\emergencystretch=3em
\\hbadness=10000

% 代码样式配置优化
\\definecolor{{codegreen}}{{rgb}}{{0,0.6,0}}
\\definecolor{{codegray}}{{rgb}}{{0.5,0.5,0.5}}
\\definecolor{{codepurple}}{{rgb}}{{0.58,0,0.82}}
\\definecolor{{backcolour}}{{rgb}}{{0.98,0.98,0.98}}

\\lstset{{
    basicstyle=\\footnotesize\\ttfamily,
    lineskip=-1pt,
    backgroundcolor=\\color{{backcolour}},
    commentstyle=\\color{{codegreen}},
    keywordstyle=\\color{{Primary}}\\bfseries,
    numberstyle=\\tiny\\color{{codegray}},
    stringstyle=\\color{{codepurple}},
    breakatwhitespace=false,         
    breaklines=true,                 
    captionpos=b,                    
    keepspaces=true,                 
    numbers=left,                    
    numbersep=5pt,                  
    showspaces=false,                
    showstringspaces=false,
    showtabs=false,                  
    tabsize=2,
    frame=single,
    rulecolor=\\color{{gray!30}},
    aboveskip=\\smallskipamount,
    belowskip=\\smallskipamount,
    xleftmargin=8pt,
    xrightmargin=8pt,
    % HTML语言支持
    literate={{<}}{{\\textless}}1 {{>}}{{\\textgreater}}1
}}

% 行内代码优化
\\newcommand{{\\code}}[1]{{\\lstinline[basicstyle=\\small\\ttfamily]|#1|}}

% 定义HTML标签显示命令
\\newcommand{{\\htmltag}}[1]{{\\texttt{{\\textlangle#1\\textrangle}}}}

% 统一告警框风格（可覆盖 Admonition 处理器中不同颜色）
\\tcbset{{
  textbook/.style={colback=Primary!3!white, colframe=Primary!60!black, arc=1mm, boxrule=0.4pt,
    left=6pt, right=6pt, top=6pt, bottom=6pt}
}}

\\begin{{document}}

% 封面
\\begin{{titlepage}}
\\centering
\\vspace*{{2cm}}
{{\\Huge\\bfseries 智慧水利平台架构与开发}}\\\\[2cm]
{{\\Large 教材}}\\\\[4cm]
{{\\large \\today}}
\\end{{titlepage}}

% 前言置于目录之前（不编号）
\\input{{chapters/preface.tex}}
\\newpage
% 目录
\\tableofcontents
\\newpage

{self._generate_chapter_inputs()}

\\end{{document}}"""
        
        return template

    def generate_main_template_with(self, chapter_numbers: list[int]) -> str:
        """按给定章节列表生成主LaTeX模板（始终包含前言），并强化章节、目录、代码样式。"""
        input_cmd = "\\input"
        chapter_inputs = "\n".join([f"{input_cmd}{{chapters/chapter{i:02d}.tex}}" for i in chapter_numbers])

        # 使用 string.Template，避免与 LaTeX 花括号冲突
        template = Template(r"""
\documentclass[$font_size,$paper_size]{$documentclass}

% 基础与中文支持
\usepackage[UTF8]{ctex}
\usepackage{xeCJK}
\usepackage{fontspec}
% 拉丁字体（优雅且常见）
\setmainfont{TeX Gyre Pagella}
\setsansfont{TeX Gyre Heros}
% 等宽体：若系统有 Inconsolata 则优先
\IfFontExistsTF{Inconsolata}{\setmonofont{Inconsolata}}{\setmonofont{TeX Gyre Cursor}}
% 中文主字体（可自动回退）
\setCJKmainfont{$font_family}

% 页面与排版质量
\usepackage[a4paper,margin=2.5cm]{geometry}
\usepackage{setspace}
\onehalfspacing
\usepackage{microtype}

% Pandoc 兼容
\usepackage{longtable,booktabs,array}
\usepackage{calc}
\usepackage{etoolbox}
\usepackage{graphicx}
\usepackage[normalem]{ulem}

% 数学环境
\usepackage{amsmath,amsfonts,amssymb}

% 图片与浮动
\usepackage{float}

% 颜色与代码（listings）
\usepackage{xcolor}
\definecolor{Primary}{HTML}{1F4E79}
\definecolor{Accent}{HTML}{E67E22}
\definecolor{CodeBg}{rgb}{0.98,0.98,0.98}
\definecolor{CodeNum}{rgb}{0.5,0.5,0.5}
\definecolor{CodeKey}{rgb}{0.1,0.2,0.6}
\definecolor{CodeStr}{rgb}{0.58,0,0.82}
\definecolor{CodeCmt}{rgb}{0,0.5,0}
\usepackage{listings}
\lstset{
  basicstyle=\small\ttfamily,
  backgroundcolor=\color{CodeBg},
  numbers=left,
  numberstyle=\tiny\color{CodeNum},
  stepnumber=1,
  numbersep=6pt,
  frame=single,
  rulecolor=\color{gray!30},
  xleftmargin=8pt,
  xrightmargin=8pt,
  aboveskip=\smallskipamount,
  belowskip=\smallskipamount,
  breaklines=true,
  showstringspaces=false,
  keywordstyle=\color{CodeKey}\bfseries,
  commentstyle=\color{CodeCmt},
  stringstyle=\color{CodeStr},
  tabsize=2,
  keepspaces=true,
  % HTML 符号安全显示
  literate={<}{\textless}1 {>}{\textgreater}1
}

% 告警框（更现代外观）
\usepackage{tcolorbox}
\tcbuselibrary{breakable,skins}
\tcbset{textbook/.style={enhanced, breakable, colback=Primary!3!white, colframe=Primary!60!black, arc=1mm, boxrule=0.5pt, left=6pt, right=6pt, top=6pt, bottom=6pt}}

% 标题与目录样式（更高级视觉）
\usepackage{titlesec}
\usepackage{tocloft}
\usepackage{enumitem}
\usepackage[labelfont=bf,font=small]{caption}
\setcounter{tocdepth}{2}
% 章节标题（彩色分隔线风格）
\titleformat{\chapter}[display]
  {\bfseries\Huge}
  {\color{Primary} 第\chinese{chapter}章}
  {1ex}
  {\titlerule[1pt]\vspace{1ex}}
  [\vspace{-0.5ex}\titlerule]
\titlespacing*{\chapter}{0pt}{*2}{*1.5}
% 小节标题着色
\titleformat{\section}{\bfseries\Large\color{Primary}}{\thesection}{0.6em}{}
\titleformat{\subsection}{\bfseries\large\color{Primary}}{\thesubsection}{0.6em}{}

% 目录优化：字距与点引导线
\renewcommand{\cftdotsep}{1}
\setlength{\cftbeforechapskip}{8pt}
\setlength{\cftbeforesecskip}{2pt}
\renewcommand{\cftchapfont}{\bfseries}
\renewcommand{\cftchappagefont}{\bfseries}

% 列表与段落间距
\setlength{\parindent}{2em}
\setlength{\parskip}{0.5em}
\setlist{nosep}
\setlist[itemize]{leftmargin=2em}
\setlist[enumerate]{leftmargin=2em}

% Pandoc 生成的紧凑列表支持
\providecommand{\tightlist}{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}

% 页眉页脚：显示章/节题名
\usepackage{fancyhdr}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[LE]{\small \leftmark}
\fancyhead[RO]{\small \rightmark}
\fancyfoot[C]{\thepage}
\renewcommand{\headrulewidth}{0.4pt}
\setlength{\headheight}{14.5pt}

% 超链接与书签
\usepackage{xurl}
\usepackage{hyperref}
\hypersetup{colorlinks=true, linkcolor=black, citecolor=black, urlcolor=Accent, pdfborder={0 0 0}}

% 溢出容错
\tolerance=1000
\emergencystretch=3em
\hbadness=10000

% 行内代码便捷命令
\newcommand{\code}[1]{\lstinline[basicstyle=\small\ttfamily]|#1|}
% HTML 标签展示（避免依赖额外宏包）
\newcommand{\htmltag}[1]{\texttt{\textless{}#1\textgreater{}}}

\begin{document}

% 前置部分
\frontmatter
% 前言置于目录之前（不编号）
\input{chapters/preface.tex}
\newpage
\tableofcontents
\newpage

% 正文
\mainmatter
$chapter_inputs

\end{document}
""")

        return template.safe_substitute(
            font_size=self.config.font_size,
            paper_size=self.config.paper_size,
            documentclass=self.config.documentclass,
            font_family=self.config.font_family,
            chapter_inputs=chapter_inputs
        )

    def _generate_chapter_inputs(self) -> str:
        """生成章节输入命令"""
        inputs = []
        input_cmd = "\\input"
        for i in range(1, self.config.chapter_count + 1):
            inputs.append(f"{input_cmd}{{chapters/chapter{i:02d}.tex}}")
        return '\n'.join(inputs)
    
    def generate_chapter_template(self, chapter_num: int, title: str) -> str:
        """生成章节模板头部"""
        return ""  # 不添加任何头部注释，避免YAML解析问题

class LaTeXPostProcessor:
    """LaTeX后处理器"""
    
    def __init__(self):
        pass
    
    def post_process(self, latex_content: str) -> str:
        """LaTeX后处理"""
        
        # 清理多余的空行
        latex_content = re.sub(r'\n\s*\n\s*\n', '\n\n', latex_content)
        
        # 修复一些常见的LaTeX语法问题
        fixes = [
            # 修复章节命令后的换行
            (r'\\chapter\{([^}]+)\}\s*\n', r'\\chapter{\1}\n\n'),
            (r'\\section\{([^}]+)\}\s*\n', r'\\section{\1}\n\n'),
            
            # 修复列表环境
            (r'\n\\begin\{', r'\n\n\\begin{'),
            (r'\\end\{([^}]+)\}\n', r'\\end{\1}\n\n'),
            
            # 修复特殊字符转义
            (r'([^\\])&', r'\1\\&'),
            (r'([^\\])%', r'\1\\%'),
            (r'([^\\])#', r'\1\\#'),
        ]
        
        for pattern, replacement in fixes:
            latex_content = re.sub(pattern, replacement, latex_content)
        
        return latex_content

import re
