"""
LaTeX模板引擎模块
提供LaTeX模板的生成和渲染功能
"""

from typing import List, Dict, Tuple, Any
from pathlib import Path
from ..utils.logger import Logger

class TemplateEngine:
    """LaTeX模板引擎"""
    
    def __init__(self, config):
        self.config = config
        self.logger = Logger("TemplateEngine")
        
        # 预定义的模板
        self.templates = {
            'main': self._get_main_template(),
            'chapter': self._get_chapter_template(),
            'preface': self._get_preface_template()
        }
        
        self.logger.info("模板引擎初始化完成")
    
    def _get_main_template(self) -> str:
        """获取主文档模板"""
        return r"""% 智慧水利平台架构与开发教材
% 使用XeLaTeX编译

\documentclass[FONT_SIZE,PAPER_SIZE]{book}

% 中文支持
\usepackage[UTF8]{ctex}
\setCJKmainfont{FONT_FAMILY}

% 页面设置
\usepackage{geometry}
\geometry{
    a4paper,
    left=2.5cm,
    right=2.0cm,
    top=2.5cm,
    bottom=2.0cm
}

% 数学支持
\usepackage{amsmath,amssymb,amsfonts}
\usepackage{mathtools}

% 图片支持
\usepackage{graphicx}
\graphicspath{{IMAGES_PATH/}}

% 代码高亮
\usepackage{listings}
\usepackage{xcolor}

% 代码样式配置
\lstset{
    basicstyle=\ttfamily\small,
    numbers=left,
    numberstyle=\tiny\color{gray},
    stepnumber=1,
    numbersep=5pt,
    backgroundcolor=\color{gray!10},
    showspaces=false,
    showstringspaces=false,
    showtabs=false,
    frame=single,
    rulecolor=\color{black},
    tabsize=4,
    captionpos=b,
    breaklines=true,
    breakatwhitespace=false,
    keywordstyle=\color{blue},
    commentstyle=\color{green!60!black},
    stringstyle=\color{red},
    escapeinside={(*@}{@*)},
    morekeywords={*,...}
}

% 告警框支持
\usepackage{tcolorbox}
\tcbuselibrary{skins,breakable}

% 定义告警框样式
\newtcolorbox{noteBox}[1][]{
    colback=blue!5!white,
    colframe=blue!75!black,
    fonttitle=\bfseries,
    title=注意,
    #1
}

\newtcolorbox{tipBox}[1][]{
    colback=green!5!white,
    colframe=green!75!black,
    fonttitle=\bfseries,
    title=提示,
    #1
}

\newtcolorbox{warningBox}[1][]{
    colback=orange!5!white,
    colframe=orange!75!black,
    fonttitle=\bfseries,
    title=警告,
    #1
}

% 表格支持
\usepackage{array,booktabs,longtable}
\usepackage{multirow,multicol}

% 链接支持
\usepackage{hyperref}
\hypersetup{
    colorlinks=true,
    linkcolor=black,
    filecolor=magenta,      
    urlcolor=cyan,
    citecolor=green,
    pdftitle={智慧水利平台架构与开发},
    pdfauthor={智慧水利教材编写组},
    pdfsubject={智慧水利平台架构与开发},
    pdfkeywords={智慧水利,平台架构,软件开发}
}

% 目录设置
\usepackage{titletoc}

% 页眉页脚
\usepackage{fancyhdr}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[LE,RO]{\thepage}
\fancyhead[LO]{\rightmark}
\fancyhead[RE]{\leftmark}

% 章节样式
\usepackage{titlesec}

% 浮动体设置
\usepackage{float}
\restylefloat{table}
\restylefloat{figure}

% 避免孤立行
\widowpenalty=1000
\clubpenalty=1000

% Pandoc兼容性
\providecommand{\tightlist}{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}

\begin{document}

% 标题页
\begin{titlepage}
\centering
{\Huge \textbf{智慧水利平台架构与开发}}
\vspace{2cm}

{\Large 教材编写组}
\vspace{1cm}

{\large \today}
\end{titlepage}

% 目录
\frontmatter
\tableofcontents
\listoffigures
\listoftables

% 正文
\mainmatter

CHAPTER_INCLUDES

% 后记
\backmatter

\end{document}
"""
    
    def _get_chapter_template(self) -> str:
        """获取章节模板"""
        return r"""CONTENT
"""
    
    def _get_preface_template(self) -> str:
        """获取前言模板"""
        return r"""\chapter*{前言}
\addcontentsline{toc}{chapter}{前言}

CONTENT
"""
    
    def render_main_template(self, chapter_files: List[Tuple[str, str]]) -> str:
        """渲染主模板"""
        self.logger.info(f"渲染主模板，包含 {len(chapter_files)} 个章节")
        
        # 生成章节包含语句
        chapter_includes = []
        for filename, title in chapter_files:
            chapter_includes.append(f"\\input{{chapters/{filename}}}")
        
        chapter_includes_str = '\n'.join(chapter_includes)
        
        # 使用字符串替换渲染模板
        template = self.templates['main']
        rendered = template.replace('FONT_FAMILY', self.config.font_family)
        rendered = rendered.replace('FONT_SIZE', self.config.font_size)  
        rendered = rendered.replace('PAPER_SIZE', self.config.paper_size)
        rendered = rendered.replace('IMAGES_PATH', '../docs/assets/images')
        rendered = rendered.replace('CHAPTER_INCLUDES', chapter_includes_str)
        
        self.logger.info("主模板渲染完成")
        return rendered
    
    def render_chapter_template(self, chapter_num: int, title: str, content: str) -> str:
        """渲染章节模板"""
        self.logger.info(f"渲染第{chapter_num}章模板: {title}")
        
        template = self.templates['chapter']
        rendered = template.replace('CONTENT', content)
        
        self.logger.info(f"第{chapter_num}章模板渲染完成")
        return rendered
    
    def render_preface_template(self, title: str, content: str) -> str:
        """渲染前言模板"""
        self.logger.info("渲染前言模板")
        
        template = self.templates['preface']
        rendered = template.replace('CONTENT', content)
        
        self.logger.info("前言模板渲染完成")
        return rendered
    
    def register_template(self, name: str, template_content: str):
        """注册自定义模板"""
        self.templates[name] = template_content
        self.logger.info(f"注册模板: {name}")
    
    def get_template(self, name: str) -> str:
        """获取模板"""
        if name not in self.templates:
            raise ValueError(f"模板 '{name}' 不存在")
        return self.templates[name]
    
    def load_template_from_file(self, template_path: Path) -> str:
        """从文件加载模板"""
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            self.logger.error(f"加载模板文件失败: {template_path}, 错误: {e}")
            raise
    
    def save_template_to_file(self, template_content: str, output_path: Path):
        """保存模板到文件"""
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(template_content)
            self.logger.info(f"模板已保存到: {output_path}")
        except Exception as e:
            self.logger.error(f"保存模板文件失败: {output_path}, 错误: {e}")
            raise

class LaTeXPostProcessor:
    """LaTeX后处理器"""
    
    def __init__(self):
        self.logger = Logger("LaTeXPostProcessor")
    
    def post_process(self, latex_content: str) -> str:
        """后处理LaTeX内容"""
        self.logger.info("开始LaTeX后处理")
        
        processed = latex_content
        
        # 修复常见的LaTeX问题
        processed = self._fix_common_issues(processed)
        
        # 优化空行
        processed = self._optimize_whitespace(processed)
        
        # 修复编码问题
        processed = self._fix_encoding_issues(processed)
        
        self.logger.info("LaTeX后处理完成")
        return processed
    
    def _fix_common_issues(self, content: str) -> str:
        """修复常见LaTeX问题"""
        import re
        
        # 修复连续的空命令
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        
        # 确保环境前后有适当的空行
        content = re.sub(r'(\S)\n(\\begin\{)', r'\1\n\n\2', content)
        content = re.sub(r'(\\end\{[^}]+\})\n(\S)', r'\1\n\n\2', content)
        
        # 修复章节命令前的空行
        content = re.sub(r'\n+(\\chapter|\\section|\\subsection)', r'\n\n\1', content)
        
        return content
    
    def _optimize_whitespace(self, content: str) -> str:
        """优化空白字符"""
        import re
        
        # 移除行尾空格
        content = re.sub(r'[ \t]+\n', '\n', content)
        
        # 标准化空行
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        return content
    
    def _fix_encoding_issues(self, content: str) -> str:
        """修复编码问题"""
        # 这里可以添加特定的编码修复逻辑
        return content

class TemplateStore:
    """模板存储管理器"""
    
    def __init__(self, template_dir: Path):
        self.template_dir = template_dir
        self.logger = Logger("TemplateStore")
        self.templates = {}
        self._load_templates()
    
    def _load_templates(self):
        """加载模板目录中的所有模板"""
        if not self.template_dir.exists():
            self.logger.warning(f"模板目录不存在: {self.template_dir}")
            return
        
        for template_file in self.template_dir.glob("*.tex"):
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    template_name = template_file.stem
                    self.templates[template_name] = f.read()
                    self.logger.info(f"加载模板: {template_name}")
            except Exception as e:
                self.logger.error(f"加载模板失败: {template_file}, 错误: {e}")
    
    def get_template(self, name: str) -> str:
        """获取模板"""
        if name not in self.templates:
            raise ValueError(f"模板 '{name}' 不存在")
        return self.templates[name]
    
    def save_template(self, name: str, content: str):
        """保存模板"""
        template_path = self.template_dir / f"{name}.tex"
        try:
            self.template_dir.mkdir(parents=True, exist_ok=True)
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.templates[name] = content
            self.logger.info(f"保存模板: {name}")
        except Exception as e:
            self.logger.error(f"保存模板失败: {name}, 错误: {e}")
            raise
    
    def list_templates(self) -> List[str]:
        """列出所有模板"""
        return list(self.templates.keys())
    
    def delete_template(self, name: str):
        """删除模板"""
        if name in self.templates:
            template_path = self.template_dir / f"{name}.tex"
            try:
                if template_path.exists():
                    template_path.unlink()
                del self.templates[name]
                self.logger.info(f"删除模板: {name}")
            except Exception as e:
                self.logger.error(f"删除模板失败: {name}, 错误: {e}")
                raise
        else:
            raise ValueError(f"模板 '{name}' 不存在")