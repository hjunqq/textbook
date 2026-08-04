import re
import sys

# 汇集所有参考文献
all_refs = {}
chapter_refs = {}

# 逐章提取参考文献
for chapter_num in [1, 6, 7, 8]:
    filename = f"chapters/chapter{chapter_num:02d}.tex"
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 找到参考文献段落
        match = re.search(r'\\paragraph\*\{参考文献\}(.*?)(?=\\(?:section|subsection|paragraph)|$)', content, re.DOTALL)
        if match:
            refs_text = match.group(1)
            chapter_refs[chapter_num] = refs_text
            print(f"===== Chapter {chapter_num} =====")
            print(refs_text[:500])
            print()
    except Exception as e:
        print(f"Error reading {filename}: {e}")

