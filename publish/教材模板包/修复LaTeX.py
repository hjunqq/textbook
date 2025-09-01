#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智慧水利教材转换修复工具
修复章节编号和格式问题
"""

import re
import shutil
import os

def fix_latex_file(input_file, output_file):
    """修复LaTeX文件的章节问题"""
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔧 开始修复LaTeX文件...")
    
    # 1. 修复前言章节 - 移除编号
    content = re.sub(
        r'\\chapter\{前言\}',
        r'\\chapter*{前言}',
        content
    )
    print("✅ 修复前言章节编号")
    
    # 2. 修复第六章和第八章 - 从section升级为chapter
    content = re.sub(
        r'\\section\{第六章 前端开发技术\}',
        r'\\chapter{第六章 前端开发技术}',
        content
    )
    content = re.sub(
        r'\\section\{第八章 系统优化与维护\}',
        r'\\chapter{第八章 系统优化与维护}',
        content
    )
    print("✅ 修复第六章和第八章级别")
    
    # 3. 修复章节标题格式 - 补全缺失的部分
    chapter_fixes = {
        r'\\chapter\{第一章\s*$': r'\\chapter{第一章 绪论}',
        r'\\chapter\{第二章\s*$': r'\\chapter{第二章 软件工程基础与需求分析}', 
        r'\\chapter\{第三章\s*$': r'\\chapter{第三章 软件模块详细设计}',
        r'\\chapter\{第四章\s*$': r'\\chapter{第四章 数据库设计与实现}',
        r'\\chapter\{第五章\s*$': r'\\chapter{第五章 后端开发技术}',
        r'\\chapter\{第七章\s*$': r'\\chapter{第七章 智慧水利三维场景构建}',
        r'\\chapter\{第九章\s*$': r'\\chapter{第九章 典型应用}'
    }
    
    for pattern, replacement in chapter_fixes.items():
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    
    print("✅ 修复章节标题格式")
    
    # 4. 修复图像路径问题 - 移除双斜杠
    content = re.sub(r'\\includegraphics\{images//(\d+)\}', r'\\includegraphics{images/image_\\1}', content)
    print("✅ 修复图像路径问题")
    
    # 5. 修复表格格式问题
    # 移除有问题的minipage命令参数
    content = re.sub(
        r'\\begin\{minipage\}\[b\]\{\\linewidth\}\\raggedright\s*\(\s*\)\s*\*\s*[0-9.]+',
        r'\\begin{minipage}[b]{\\linewidth}\\raggedright',
        content
    )
    print("✅ 修复表格格式问题")
    
    # 创建输出目录
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # 写入修复后的文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"🎉 修复完成！输出文件：{output_file}")
    
    return True

def main():
    input_file = r"E:\2025\教材\智慧水利平台架构与开发\publish\latex_output\教材.tex"
    output_file = r"E:\2025\教材\智慧水利平台架构与开发\publish\latex_output\教材_修复版.tex"
    
    if not os.path.exists(input_file):
        print(f"❌ 输入文件不存在：{input_file}")
        return False
    
    try:
        fix_latex_file(input_file, output_file)
        
        # 复制图像目录
        input_images = os.path.dirname(input_file) + "/images"
        if os.path.exists(input_images):
            print(f"📁 图像目录已存在：{input_images}")
        
        print("\n" + "="*50)
        print("修复完成!")
        print("="*50)
        print(f"修复后的LaTeX文件：{output_file}")
        print("\n使用以下命令重新编译：")
        print(f'cd "{os.path.dirname(output_file)}"')
        print(f'xelatex "{os.path.basename(output_file)}"')
        print(f'xelatex "{os.path.basename(output_file)}"')
        print(f'xelatex "{os.path.basename(output_file)}"')
        
    except Exception as e:
        print(f"❌ 修复失败：{str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    main()
