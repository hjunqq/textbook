#!/usr/bin/env python3
"""
超级简单的解决方案：直接处理，不搞复杂逻辑
"""

from pathlib import Path
import re

def simple_solution():
    """简单粗暴的解决方案"""
    print("📚 超级简单的解决方案...")
    
    Path('output').mkdir(exist_ok=True)
    
    # 直接按顺序读取所有文件
    all_files = [
        '../docs/前言.md',
        '../docs/chapters/chapter01/chapter01.md',
        '../docs/chapters/chapter01/section01-01.md',
        '../docs/chapters/chapter01/section01-02.md', 
        '../docs/chapters/chapter01/section01-03.md',
        '../docs/chapters/chapter02/chapter02.md',
        '../docs/chapters/chapter02/section02-01.md',
        '../docs/chapters/chapter02/section02-02.md',
        '../docs/chapters/chapter02/section02-03.md',
        '../docs/chapters/chapter02/section02-04.md',
        '../docs/chapters/chapter02/section02-05.md',
        '../docs/chapters/chapter02/section02-06.md',
        '../docs/chapters/chapter03/chapter03.md',
        '../docs/chapters/chapter03/section03-01.md',
        '../docs/chapters/chapter03/section03-02.md',
        '../docs/chapters/chapter03/section03-03.md',
        '../docs/chapters/chapter03/section03-04.md',
        '../docs/chapters/chapter03/section03-05.md',
        '../docs/chapters/chapter03/section03-06.md',
        '../docs/chapters/chapter03/section03-07.md',
        '../docs/chapters/chapter04/chapter04.md',
        '../docs/chapters/chapter04/section04-01.md',
        '../docs/chapters/chapter04/section04-02.md',
        '../docs/chapters/chapter04/section04-03.md',
        '../docs/chapters/chapter04/section04-04.md',
        '../docs/chapters/chapter04/section04-05.md',
        '../docs/chapters/chapter04/section04-06.md',
        '../docs/chapters/chapter04/section04-07.md',
        '../docs/chapters/chapter05/chapter05.md',
        '../docs/chapters/chapter05/section05-01.md',
        '../docs/chapters/chapter05/section05-02.md',
        '../docs/chapters/chapter05/section05-03.md',
        '../docs/chapters/chapter05/section05-04.md',
        '../docs/chapters/chapter05/section05-05.md',
        '../docs/chapters/chapter05/section05-06.md',
        '../docs/chapters/chapter06/chapter06.md',
        '../docs/chapters/chapter06/section06-01.md',
        '../docs/chapters/chapter06/section06-02.md',
        '../docs/chapters/chapter06/section06-03.md',
        '../docs/chapters/chapter06/section06-04.md',
        '../docs/chapters/chapter06/section06-05.md',
        '../docs/chapters/chapter06/section06-06.md',
        '../docs/chapters/chapter06/section06-07.md',
        '../docs/chapters/chapter07/chapter07.md',
        '../docs/chapters/chapter07/section07-01.md',
        '../docs/chapters/chapter07/section07-02.md',
        '../docs/chapters/chapter07/section07-03.md',
        '../docs/chapters/chapter07/section07-04.md',
        '../docs/chapters/chapter08/chapter08.md',
        '../docs/chapters/chapter08/section08-01.md',
        '../docs/chapters/chapter08/section08-02.md',
        '../docs/chapters/chapter08/section08-03.md',
        '../docs/chapters/chapter08/section08-04.md',
        '../docs/chapters/chapter08/section08-05.md',
        '../docs/chapters/chapter09/chapter09.md',
    ]
    
    all_content = []
    
    for file_path in all_files:
        p = Path(file_path)
        if p.exists():
            print(f"  ✅ {p.name}")
            with open(p, 'r', encoding='utf-8') as f:
                content = f.read()
                all_content.append(content)
        else:
            print(f"  ❌ {file_path} 不存在")
    
    # 合并内容
    raw_content = '\n\n'.join(all_content)
    
    # 简单清理
    print("清理内容...")
    raw_content = re.sub(r'\$[^$]*\$', '[数学公式]', raw_content)
    raw_content = re.sub(r'\$\$[^$]*\$\$', '[数学公式]', raw_content)
    raw_content = re.sub(r'\\[a-zA-Z]+\{[^}]*\}', '[LaTeX]', raw_content)
    raw_content = re.sub(r'\\[a-zA-Z]+', '[LaTeX]', raw_content)
    raw_content = re.sub(r'[📱🔍📑💡🧮📊🌓📖🟢🔴🚨⚠️ℹ️🐛📝❌✅✓✗○□├─│└┌┐┘┴┬┤]', '', raw_content)
    raw_content = re.sub(r'\\u[0-9a-fA-F]{4}', '', raw_content)
    
    # 简单修复标题层级：只保留主章节为#，其他都变成##或更低
    lines = raw_content.split('\n')
    fixed_lines = []
    
    main_chapter_patterns = [
        '# 前言',
        '# 第一章',
        '# 第二章', 
        '# 第三章',
        '# 第四章',
        '# 第五章',
        '# 第六章',
        '# 第七章',
        '# 第八章',
        '# 第九章',
    ]
    
    for line in lines:
        if line.startswith('# '):
            # 检查是否是主章节
            is_main = any(line.startswith(pattern) for pattern in main_chapter_patterns)
            if is_main:
                fixed_lines.append(line)  # 保持为一级标题
            else:
                fixed_lines.append('## ' + line[2:])  # 降级为二级标题
        else:
            fixed_lines.append(line)
    
    final_content = '\n'.join(fixed_lines)
    
    # 保存
    with open('output/simple_textbook.md', 'w', encoding='utf-8') as f:
        f.write(final_content)
    
    # 验证
    h1_titles = re.findall(r'^# (.+)$', final_content, re.MULTILINE)
    print(f"\n✅ 最终章节目录 ({len(h1_titles)} 个):")
    for i, title in enumerate(h1_titles, 1):
        print(f"  {i:2d}. {title}")
    
    print(f"\n文档大小: {len(final_content):,} 字符")
    print(f"文件已保存: output/simple_textbook.md")
    
    return len(h1_titles) >= 9

if __name__ == "__main__":
    success = simple_solution()
    if success:
        print("\n🎉 成功！所有章节都包含！")
        print("现在可以生成PDF了！")
    else:
        print("\n⚠️ 仍有问题")