#!/usr/bin/env python3
"""
彻底解决嵌套$$问题
"""

import re
from pathlib import Path

def fix_nested_dollars(content):
    """彻底修复嵌套的$$符号"""
    print("修复嵌套的$$符号...")
    
    # 首先找到所有的$$...$$块
    original_blocks = re.findall(r'\$\$.*?\$\$', content, re.DOTALL)
    print(f"找到 {len(original_blocks)} 个$$块")
    
    # 替换嵌套的$$符号
    # 模式1: $$\n$$内容$$\n$$  -> $$内容$$
    content = re.sub(r'\$\$\s*\n\s*\$\$([^$]*?)\$\$\s*\n\s*\$\$', r'$$\1$$', content, flags=re.DOTALL)
    
    # 模式2: $$$$内容$$$$ -> $$内容$$
    content = re.sub(r'\$\$\$\$([^$]*?)\$\$\$\$', r'$$\1$$', content)
    
    # 模式3: 检查并清理多重嵌套
    lines = content.split('\n')
    fixed_lines = []
    in_math_block = False
    
    for line in lines:
        # 如果这行只有$$，跳过重复的
        if line.strip() == '$$':
            if not in_math_block:
                fixed_lines.append(line)
                in_math_block = True
            else:
                # 结束数学块
                fixed_lines.append(line) 
                in_math_block = False
        else:
            fixed_lines.append(line)
            # 重置状态如果不是空行或$$行
            if line.strip() and '$$' in line:
                in_math_block = False
    
    return '\n'.join(fixed_lines)

def create_final_fixed_version():
    """创建最终修复版本"""
    print("创建最终修复版本...")
    
    # 从最原始的数学修复版本开始
    with open('output/math_fixed_textbook.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("原始文件大小:", len(content))
    
    # 第一步：清理所有嵌套问题
    content = fix_nested_dollars(content)
    
    # 第二步：只处理真正裸露的数学命令（非常谨慎）
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines):
        # 非常精确的条件：行中包含数学等式但没有被$包围
        if (line.strip() and 
            '=' in line and 
            re.search(r'\\(frac|sqrt|Delta|times)', line) and
            '$' not in line and
            not line.strip().startswith('#') and
            not line.strip().startswith('```') and
            not line.strip().startswith('*') and
            len(line.strip()) > 10):  # 避免处理太短的行
            
            print(f"包装裸露公式 第{i+1}行: {line[:50]}...")
            fixed_lines.append(f'$${line.strip()}$$')
        else:
            fixed_lines.append(line)
    
    final_content = '\n'.join(fixed_lines)
    
    # 最终语法检查
    single_dollars = final_content.count('$')
    double_dollars = final_content.count('$$')
    net_single = single_dollars - double_dollars * 2
    
    print(f"最终检查:")
    print(f"  单$符号: {single_dollars}")
    print(f"  双$$符号: {double_dollars}")
    print(f"  净单$符号: {net_single}")
    
    if net_single % 2 == 0:
        print("✅ $符号匹配正确")
    else:
        print("⚠️ $符号不匹配，需要手动检查")
    
    # 保存最终版本
    with open('output/final_fixed_textbook.md', 'w', encoding='utf-8') as f:
        f.write(final_content)
    
    print("最终修复版本已创建: output/final_fixed_textbook.md")
    
    # 创建统计报告
    inline_math = len(re.findall(r'\$[^$]+\$', final_content))
    block_math = len(re.findall(r'\$\$[^$]+\$\$', final_content))
    
    report = f"""# 最终修复报告

## 修复结果
- 文件大小: {len(final_content):,} 字节
- 行内公式: {inline_math} 个
- 块级公式: {block_math} 个  
- 总公式: {inline_math + block_math} 个

## 符号检查
- 单$符号: {single_dollars}
- 双$$符号: {double_dollars}  
- 匹配状态: {'✅ 正确' if net_single % 2 == 0 else '⚠️ 不匹配'}

生成时间: {Path().cwd()}
"""
    
    with open('output/final_report.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    return net_single % 2 == 0

if __name__ == "__main__":
    success = create_final_fixed_version()
    if success:
        print("\n🎉 修复完成！现在可以尝试生成PDF了")
    else:
        print("\n⚠️ 还有语法问题，需要进一步检查")