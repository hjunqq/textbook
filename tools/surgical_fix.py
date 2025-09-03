#!/usr/bin/env python3
"""
外科手术式修复：只修复确实存在的语法错误
"""

import re
from pathlib import Path

def surgical_fix_latex_errors(content):
    """外科手术式修复LaTeX语法错误"""
    print("🔧 外科手术式修复LaTeX语法错误...")
    
    fixes_made = 0
    
    # 修复1: \sqrt { -> \sqrt{
    before_count = len(re.findall(r'\\sqrt \{', content))
    content = re.sub(r'\\sqrt \{', r'\\sqrt{', content)
    after_count = len(re.findall(r'\\sqrt \{', content))
    sqrt_fixes = before_count - after_count
    fixes_made += sqrt_fixes
    print(f"修复 \\sqrt空格错误: {sqrt_fixes} 处")
    
    # 修复2: \frac { -> \frac{
    before_count = len(re.findall(r'\\frac \{', content))
    content = re.sub(r'\\frac \{', r'\\frac{', content)
    after_count = len(re.findall(r'\\frac \{', content))
    frac_fixes = before_count - after_count
    fixes_made += frac_fixes
    print(f"修复 \\frac空格错误: {frac_fixes} 处")
    
    # 修复3: 其他常见的空格问题
    latex_commands = ['partial', 'sum', 'int', 'Delta', 'times', 'cdot']
    for cmd in latex_commands:
        pattern = f'\\\\{cmd} \\{{'
        before_count = len(re.findall(pattern, content))
        content = re.sub(pattern, f'\\\\{cmd}{{', content)
        after_count = len(re.findall(pattern, content))
        cmd_fixes = before_count - after_count
        if cmd_fixes > 0:
            fixes_made += cmd_fixes
            print(f"修复 \\{cmd}空格错误: {cmd_fixes} 处")
    
    # 修复4: 检查是否有完全裸露的LaTeX命令（不在$中的）
    lines = content.split('\n')
    bare_latex_fixed = 0
    
    for i, line in enumerate(lines):
        # 检查是否包含裸露的LaTeX命令
        if (re.search(r'[^$]\\(sqrt|frac|partial)', line) and 
            '$' not in line and
            not line.strip().startswith('#') and
            not line.strip().startswith('```')):
            print(f"警告：第{i+1}行可能有裸露LaTeX命令: {line[:50]}...")
    
    print(f"总共修复: {fixes_made} 处LaTeX语法错误")
    return content

def fix_image_paths(content):
    """修复图片路径问题"""
    print("🖼️ 修复图片路径...")
    
    # 统计原始图片引用
    original_images = len(re.findall(r'!\[[^\]]*\]\([^)]+\)', content))
    print(f"原始图片引用: {original_images} 个")
    
    # 修复相对路径
    fixes = 0
    
    # 修复 docs/chapters/ 路径
    before = len(re.findall(r'!\[[^\]]*\]\(docs/chapters/', content))
    content = re.sub(r'!\[([^\]]*)\]\(docs/chapters/', r'![\1](../docs/chapters/', content)
    after = len(re.findall(r'!\[[^\]]*\]\(docs/chapters/', content))
    fixes += (before - after)
    
    # 修复相对images/路径为绝对路径
    before = len(re.findall(r'!\[[^\]]*\]\(images/', content))
    content = re.sub(r'!\[([^\]]*)\]\(images/', r'![\1](../docs/chapters/images/', content)
    after = len(re.findall(r'!\[[^\]]*\]\(images/', content))
    fixes += (before - after)
    
    print(f"修复图片路径: {fixes} 处")
    
    # 最终统计
    final_images = len(re.findall(r'!\[[^\]]*\]\([^)]+\)', content))
    print(f"修复后图片引用: {final_images} 个")
    
    return content

def create_surgically_fixed_version():
    """创建外科手术式修复版本"""
    print("📋 创建外科手术式修复版本...")
    
    # 读取干净重建版本
    with open('output/clean_rebuild.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"原始文件大小: {len(content):,} 字符")
    
    # 外科手术式修复LaTeX错误
    content = surgical_fix_latex_errors(content)
    
    # 修复图片路径
    content = fix_image_paths(content)
    
    # 最终检查
    single_dollars = content.count('$')
    double_dollars = content.count('$$')
    net_single = single_dollars - double_dollars * 2
    
    print(f"最终检查:")
    print(f"  单$符号: {single_dollars}")
    print(f"  双$$符号: {double_dollars}") 
    print(f"  净单$符号: {net_single}")
    print(f"  符号匹配: {'✅' if net_single % 2 == 0 else '⚠️'}")
    
    # 保存外科修复版本
    with open('output/surgical_fixed.md', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("外科修复版本已保存: output/surgical_fixed.md")
    return net_single % 2 == 0

if __name__ == "__main__":
    success = create_surgically_fixed_version()
    print(f"\n{'✅ 修复完成' if success else '⚠️ 需要进一步检查'}!")
    print("请运行测试脚本验证修复效果")