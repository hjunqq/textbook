#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""智慧水利教材终极转换器（最小干净版 v5.2）
步骤: 发现 -> 预处理 -> 合并 -> Pandoc -> 轻量 LaTeX 修复 -> 编译
说明: 全量重建，移除历史残留/重复/模板代码。
"""
from __future__ import annotations
import os, re, shutil, subprocess
from pathlib import Path
from typing import List, Optional, Tuple
from converter_config import (
    CHAPTER_ORDER,
    UNNECESSARY_SECTION_PATTERNS,
    IMAGE_PATH_PATTERNS,
    SECTION_BLOCK_REMOVE_PATTERNS,
    YAML_FRONTMATTER_RE,
    PANDOC_FROM_FORMAT,
    PROTECTIVE_COMMENT,
    ADMONITION_TYPES,
    ADMONITION_RE,
    TCOLORBOX_TPL,
    ENABLE_ADMONITION,
)
IMG_EXTS = {'.png','.jpg','.jpeg','.gif','.svg','.bmp','.webp','.wmf','.emf'}
class SmartWaterTextbookConverterFinal:
    def __init__(self, config_file: Optional[str] = None):
        script_dir = Path(__file__).parent
        self.project_root = script_dir.parent.parent
        self.source_dir = self.project_root / 'docs'
        self.output_dir = script_dir / '输出'
        self.images_dir = self.output_dir / 'images'
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.images_dir.mkdir(parents=True, exist_ok=True)
        self.chapter_order = CHAPTER_ORDER
        print('[INIT] source=', self.source_dir, ' output=', self.output_dir)
    def discover_chapters(self) -> List[Tuple[str,str]]:
        chapters_dir = self.source_dir / 'chapters'
        if not chapters_dir.exists():
            raise FileNotFoundError(f'章节目录缺失: {chapters_dir}')
        result: List[Tuple[str,str]] = []
        preface = self.source_dir / '前言.md'
        if preface.exists():
            result.append(('preface', str(preface)))
        for key in self.chapter_order:
            cdir = chapters_dir / key
            if not cdir.exists():
                continue
            main_md = cdir / f'{key}.md'
            if main_md.exists():
                result.append(('chapter', str(main_md)))
            for sec in sorted(cdir.glob('section*.md')):
                result.append(('section', str(sec)))
        appendix_dir = self.project_root / 'appendix'
        if appendix_dir.exists():
            for app in sorted(appendix_dir.glob('*.md')):
                result.append(('appendix', str(app)))
        print(f'[DISCOVER] {len(result)} 个文件')
        return result
    def preprocess_markdown(self, content: str, file_path: str, file_type: str) -> str:
        content = self.standardize_headings(content, file_path, file_type)
        content = self.unify_image_paths(content)
    # 不在此阶段做正则复杂替换，保持语义完整
        return content
    def standardize_headings(self, content: str, file_path: str, file_type: str) -> str:
        name = Path(file_path).name
        if file_type == 'preface':
            content = re.sub(r'^#\s+(.+)', r'# \1', content, count=1, flags=re.MULTILINE)
        elif file_type == 'chapter' and name.startswith('chapter'):
            m = re.search(r'chapter(\d+)', name)
            if m:
                key = f'chapter{m.group(1).zfill(2)}'
                if key in self.chapter_order:
                    title = self.chapter_order[key]['title']
                    content = re.sub(r'^#\s+.*', f'# {title}', content, count=1, flags=re.MULTILINE)
        elif file_type == 'section' and name.startswith('section'):
            sm = re.search(r'section(\d+)-(\d+)', name)
            if sm:
                cno, sno = int(sm.group(1)), int(sm.group(2))
                content = re.sub(r'^#\s+(.+)', f'## {cno}.{sno} \\1', content, count=1, flags=re.MULTILINE)
                content = re.sub(r'^##\s+(?!{}\\.{})(.+)'.format(cno, sno), r'### \\1', content, flags=re.MULTILINE)
        for pat in UNNECESSARY_SECTION_PATTERNS:
            content = re.sub(pat, '', content, flags=re.MULTILINE)
        return re.sub(r'\n{3,}', '\n\n', content)
    def unify_image_paths(self, content: str) -> str:
        for pattern, repl in IMAGE_PATH_PATTERNS:
            content = re.sub(pattern, repl, content, flags=re.IGNORECASE)
        return content
    def filter_unnecessary_content(self, content: str) -> str:
        for pat in SECTION_BLOCK_REMOVE_PATTERNS:
            content = re.sub(pat, '', content, flags=re.DOTALL | re.MULTILINE)
        return re.sub(r'\n{3,}', '\n\n', content)
    def remove_yaml_frontmatter(self, content: str) -> str:
        norm = content.replace('\r\n', '\n')
        if norm.startswith('---'):
            norm = re.sub(YAML_FRONTMATTER_RE, '', norm, count=1)
        return norm
    def merge_chapters(self, chapter_files: List[Tuple[str,str]]) -> str:
        parts: List[str] = []
        self._merge_debug = []  # (filename, lines_before, lines_after)
        for ftype, fpath in chapter_files:
            print(f'[MERGE] {Path(fpath).name:<40} ({ftype})')
            try:
                txt = Path(fpath).read_text(encoding='utf-8')
                raw_lines = txt.count('\n') + 1
                txt = self.remove_yaml_frontmatter(txt)
                pre = self.preprocess_markdown(txt, fpath, ftype)
                post = self.filter_unnecessary_content(pre)
                cleaned_lines = post.count('\n') + 1
                self._merge_debug.append((Path(fpath).name, raw_lines, cleaned_lines))
                parts.append(f'% [FILE-BEGIN] {Path(fpath).name} raw={raw_lines} cleaned={cleaned_lines}\n')
                parts.append(post)
                if ftype in ('chapter','preface'):
                    parts.append('\n\n\\newpage\n\n')
                parts.append(f'% [FILE-END] {Path(fpath).name}\n')
            except Exception as e:
                print(f'[WARN] 读取失败 {fpath}: {e}')
        return '\n'.join(parts)
    def convert_to_latex(self, merged_content: str) -> str:
        temp_md = self.output_dir / 'temp_merged.md'
        temp_md.write_text(PROTECTIVE_COMMENT + merged_content, encoding='utf-8')
        # 生成合并统计文件
        stats_path = self.output_dir / 'merge_stats.txt'
        if hasattr(self, '_merge_debug'):
            total_raw = sum(r for _, r, _ in self._merge_debug)
            total_clean = sum(c for _, _, c in self._merge_debug)
            lines = [f'TOTAL_RAW={total_raw}', f'TOTAL_CLEAN={total_clean}', 'DETAIL: filename raw_lines cleaned_lines']
            for name, r, c in self._merge_debug:
                lines.append(f'{name}\t{r}\t{c}')
            stats_path.write_text('\n'.join(lines), encoding='utf-8')
        output_tex = self.output_dir / '教材.tex'
        cmd = [ 'pandoc', str(temp_md), '--from', PANDOC_FROM_FORMAT, '--to', 'latex', '--standalone', '--toc', '--top-level-division=chapter', '--metadata', 'title=智慧水利平台架构与开发', '--metadata', 'author=教材编写组', '--metadata', 'documentclass=book', '--output', str(output_tex) ]
        print('[PANDOC]', ' '.join(cmd))
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True, encoding='utf-8')
            print('[PANDOC] 成功')
            self.postprocess_latex(str(output_tex))
            return str(output_tex)
        except subprocess.CalledProcessError as e:
            print('[PANDOC] 失败:'); print(e.stderr)
            if temp_md.exists():
                print('---- temp_merged.md 前20行 ----')
                for i, line in enumerate(temp_md.read_text(encoding='utf-8').splitlines()[:20],1):
                    print(f'{i:2}: {line}')
            raise
    def postprocess_latex(self, tex_file: str):
        content = Path(tex_file).read_text(encoding='utf-8')
        if '\\usepackage{ctex}' not in content:
            # 正确在 \documentclass 行后插入 ctex
            content = re.sub(r'(\\documentclass\[.*?\]\{.*?\}\s*)', r'\1\n\\usepackage[UTF8]{ctex}\n', content, count=1)
        content = re.sub(r'\\section\{前言\}', r'\\chapter*{前言}', content)
        # 轻量特殊字符兜底：避免再度破坏 LaTeX 结构
        def escape_dollar(m):
            return m.group(0) if m.group(0).startswith('\\') else '\\$'
        content = re.sub(r'(?<!\\)\$', escape_dollar, content)
        Path(tex_file).write_text(content, encoding='utf-8')
        print('[LATEX] 后处理完成')
        # 可选：admonition 二次转换（若 Pandoc 保留 !!! 结构则处理；当前大多在 Markdown 中保持原样不会进入 LaTeX）
        if ENABLE_ADMONITION and '!!! ' in content:
            print('[LATEX] 检测到残留 admonition 标记，后续可扩展处理逻辑')
    def compile_pdf(self, tex_file: str) -> str:
        tex_path = Path(tex_file); out_dir = tex_path.parent
        old = os.getcwd(); os.chdir(out_dir)
        try:
            engine = None
            for c in ['xelatex','pdflatex','lualatex']:
                try:
                    r = subprocess.run([c,'--version'], capture_output=True, text=True, encoding='utf-8')
                    if r.returncode == 0: engine = c; break
                except FileNotFoundError: continue
            if not engine:
                print('[LATEX] 无编译器，跳过 PDF'); return str(tex_path)
            for i in range(2):
                print(f'[LATEX] 第 {i+1} 次编译 ({engine})')
                # 避免 GBK 解码异常：不捕获输出或以二进制忽略
                subprocess.run([engine,'-interaction=nonstopmode','-halt-on-error', tex_path.name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            # 保存 tex 行数统计
            tex_stats = out_dir / 'tex_stats.txt'
            try:
                t = tex_path.read_text(encoding='utf-8', errors='ignore')
                chapters = len(re.findall(r'\\chapter', t))
                sections = len(re.findall(r'\\section', t))
                tex_stats.write_text(f'lines={t.count("\n")+1}\nchapters={chapters}\nsections={sections}\n', encoding='utf-8')
            except Exception:
                pass
            pdf = out_dir / '教材.pdf'
            if pdf.exists() and pdf.stat().st_size > 150*1024:
                print('[LATEX] PDF 生成完成'); return str(pdf)
            print('[LATEX] PDF 不完整，返回 tex'); return str(tex_path)
        finally: os.chdir(old)
    def copy_images(self):
        src_dirs = [ self.source_dir / 'assets' / 'images', self.source_dir / 'chapters' / 'images', self.source_dir / 'images', self.project_root / 'images', self.project_root / '参考' / 'extracted_images_ch6', self.project_root / '参考' / 'images' ]
        copied = 0
        for d in src_dirs:
            if not d.exists(): continue
            for f in d.rglob('*'):
                if f.is_file() and f.suffix.lower() in IMG_EXTS:
                    new_name = f'ch6_{f.name}' if 'extracted_images_ch6' in str(f) else f.name
                    target = self.images_dir / new_name
                    if target.exists(): continue
                    try: shutil.copy2(f, target); copied += 1
                    except Exception as e: print(f'[IMG] 复制失败 {f}: {e}')
        if copied == 0: print('[IMG] 未复制到图片，生成占位符'); self.create_placeholder_images()
        else: print(f'[IMG] 图片复制完成: {copied}')
    def create_placeholder_images(self):
        names = ['placeholder.png','image_001.png']
        try:
            from PIL import Image, ImageDraw, ImageFont
            for n in names:
                p = self.images_dir / n
                if p.exists(): continue
                img = Image.new('RGB',(400,300),'#DDDDDD'); d = ImageDraw.Draw(img)
                try: font = ImageFont.load_default(); d.text((30,130), n, fill='black', font=font)
                except Exception: d.text((30,130), n, fill='black')
                img.save(p)
        except ImportError:
            for n in names:
                p = self.images_dir / n
                if not p.exists(): p.write_text(f'Placeholder for {n}', encoding='utf-8')
    def run_conversion(self):
        print('='*60); print('智慧水利教材转换器 v5.2'); print('='*60)
        files = self.discover_chapters()
        self.copy_images()
        merged = self.merge_chapters(files)
        # 快速内容体积验证
        merged_len = len(merged)
        print(f'[DEBUG] 合并后字符数: {merged_len}')
        print(f'[DEBUG] 预期章节数(含前言): {len(self.chapter_order)+1}')
        # 保存合并文件以人工审查（截取前 8000 字符）
        try:
            (self.output_dir / 'debug_merged_preview.md').write_text(merged[:8000], encoding='utf-8')
        except Exception as e:
            print('[WARN] 写入 debug_merged_preview.md 失败:', e)
        tex = self.convert_to_latex(merged)
        output = self.compile_pdf(tex)
        print('[DONE] 输出:', output)

def main():
    SmartWaterTextbookConverterFinal().run_conversion()
if __name__ == '__main__':
    main()
