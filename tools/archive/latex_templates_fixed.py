"""
智慧水利教材转换器 - 修复后的LaTeX模板生成器
软件工程设计：模板方法模式 + 修复tcolorbox等问题
"""

import re
from typing import List
from converter_config import ConverterConfig

class LaTeXTemplateGenerator:
    """LaTeX模板生成器 - 修复版"""
    
    def __init__(self, config: ConverterConfig):
        self.config = config
    
    def generate_main_template(self) -> str:
        """生成主LaTeX模板 - 增强版，修复包引用问题"""
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

% 告警框包 - 修复版配置
\\usepackage{{tcolorbox}}
\\tcbuselibrary{{breakable,skins}}

% 修复Pandoc生成的问题
\\providecommand{{\\tightlist}}{{%
  \\setlength{{\\itemsep}}{{0pt}}\\setlength{{\\parskip}}{{0pt}}}}

% 定义自定义环境以处理特殊情况
\\newenvironment{{admonition}}[2]{{
  \\begin{{tcolorbox}}[colback=#1!5!white,colframe=#1!75!black,title=#2]
}}{{
  \\end{{tcolorbox}}
}}

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
    pdfborder={{0 0 0}},
    unicode=true
}}

% 代码样式配置 - 增强版
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
    tabsize=2,
    breakatwhitespace=false,
    breaklines=true,
    captionpos=b,
    keepspaces=true,
    showspaces=false,
    showstringspaces=false,
    showtabs=false
}}

% 中文处理增强
\\XeTeXlinebreaklocale "zh"
\\XeTeXlinebreakskip = 0pt plus 1pt minus 0.1pt

% 修复常见的Pandoc问题
\\let\\oldsection\\section
\\renewcommand{{\\section}}{{\\clearpage\\oldsection}}

\\begin{{document}}

% 封面
\\begin{{titlepage}}
\\centering
\\vspace*{{2cm}}
{{\\Huge\\bfseries 智慧水利平台架构与开发}}\\\\[2cm]
{{\\Large 高等院校水利工程专业教材}}\\\\[4cm]
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
    """LaTeX后处理器 - 修复版"""
    
    def __init__(self):
        pass
    
    def post_process(self, latex_content: str) -> str:
        """LaTeX后处理 - 增强版"""
        
        # 首先进行基础清理
        latex_content = self._basic_cleanup(latex_content)
        
        # 然后进行语法修复
        latex_content = self._fix_latex_syntax(latex_content)
        
        # 最后进行格式优化
        latex_content = self._optimize_formatting(latex_content)
        
        return latex_content
    
    def _basic_cleanup(self, content: str) -> str:
        """基础清理"""
        # 清理多余的空行
        content = re.sub(r'\n\s*\n\s*\n', '\\n\\n', content)
        
        # 移除可能的YAML残留
        if content.startswith('---'):
            second_yaml = content.find('---', 3)
            if second_yaml != -1:
                content = content[second_yaml + 3:].lstrip('\\n')
        
        return content
    
    def _fix_latex_syntax(self, content: str) -> str:
        """修复LaTeX语法问题"""
        fixes = [
            # 修复过度转义的章节命令
            (r'\\\\textbackslash section\\\\{([^}]+)\\\\}', r'\\\\section{\\1}'),
            (r'\\\\textbackslash chapter\\\\{([^}]+)\\\\}', r'\\\\chapter{\\1}'),
            
            # 修复tcolorbox语法
            (r'\\\\textbackslash begin\\\\{tcolorbox\\\\}\\\\{\\\\\\[\\\\\\]([^}]+)\\\\{\\\\\\]\\\\}', 
             r'\\\\begin{tcolorbox}[\\1]'),
            (r'\\\\textbackslash end\\\\{tcolorbox\\\\}', r'\\\\end{tcolorbox}'),
            
            # 修复章节命令后的换行
            (r'\\\\chapter\\{([^}]+)\\}\\s*\\n', r'\\\\chapter{\\1}\\n\\n'),
            (r'\\\\section\\{([^}]+)\\}\\s*\\n', r'\\\\section{\\1}\\n\\n'),
            
            # 修复列表环境
            (r'\\n\\\\begin\\{', r'\\n\\n\\\\begin{'),
            (r'\\\\end\\{([^}]+)\\}\\n', r'\\\\end{\\1}\\n\\n'),
        ]
        
        for pattern, replacement in fixes:
            content = re.sub(pattern, replacement, content)
        
        return content
    
    def _optimize_formatting(self, content: str) -> str:
        """优化格式"""
        # 确保章节之间有适当间隔
        content = re.sub(r'(\\\\end\\{[^}]+\\})\\n(\\\\chapter)', r'\\1\\n\\n\\\\clearpage\\n\\2', content)
        
        # 优化段落间距
        content = re.sub(r'\\n\\n\\n+', '\\n\\n', content)
        
        return content

class TexFileFixer:
    """tex文件修复器 - 新增：专门处理已生成的tex文件"""
    
    def __init__(self):
        self.logger = __import__('logging').getLogger(__name__)
    
    def fix_tex_file(self, tex_file_path: str) -> bool:
        """修复单个tex文件"""
        try:
            # 读取文件
            with open(tex_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 应用修复
            fixed_content = self._apply_comprehensive_fixes(content)
            
            # 写回文件
            with open(tex_file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            
            self.logger.info(f"修复文件完成: {tex_file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"修复文件失败 {tex_file_path}: {e}")
            return False
    
    def _apply_comprehensive_fixes(self, content: str) -> str:
        """应用全面的修复"""
        
        # 1. 修复过度转义的LaTeX命令
        escape_fixes = [
            (r'\\textbackslash section\\{([^}]+)\\}', r'\\section{\\1}'),
            (r'\\textbackslash chapter\\{([^}]+)\\}', r'\\chapter{\\1}'),
            (r'\\textbackslash subsection\\{([^}]+)\\}', r'\\subsection{\\1}'),
            (r'\\textbackslash begin\\{([^}]+)\\}', r'\\begin{\\1}'),
            (r'\\textbackslash end\\{([^}]+)\\}', r'\\end{\\1}'),
        ]
        
        for pattern, replacement in escape_fixes:
            content = re.sub(pattern, replacement, content)
        
        # 2. 修复tcolorbox语法错误
        tcolorbox_fixes = [
            # 修复错误的选项语法
            (r'\\begin\\{tcolorbox\\}\\{\\[\\]([^}]+)\\{\\]\\}', r'\\begin{tcolorbox}[\\1]'),
            # 修复标题中的特殊字符
            (r'title=([^,\\]]+)', self._clean_tcolorbox_title),
        ]
        
        for pattern, replacement in tcolorbox_fixes:
            if callable(replacement):
                content = re.sub(pattern, replacement, content)
            else:
                content = re.sub(pattern, replacement, content)
        
        # 3. 修复markdown残留
        markdown_fixes = [
            (r'\\#\\#\\#', r'###'),
            (r'\\*\\*([^*]+)\\*\\*', r'\\textbf{\\1}'),
            (r'=== ``([^`]+)``', r'\\subsection{\\1}'),
        ]
        
        for pattern, replacement in markdown_fixes:
            content = re.sub(pattern, replacement, content)
        
        # 4. 清理和格式化
        content = re.sub(r'\\n\\s*\\n\\s*\\n', '\\n\\n', content)  # 多余空行
        content = re.sub(r'\\\\section\\{([^}]+)\\}\\s*\\n', r'\\section{\\1}\\n\\n', content)
        
        return content
    
    def _clean_tcolorbox_title(self, match):
        """清理tcolorbox标题中的特殊字符"""
        title = match.group(1)
        # 移除可能导致问题的字符
        title = title.replace('{', '').replace('}', '').replace('[', '').replace(']', '')
        return f'title={title}'