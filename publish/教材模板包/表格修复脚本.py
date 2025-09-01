#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
表格修复脚本 - 专门修复LaTeX文件中的表格问题
"""

import re
from pathlib import Path

def fix_table_issues(tex_file_path):
    """修复LaTeX文件中的表格问题"""
    
    with open(tex_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔧 开始修复表格问题...")
    
    # 1. 修复破碎的表格列定义 - 最常见的问题
    print("   修复破碎的表格列定义...")
    
    # 修复多行分割的列定义
    content = re.sub(
        r'\\begin\{longtable\}\[\]\{\s*([lcr])\s*\}\s*([lcr])\s*\}\s*([lcr])\s*\}\}',
        r'\\begin{longtable}{|\1|\2|\3|}',
        content,
        flags=re.MULTILINE | re.DOTALL
    )
    
    # 修复单行破碎列定义
    content = re.sub(
        r'\\begin\{longtable\}\[\]\{\s*([lcr])\s*([lcr])\s*([lcr])\s*\}',
        r'\\begin{longtable}{|\1|\2|\3|}',
        content,
        flags=re.MULTILINE
    )
    
    # 2. 修复复杂的列定义为简单格式
    print("   简化复杂列定义...")
    
    # 处理包含复杂计算的列定义
    content = re.sub(
        r'\\begin\{longtable\}\[\]\{@\{\}[^}]*columnwidth[^}]*@\{\}\}',
        r'\\begin{longtable}{|l|l|l|}',
        content,
        flags=re.MULTILINE | re.DOTALL
    )
    
    # 处理包含arraybackslash的列定义
    content = re.sub(
        r'\\begin\{longtable\}\[\]\{[^}]*arraybackslash[^}]*\}',
        r'\\begin{longtable}{|l|l|l|}',
        content,
        flags=re.MULTILINE | re.DOTALL
    )
    
    # 处理包含raggedright的列定义
    content = re.sub(
        r'\\begin\{longtable\}\[\]\{[^}]*raggedright[^}]*\}',
        r'\\begin{longtable}{|l|l|l|}',
        content,
        flags=re.MULTILINE | re.DOTALL
    )
    
    # 3. 修复表格头部和分隔线
    print("   修复表格头部格式...")
    
    # 统一表格线格式
    content = re.sub(r'\\toprule\\noalign\{\}', r'\\hline', content)
    content = re.sub(r'\\midrule\\noalign\{\}', r'\\hline', content) 
    content = re.sub(r'\\bottomrule\\noalign\{\}', r'\\hline', content)
    content = re.sub(r'\\endhead', r'', content)
    content = re.sub(r'\\endlastfoot', r'', content)
    
    # 4. 清理多余的空行和格式错误
    print("   清理格式错误...")
    
    # 移除多余的hline
    content = re.sub(r'(\\hline\s*){3,}', r'\\hline\n', content, flags=re.MULTILINE)
    
    # 清理空的表格行
    content = re.sub(r'\\hline\s*\n\s*\\hline', r'\\hline', content, flags=re.MULTILINE)
    
    # 5. 修复特殊字符问题
    print("   修复特殊字符...")
    
    # 清理@{}语法
    content = re.sub(r'@\{\}', '', content)
    
    # 6. 最终的全面修复 - 处理所有剩余的异常表格定义
    print("   最终全面修复...")
    
    # 匹配任何异常的longtable定义并替换为标准格式
    content = re.sub(
        r'\\begin\{longtable\}\[[^\]]*\]\{[^{}]*\{[^{}]*\}[^{}]*\}',
        r'\\begin{longtable}{|l|l|l|}',
        content,
        flags=re.MULTILINE | re.DOTALL
    )
    
    # 处理仍然存在的问题格式
    content = re.sub(
        r'\\begin\{longtable\}\[\]\{[^}]*real[^}]*\}',
        r'\\begin{longtable}{|l|l|l|}',
        content,
        flags=re.MULTILINE | re.DOTALL
    )
    
    # 保存修复后的文件
    with open(tex_file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ 表格修复完成!")
    return content

def main():
    # 指定LaTeX文件路径
    tex_file = Path("输出/教材.tex")
    
    if not tex_file.exists():
        print(f"❌ 文件不存在: {tex_file}")
        return
    
    print(f"📄 处理文件: {tex_file}")
    fix_table_issues(tex_file)
    
    print(f"🎉 修复完成！文件已更新: {tex_file}")

if __name__ == "__main__":
    main()