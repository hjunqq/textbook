"""集中存放转换器使用的常量、正则与模板配置。"""
from __future__ import annotations
import re
from pathlib import Path

# 章节顺序映射
CHAPTER_ORDER = {
    'chapter01': {'title': '第一章 智慧水利概述与平台架构基础'},
    'chapter02': {'title': '第二章 软件工程基础与需求分析'},
    'chapter03': {'title': '第三章 版本控制系统'},
    'chapter04': {'title': '第四章 系统开发技术基础'},
    'chapter05': {'title': '第五章 后端开发技术'},
    'chapter06': {'title': '第六章 前端开发技术'},
    'chapter07': {'title': '第七章 智慧水利三维场景构建'},
    'chapter08': {'title': '第八章 系统优化与维护'},
    'chapter09': {'title': '第九章 典型应用'},
}

# 需要整段删除的节标题（行级剔除）
UNNECESSARY_SECTION_PATTERNS = [
    r'^##\s+本章小结.*$',
    r'^##\s+重点难点.*$', 
    r'^##\s+思考题与练习.*$',
    r'^##\s+本节小结.*$',
    r'^##\s+参考文献.*$',
    r'^##\s+配套资源.*$',
    r'^##\s+许可证.*$',
    r'^##\s+联系方式.*$',
    r'^##\s+技术支持.*$',
    r'^##\s+软件.*$',
    r'^##\s+版权声明.*$',
    r'^##\s+编写背景.*$',
    r'^##\s+编写目标.*$',
    r'^##\s+适用对象.*$',
    r'^##\s+主要特色.*$',
    r'^##\s+内容结构.*$',
    r'^##\s+使用建议.*$',
    r'^##\s+贡献指南.*$',
]

# 需要按区块删除的模式（filter_unnecessary_content 使用）
SECTION_BLOCK_REMOVE_PATTERNS = [
    r'##\s+本章小结.*?(?=\n##|\n#|\Z)',
    r'##\s+重点难点.*?(?=\n##|\n#|\Z)',
    r'##\s+思考题与练习.*?(?=\n##|\n#|\Z)',
    r'##\s+本节小结.*?(?=\n##|\n#|\Z)',
    r'##\s+参考文献.*?(?=\n##|\n#|\Z)',
]

# 图片路径归一化替换模式
IMAGE_PATH_PATTERNS = [
    (r'!\[([^\]]*)\]\(\.\./images/([^)]+)\)', r'![\1](images/\2)'),
    (r'!\[([^\]]*)\]\(\./(images/[^)]+)\)', r'![\1](\2)'),
    (r'!\[([^\]]*)\]\(images/([^)]+)\)', r'![\1](images/\2)'),
    (r'!\[([^\]]*)\]\([^/]*/(images/[^)]+)\)', r'![\1](\2)'),
    (r'!\[([^\]]*)\]\(docs/chapters/images/([^)]+)\)', r'![\1](images/\2)'),
    (r'!\[([^\]]*)\]\(docs/assets/images/([^)]+)\)', r'![\1](images/\2)'),
    (r'!\[([^\]]*)\]\(chapters/images/([^)]+)\)', r'![\1](images/\2)'),
    (r'!\[([^\]]*)\]\((?!images/)([^/\s][^)]*\.(png|jpg|jpeg|gif|svg|bmp|webp))\)', r'![\1](images/\2)'),
]

# YAML front matter 正则
YAML_FRONTMATTER_RE = re.compile(r'^---\s*\n.*?\n---\s*(\n|$)', re.DOTALL)

# Pandoc 输入格式能力集合
# gfm 模式下不支持: grid_tables, header_attributes, implicit_figures
# 如需这些特性，可换用 markdown+yaml_metadata_block+... 组合。暂时保持最安全子集以先成功生成。
PANDOC_FROM_FORMAT = 'gfm+emoji+pipe_tables+fenced_divs+definition_lists'

# 保护性注释
PROTECTIVE_COMMENT = '% merged markdown (no YAML)\n'

# Admonition 类型映射（后续可用于 LaTeX tcolorbox 转换）
ADMONITION_TYPES = {
    'note':   {'title_cn': '注意', 'color': 'blue'},
    'info':   {'title_cn': '信息', 'color': 'cyan'},
    'tip':    {'title_cn': '提示', 'color': 'green'},
    'warning':{'title_cn': '警告', 'color': 'orange'},
    'important':{'title_cn': '重要', 'color': 'red'},
}

# Admonition 原始语法正则（!!! type "Title" 形式）
ADMONITION_RE = re.compile(r'^!!!\s+(?P<kind>\w+)(?:\s+"(?P<title>[^"]+)")?\s*$', re.MULTILINE)

# LaTeX tcolorbox 模板（placeholder 替换）
TCOLORBOX_TPL = (
    r"\\begin{{tcolorbox}}[colback={color}!5,colframe={color}!60,title=\\textbf{{{title}}}]\n"
    r"{body}\n\\end{{tcolorbox}}\n"
)

# 是否启用 admonition 转换（可由主脚本切换）
ENABLE_ADMONITION = True

# 模板文件（可选使用外部文件，当前保留常量以便快速引用）
TEMPLATE_FILE_NAME = 'book_template.tex'

def load_template(search_dir: Path) -> str | None:
    """从给定目录递归查找模板文件。没找到返回 None。"""
    candidate = search_dir / TEMPLATE_FILE_NAME
    if candidate.exists():
        return candidate.read_text(encoding='utf-8')
    return None
