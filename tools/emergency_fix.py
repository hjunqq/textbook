#!/usr/bin/env python3
"""
紧急修复：直接解决第32115行的嵌套$$问题
"""

import re

def emergency_fix():
    """紧急修复嵌套$$问题"""
    print("🚨 紧急修复：解决嵌套$$问题")
    
    with open('output/final_fixed_textbook.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("修复前检查...")
    # 检查当前的嵌套问题
    nested_patterns = [
        r'\$\$\s*\n\s*\$\$([^$]*?)\$\$\s*\n\s*\$\$',  # $$\n$$content$$\n$$
        r'\$\$\$\$([^$]*?)\$\$\$\$',  # $$$$content$$$$
    ]
    
    for i, pattern in enumerate(nested_patterns):
        matches = re.findall(pattern, content, re.DOTALL)
        if matches:
            print(f"发现嵌套模式{i+1}: {len(matches)}个")
            for match in matches[:3]:  # 显示前3个
                print(f"  - {match[:30]}...")
    
    # 修复嵌套问题
    print("开始修复...")
    
    # 修复模式1: $$\n$$content$$\n$$ -> $$content$$
    original_count = len(re.findall(nested_patterns[0], content, re.DOTALL))
    content = re.sub(nested_patterns[0], r'$$\1$$', content, flags=re.DOTALL)
    fixed_count1 = original_count - len(re.findall(nested_patterns[0], content, re.DOTALL))
    print(f"修复嵌套模式1: {fixed_count1}个")
    
    # 修复模式2: $$$$content$$$$ -> $$content$$  
    original_count = len(re.findall(nested_patterns[1], content))
    content = re.sub(nested_patterns[1], r'$$\1$$', content)
    fixed_count2 = original_count - len(re.findall(nested_patterns[1], content))
    print(f"修复嵌套模式2: {fixed_count2}个")
    
    # 额外检查：移除连续的空行$$
    lines = content.split('\n')
    cleaned_lines = []
    prev_line = ""
    
    for line in lines:
        # 如果当前行和前一行都是$$，跳过当前行
        if line.strip() == '$$' and prev_line.strip() == '$$':
            print(f"移除重复的$$行")
            continue
        cleaned_lines.append(line)
        prev_line = line
    
    content = '\n'.join(cleaned_lines)
    
    # 最终检查
    single_dollars = content.count('$')
    double_dollars = content.count('$$') 
    net_single = single_dollars - double_dollars * 2
    
    print(f"最终统计:")
    print(f"  总$符号: {single_dollars}")
    print(f"  $$符号对: {double_dollars}")
    print(f"  净单$: {net_single}")
    print(f"  匹配状态: {'✅' if net_single % 2 == 0 else '❌'}")
    
    # 保存紧急修复版本
    with open('output/emergency_fixed_textbook.md', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("紧急修复版本已保存: output/emergency_fixed_textbook.md")
    
    # 验证修复的具体行
    lines = content.split('\n')
    for i in range(32110, min(32120, len(lines))):
        if i < len(lines):
            line = lines[i]
            if 'Delta' in line and 'frac' in line:
                print(f"验证第{i+1}行: {line}")
    
    return net_single % 2 == 0

if __name__ == "__main__":
    success = emergency_fix()
    if success:
        print("\n🎉 紧急修复完成！符号匹配正确！")
    else:
        print("\n⚠️ 还需要进一步检查$符号匹配")