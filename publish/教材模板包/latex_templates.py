# -*- coding: utf-8 -*-
"""
LaTeX模板配置文件
将所有长文本和模板从主代码中分离出来
"""

# LaTeX文档模板
LATEX_TEMPLATE = r'''\documentclass[12pt,a4paper]{ctexart}

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

% 定义Pandoc生成的命令
\providecommand{\tightlist}{%
  \setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}

\begin{document}

'''

# 章节映射配置
CHAPTER_MAPPING = {
    'preface': {'title': '前言', 'file': '前言.md'},
    'chapter01': {'title': '第1章 智慧水利概述', 'file': 'chapters/chapter01/chapter01.md'},
    'chapter02': {'title': '第2章 物联网技术基础', 'file': 'chapters/chapter02/chapter02.md'},
    'chapter03': {'title': '第3章 大数据技术架构', 'file': 'chapters/chapter03/chapter03.md'},
    'chapter04': {'title': '第4章 云计算平台搭建', 'file': 'chapters/chapter04/chapter04.md'},
    'chapter05': {'title': '第5章 人工智能应用', 'file': 'chapters/chapter05/chapter05.md'},
    'chapter06': {'title': '第6章 数字孪生技术', 'file': 'chapters/chapter06/chapter06.md'},
    'chapter07': {'title': '第7章 系统集成与优化', 'file': 'chapters/chapter07/chapter07.md'},
    'chapter08': {'title': '第8章 安全与运维', 'file': 'chapters/chapter08/chapter08.md'},
    'chapter09': {'title': '第9章 案例分析与实践', 'file': 'chapters/chapter09/chapter09.md'},
}

# 正则表达式模式
ADMONITION_PATTERNS = {
    'note': {
        'pattern': r'(?ms)^!!! note(?:\s+"([^"]*)")?\s*\n(.*?)(?=\n##|\n!!! |\Z)',
        'color': 'blue',
        'title_default': '注意'
    },
    'tip': {
        'pattern': r'(?ms)^!!! tip(?:\s+"([^"]*)")?\s*\n(.*?)(?=\n##|\n!!! |\Z)',
        'color': 'green', 
        'title_default': '提示'
    },
    'warning': {
        'pattern': r'(?ms)^!!! warning(?:\s+"([^"]*)")?\s*\n(.*?)(?=\n##|\n!!! |\Z)',
        'color': 'orange',
        'title_default': '警告'
    },
    'info': {
        'pattern': r'(?ms)^!!! info(?:\s+"([^"]*)")?\s*\n(.*?)(?=\n##|\n!!! |\Z)',
        'color': 'cyan',
        'title_default': '信息'
    },
    'important': {
        'pattern': r'(?ms)^!!! important(?:\s+"([^"]*)")?\s*\n(.*?)(?=\n##|\n!!! |\Z)',
        'color': 'red',
        'title_default': '重要'
    }
}

# tcolorbox模板
TCOLORBOX_TEMPLATE = r'''\begin{{tcolorbox}}[colback={color}!5!white,colframe={color}!75!black,title={title}]
{content}
\end{{tcolorbox}}

'''

# 日志配置
LOG_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(levelname)s - %(message)s'
}

# Pandoc参数
PANDOC_ARGS = [
    '--from=markdown',
    '--to=latex',
    '--listings',
    '--number-sections'
]

# LaTeX编译参数
LATEX_COMPILE_ARGS = [
    '-interaction=nonstopmode',
    '-halt-on-error',
    '-file-line-error',
    '-synctex=1'
]
