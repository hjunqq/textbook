#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LaTeX错误修复脚本 - 修复已生成的LaTeX文件中的各种问题
"""

import re
from pathlib import Path

def fix_latex_errors(tex_file_path):
    """修复LaTeX文件中的各种错误"""
    
    with open(tex_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔧 开始修复LaTeX错误...")
    
    # 1. 修复FontAwesome图标问题
    print("   修复FontAwesome图标问题...")
    
    # 移除FontAwesome包引用
    content = re.sub(r'\\usepackage\{fontawesome5?\}', '', content)
    
    # 替换所有FontAwesome图标命令
    fa_replacements = {
        r'\\faInfoCircle\\': '\\textbf{ℹ}',
        r'\\faLightbulb\\': '\\textbf{💡}',
        r'\\faExclamationTriangle\\': '\\textbf{⚠}',
        r'\\faExclamation\\': '\\textbf{!}',
        r'\\faCheck\\': '\\textbf{✓}',
        r'\\faTimes\\': '\\textbf{✗}',
    }
    
    for fa_cmd, replacement in fa_replacements.items():
        content = re.sub(fa_cmd, replacement, content, flags=re.MULTILINE)
    
    # 2. 修复破碎的tcolorbox
    print("   修复破碎的tcolorbox...")
    
    # 修复包含\\1和\\2的错误引用
    content = re.sub(
        r'\\begin\{tcolorbox\}\[colback=([^,]+), colframe=([^,]+), title=[^\\]*\\\\1\][^\\]*\\\\2\\\\end\{tcolorbox\}[^\\]*',
        lambda m: f'\\begin{{tcolorbox}}[colback={m.group(1)}, colframe={m.group(2)}, title=\\textbf{{注意}}]\n内容\n\\end{{tcolorbox}}\n',
        content,
        flags=re.MULTILINE | re.DOTALL
    )
    
    # 修复有问题的tcolorbox标题
    content = re.sub(
        r'title=\\\\fa[A-Za-z]+\\\\ \\\\1',
        'title=\\textbf{注意}',
        content
    )
    
    content = re.sub(
        r'title=\\fa[A-Za-z]+\\ \\1',
        'title=\\textbf{注意}',
        content
    )
    
    # 3. 修复特殊字符问题
    print("   修复特殊字符问题...")
    
    # 修复数学模式中的问题
    content = re.sub(r'\\\\1', '', content)
    content = re.sub(r'\\\\2', '', content)
    content = re.sub(r'\\1', '', content)
    content = re.sub(r'\\2', '', content)
    
    # 4. 修复图片路径问题
    print("   修复图片路径问题...")
    
    # 确保所有图片引用都有宽度设置
    content = re.sub(
        r'\\includegraphics\{([^}]+)\}',
        r'\\includegraphics[width=0.8\\textwidth]{\1}',
        content
    )
    
    # 修复重复的宽度设置
    content = re.sub(
        r'\\includegraphics\[width=[^]]*\]\[width=[^]]*\]',
        r'\\includegraphics[width=0.8\\textwidth]',
        content
    )
    
    # 5. 修复URL问题
    print("   修复URL格式...")
    
    # 确保URL命令正确
    content = re.sub(r'\\url\s*\{([^}]*)\}', r'\\url{\1}', content)
    
    # 6. 修复代码块问题
    print("   修复代码块格式...")
    
    # 修复verbatim环境
    content = re.sub(r'\\begin\{verbatim\}\s*\n\s*\\end\{verbatim\}', '', content, flags=re.MULTILINE)
    
    # 7. 修复空的环境
    print("   清理空环境...")
    
    # 清理空的tcolorbox
    content = re.sub(
        r'\\begin\{tcolorbox\}\[[^\]]*\]\s*\\end\{tcolorbox\}',
        '',
        content,
        flags=re.MULTILINE | re.DOTALL
    )
    
    # 8. 修复多余的空行
    print("   清理多余空行...")
    content = re.sub(r'\n{4,}', '\n\n\n', content)
    
    # 9. 最终检查和修复
    print("   最终检查...")
    
    # 确保必要的包被包含
    if '\\usepackage{amsmath}' not in content:
        content = content.replace('\\usepackage{array}', '\\usepackage{array}\n\\usepackage{amsmath}')
    
    if '\\usepackage{amssymb}' not in content:
        content = content.replace('\\usepackage{amsmath}', '\\usepackage{amsmath}\n\\usepackage{amssymb}')
    
    # 保存修复后的文件
    with open(tex_file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ LaTeX错误修复完成!")
    return content

def main():
    # 处理两个可能的位置
    possible_files = [
        Path("输出/教材.tex"),
        Path("../latex_output/教材.tex")
    ]
    
    tex_file = None
    for file_path in possible_files:
        if file_path.exists():
            tex_file = file_path
            break
    
    if not tex_file:
        print("❌ 未找到教材.tex文件")
        return
    
    print(f"📄 处理文件: {tex_file}")
    fix_latex_errors(tex_file)
    
    print(f"🎉 修复完成！文件已更新: {tex_file}")

if __name__ == "__main__":
    main()