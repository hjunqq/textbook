#!/usr/bin/env python3
import sys, yaml, os

def iter_nav(nav):
    if isinstance(nav, list):
        for item in nav:
            yield from iter_nav(item)
    elif isinstance(nav, dict):
        for _, v in nav.items():
            if isinstance(v, str) and v.lower().endswith(('.md','.markdown','.mdx')):
                yield v
            else:
                yield from iter_nav(v)

def main():
    mk = 'mkdocs.yml'
    docs_dir = 'docs'
    if not os.path.exists(mk):
        print('mkdocs.yml not found', file=sys.stderr); sys.exit(1)
    
    try:
        with open(mk, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
    except Exception as e:
        print(f'Error reading mkdocs.yml: {e}', file=sys.stderr); sys.exit(1)
    
    docs_dir = data.get('docs_dir', docs_dir)
    nav = data.get('nav', [])
    files = list(iter_nav(nav))
    
    # 兼容未显式 nav 的项目：按目录遍历
    if not files:
        for root, _, fnames in os.walk(docs_dir):
            for f in sorted(fnames):
                if f.lower().endswith(('.md','.markdown','.mdx')):
                    files.append(os.path.relpath(os.path.join(root,f), start='.'))
    
    # 确保pandoc目录存在
    os.makedirs('pandoc', exist_ok=True)
    
    # 处理文件路径，确保正确找到文件
    processed_files = []
    for p in files:
        # 处理根目录的index.md
        if p == 'index.md':
            if os.path.exists('index.md'):
                processed_files.append('index.md')
            elif os.path.exists(os.path.join(docs_dir, 'index.md')):
                processed_files.append(os.path.join(docs_dir, 'index.md'))
        else:
            # 其他文件都在docs目录下
            full_path = os.path.join(docs_dir, p)
            if os.path.exists(full_path):
                processed_files.append(full_path)
            else:
                print(f'Warning: File not found: {full_path}', file=sys.stderr)
    
    with open('pandoc/files.txt','w',encoding='utf-8') as f:
        for p in processed_files:
            f.write(f"{p}\n")
    
    print(f'Generated file list with {len(processed_files)} files')

if __name__ == '__main__':
    main()