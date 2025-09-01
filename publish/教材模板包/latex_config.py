# -*- coding: utf-8 -*-
"""
LaTeX转换器配置文件
包含模板、章节映射和各种配置项
"""

# 章节映射配置
CHAPTER_MAPPING = {
    'preface': {
        'title': '前言', 
        'files': ['前言.md']
    },
    'chapter01': {
        'title': '第1章 智慧水利概述与平台架构基础', 
        'files': [
            'chapters/chapter01/chapter01.md',
            'chapters/chapter01/section01-01.md',
            'chapters/chapter01/section01-02.md',
            'chapters/chapter01/section01-03.md'
        ]
    },
    'chapter02': {
        'title': '第2章 物联网技术基础', 
        'files': ['chapters/chapter02/chapter02.md']
    },
    'chapter03': {
        'title': '第3章 大数据技术架构', 
        'files': ['chapters/chapter03/chapter03.md']
    },
}

# LaTeX文档模板
LATEX_TEMPLATE = r'''\documentclass[12pt,a4paper]{ctexbook}

% 中文支持
\usepackage[UTF8]{ctex}

% 基础包
\usepackage{amsmath,amssymb}
\usepackage{graphicx}
\usepackage{xcolor}
\usepackage{geometry}
\usepackage{hyperref}

% 页面设置
\geometry{
    top=2.5cm,
    bottom=2.5cm,
    left=2.8cm,
    right=2.2cm
}

% 字体设置
\setCJKmainfont{SimSun}[BoldFont=SimHei, ItalicFont=KaiTi]
\setCJKsansfont{SimHei}
\setCJKmonofont{FangSong}

% 代码环境
\usepackage{listings}
\lstset{
    basicstyle=\ttfamily\footnotesize,
    frame=single,
    breaklines=true,
    showstringspaces=false,
    numbers=left,
    numberstyle=\tiny,
    backgroundcolor=\color{gray!10}
}

% 美化框架
\usepackage{tcolorbox}
\tcbuselibrary{skins,breakable}

% 列表环境增强
\usepackage{enumitem}

% 表格增强
\usepackage{longtable}
\usepackage{booktabs}
\usepackage{array}

% 定义Pandoc生成的命令
\providecommand{\tightlist}{%
  \setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}

\begin{document}

CONTENT_PLACEHOLDER

\end{document}

'''

# Admonition样式配置
ADMONITION_STYLES = {
    'note': {
        'color': 'blue!5!white',
        'frame': 'blue!75!black',
        'title': '注意'
    },
    'tip': {
        'color': 'green!5!white',
        'frame': 'green!75!black',
        'title': '提示'
    },
    'warning': {
        'color': 'orange!5!white',
        'frame': 'orange!75!black',
        'title': '警告'
    },
    'info': {
        'color': 'cyan!5!white',
        'frame': 'cyan!75!black',
        'title': '信息'
    },
    'important': {
        'color': 'red!5!white',
        'frame': 'red!75!black',
        'title': '重要'
    }
}

# Admonition转换模式配置
ADMONITION_PATTERNS = {
    'note': {
        'pattern': r'!!!\s+note\s+(?:"([^"]*)")?\s*\n((?:(?:^    .*\n?)|(?:^\s*\n))*)',
        'color': 'blue',
        'title_default': '注意'
    },
    'tip': {
        'pattern': r'!!!\s+tip\s+(?:"([^"]*)")?\s*\n((?:(?:^    .*\n?)|(?:^\s*\n))*)',
        'color': 'green',
        'title_default': '提示'
    },
    'warning': {
        'pattern': r'!!!\s+warning\s+(?:"([^"]*)")?\s*\n((?:(?:^    .*\n?)|(?:^\s*\n))*)',
        'color': 'orange',
        'title_default': '警告'
    },
    'info': {
        'pattern': r'!!!\s+info\s+(?:"([^"]*)")?\s*\n((?:(?:^    .*\n?)|(?:^\s*\n))*)',
        'color': 'cyan',
        'title_default': '信息'
    },
    'important': {
        'pattern': r'!!!\s+important\s+(?:"([^"]*)")?\s*\n((?:(?:^    .*\n?)|(?:^\s*\n))*)',
        'color': 'red',
        'title_default': '重要'
    }
}

# Pandoc转换参数
PANDOC_ARGS = [
    '--from=markdown',
    '--to=latex',
    '--listings',
    '--top-level-division=chapter',
    '-V', 'documentclass=ctexbook'
]

# 内容清理模式
CLEANUP_PATTERNS = [
    # 移除HTML注释
    (r'<!--.*?-->', ''),
    # 移除多余空行
    (r'\n\n\n+', r'\n\n'),
]

# LaTeX后处理模式
LATEX_FIX_PATTERNS = [
    # 修复图片包含语句
    (r'\\includegraphics\{([^}]+)\}', r'\\includegraphics[width=0.8\\textwidth,keepaspectratio]{\1}'),
    # 修复代码块
    (r'\\begin\{verbatim\}', r'\\begin{lstlisting}'),
    (r'\\end\{verbatim\}', r'\\end{lstlisting}'),
    # 确保列表项有适当间距
    (r'\\item\s*\n\\textbf', r'\\item \\textbf'),
    # 移除多余空行
    (r'\n\n\n+', r'\n\n'),
]
