#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LaTeX内容检查和修复工具
"""

import re
from pathlib import Path

def check_and_fix_latex():
    """检查并修复LaTeX文件"""
    print("🔧 LaTeX内容检查和修复工具")
    print("=" * 40)
    
    # 检查合并的Markdown文件
    script_dir = Path(__file__).parent
    output_dir = script_dir / 'output'
    merged_file = output_dir / 'textbook_merged.md'
    
    if not merged_file.exists():
        print("❌ 未找到 textbook_merged.md 文件")
        print("💡 请先运行 convert_safe.bat")
        return
    
    print(f"📄 检查文件: {merged_file}")
    
    # 读取内容
    with open(merged_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"📊 原始文件大小: {len(content)} 字符")
    
    # 检查问题
    issues = []
    fixes_applied = []
    
    # 1. 检查 \n 字符串
    if '\\n' in content:
        count = content.count('\\n')
        issues.append(f"发现 {count} 个 \\n 字符串")
        content = content.replace('\\n', '\n')
        fixes_applied.append(f"修复了 {count} 个 \\n 字符串")
    
    # 2. 检查其他转义问题
    problematic_patterns = [
        ('\\r', ''),
        ('\\t', ' '),
        ('\\\\', '\\')
    ]
    
    for pattern, replacement in problematic_patterns:
        if pattern in content:
            count = content.count(pattern)
            issues.append(f"发现 {count} 个 {pattern}")
            content = content.replace(pattern, replacement)
            fixes_applied.append(f"修复了 {count} 个 {pattern}")
    
    # 3. 检查LaTeX特殊字符（在非代码块中）
    def check_special_chars(text):
        # 保护代码块
        code_blocks = []
        def save_code_block(match):
            code_blocks.append(match.group(0))
            return f'__CODE_BLOCK_{len(code_blocks)-1}__'
        
        protected = re.sub(r'```.*?```', save_code_block, text, flags=re.DOTALL)
        protected = re.sub(r'`[^`\n]+`', save_code_block, protected)
        
        # 检查特殊字符
        special_chars = ['#', '$', '%', '&', '^', '_', '{', '}', '~']
        char_counts = {}
        
        for char in special_chars:
            count = protected.count(char)
            if count > 0:
                char_counts[char] = count
        
        return char_counts
    
    special_counts = check_special_chars(content)
    if special_counts:
        for char, count in special_counts.items():
            issues.append(f"发现 {count} 个可能有问题的字符: {char}")
    
    # 4. 检查日期格式
    date_patterns = re.findall(r'\d{4}年\d{1,2}月[^\w\s]*', content)
    if date_patterns:
        issues.append(f"发现 {len(date_patterns)} 个日期格式可能有问题")
        for pattern in date_patterns[:3]:  # 只显示前3个
            print(f"  示例: {pattern}")
    
    # 输出检查结果
    print(f"\n📋 检查结果:")
    if issues:
        print(f"⚠️  发现 {len(issues)} 类问题:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("✅ 未发现明显问题")
    
    # 应用修复
    if fixes_applied:
        print(f"\n🔧 应用修复:")
        for fix in fixes_applied:
            print(f"  ✅ {fix}")
        
        # 保存修复后的文件
        fixed_file = output_dir / 'textbook_merged_fixed.md'
        with open(fixed_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"💾 修复后文件保存为: {fixed_file}")
        print(f"📊 修复后文件大小: {len(content)} 字符")
        
        # 建议
        print(f"\n💡 建议:")
        print(f"  1. 使用修复后的文件进行转换")
        print(f"  2. 运行: pandoc textbook_merged_fixed.md -o textbook.tex ...")
    else:
        print(f"\n✅ 文件内容正常，无需修复")
    
    # 生成简化的测试文件
    print(f"\n🧪 生成测试用小文件...")
    test_content = content[:5000] + "\n\n# 测试结束\n\n这是一个用于测试LaTeX转换的简化版本。"
    test_file = output_dir / 'test_small.md'
    
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    print(f"📄 测试文件: {test_file} ({len(test_content)} 字符)")
    print(f"💡 可以先用小文件测试: pandoc test_small.md -o test_small.tex ...")

if __name__ == '__main__':
    check_and_fix_latex()