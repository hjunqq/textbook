"""
智慧水利教材转换器 - LaTeX模板生成器
软件工程设计：模板方法模式
"""

from typing import List
from converter_config import ConverterConfig

class LaTeXTemplateGenerator:
    """LaTeX模板生成器"""
    
    def __init__(self, config: ConverterConfig):
        self.config = config
    
    def generate_main_template(self) -> str:
        """生成主LaTeX模板"""
        template = f"""\\documentclass[{self.config.font_size},{self.config.paper_size}]{{{self.config.documentclass}}}

% 基础包配置
\\usepackage[UTF8]{{ctex}}
\\usepackage{{xeCJK}}
\\setCJKmainfont{{{self.config.font_family}}}

% 页面设置
\\usepackage[a4paper,margin=2.5cm]{{geometry}}
\\usepackage{{setspace}}
\\onehalfspacing

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

% 告警框包
\\usepackage{{tcolorbox}}
\\tcbuselibrary{{breakable}}

% 定义Pandoc需要的命令
\\providecommand{{\\tightlist}}{{%
  \\setlength{{\\itemsep}}{{0pt}}\\setlength{{\\parskip}}{{0pt}}}}

% 页眉页脚
\\usepackage{{fancyhdr}}
\\pagestyle{{fancy}}
\\fancyhf{{}}
\\fancyhead[C]{{智慧水利平台架构与开发}}
\\fancyfoot[C]{{\\thepage}}

% 超链接
\\usepackage{{hyperref}}
\\hypersetup{{
    colorlinks=true,
    linkcolor=black,
    citecolor=black, 
    urlcolor=blue,
    pdfborder={{0 0 0}}
}}

% 代码样式配置
\\lstset{{
    basicstyle=\\ttfamily\\small,
    backgroundcolor=\\color{{gray!10}},
    frame=single,
    breaklines=true,
    numbers=left,
    numberstyle=\\tiny\\color{{gray}},
    keywordstyle=\\color{{blue}},
    commentstyle=\\color{{green!60!black}},
    stringstyle=\\color{{red}},
    showstringspaces=false,
    tabsize=2
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

% 目录
\\tableofcontents
\\newpage

% 前言
\\input{{chapters/preface.tex}}

{self._generate_chapter_inputs()}

\\end{{document}}"""
        
        return template
    
    def _generate_chapter_inputs(self) -> str:
        """生成章节输入命令"""
        inputs = []
        for i in range(1, self.config.chapter_count + 1):
            inputs.append(f"\\input{{chapters/chapter{i:02d}.tex}}")
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