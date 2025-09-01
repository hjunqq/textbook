
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
md2latex_robust.py — 更加健壮的 Markdown→LaTeX 转换器（v1.0）

设计目标：
- 分阶段、可观测：每个阶段产物可落盘（merged.md、generated.tex、logs）。
- 兼容性优先：Pandoc 输入格式自动降级（gfm → commonmark_x）。
- 编译稳定：自动注入 ctex，前言强制 \chapter*，GBK/UTF-8 安全。
- 删除策略可控：默认“温和模式”，可通过 --aggressive 打开更强过滤。
- 图片可追踪：优先复制“正文中引用”的图片，记录缺失列表。
- 故障隔离：单文件失败不阻断全流程；Pandoc/LaTeX 失败时仍保留上一步结果。
- 可配置：尽量复用 converter_config.py；无则采用内置兜底配置。

用法示例：
python md2latex_robust.py --project-root . --source-dir docs --output-dir 输出
"""
from __future__ import annotations
import argparse
import logging
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple, Iterable, Set

# ---------- 配置加载（优先使用用户的 converter_config.py） ----------
FALLBACK_PANDOC_FROM = 'gfm+emoji+pipe_tables+fenced_divs+definition_lists'
try:
    from converter_config import (
        CHAPTER_ORDER,
        UNNECESSARY_SECTION_PATTERNS,
        SECTION_BLOCK_REMOVE_PATTERNS,
        IMAGE_PATH_PATTERNS,
        YAML_FRONTMATTER_RE,
        PANDOC_FROM_FORMAT as CFG_PANDOC_FROM,
        PROTECTIVE_COMMENT,
    )
    PANDOC_FROM_FORMAT = CFG_PANDOC_FROM or FALLBACK_PANDOC_FROM
except Exception:
    # 兜底配置（当未提供 converter_config.py 时仍可运行）
    CHAPTER_ORDER = {}
    UNNECESSARY_SECTION_PATTERNS = []
    SECTION_BLOCK_REMOVE_PATTERNS = []
    IMAGE_PATH_PATTERNS = []
    PROTECTIVE_COMMENT = '% merged markdown (no YAML)\\n'
    from re import compile as _re_compile
    YAML_FRONTMATTER_RE = _re_compile(r'^---\\s*\\n.*?\\n---\\s*(\\n|$)', re.DOTALL)
    PANDOC_FROM_FORMAT = FALLBACK_PANDOC_FROM

IMG_EXTS = {'.png','.jpg','.jpeg','.gif','.svg','.bmp','.webp','.wmf','.emf'}

# ---------- 日志 ----------
def setup_logger(log_dir: Path) -> logging.Logger:
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / 'run.log'
    logger = logging.getLogger('md2latex')
    logger.setLevel(logging.DEBUG)
    fmt = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')
    fh = logging.FileHandler(log_file, encoding='utf-8')
    fh.setFormatter(fmt)
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    logger.handlers.clear()
    logger.addHandler(fh)
    logger.addHandler(sh)
    return logger

# ---------- 工具 ----------
def read_text_safe(p: Path) -> str:
    try:
        return p.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        return p.read_text(encoding='utf-8', errors='ignore')

def write_text_safe(p: Path, s: str):
    p.write_text(s, encoding='utf-8')

def run_cmd(cmd: List[str], cwd: Optional[Path]=None, logger: Optional[logging.Logger]=None) -> Tuple[int, str, str]:
    if logger:
        logger.debug('RUN: %s', ' '.join(cmd))
    try:
        r = subprocess.run(cmd, cwd=str(cwd) if cwd else None, capture_output=True, text=True, encoding='utf-8')
        out, err = r.stdout or '', r.stderr or ''
        if logger:
            if out.strip():
                logger.debug('STDOUT: %s', out[:8000])
            if err.strip():
                logger.debug('STDERR: %s', err[:8000])
        return r.returncode, out, err
    except FileNotFoundError as e:
        return 127, '', str(e)

# ---------- 主逻辑 ----------
@dataclass
class Paths:
    project_root: Path
    source_dir: Path
    output_dir: Path
    images_dir: Path
    logs_dir: Path

class Converter:
    def __init__(self, paths: Paths, aggressive: bool=False, prefer_commonmark: bool=False, template: Optional[Path]=None, keep_tmp: bool=True):
        self.p = paths
        self.aggressive = aggressive
        self.prefer_commonmark = prefer_commonmark
        self.template = template
        self.keep_tmp = keep_tmp
        self.logger = setup_logger(self.p.logs_dir)

    # ---------- 发现 ----------
    def discover(self) -> List[Tuple[str, Path]]:
        chapters_dir = self.p.source_dir / 'chapters'
        if not chapters_dir.exists():
            raise FileNotFoundError(f'章节目录缺失: {chapters_dir}')
        result: List[Tuple[str, Path]] = []
        preface = self.p.source_dir / '前言.md'
        if preface.exists():
            result.append(('preface', preface))
        # 按 CHAPTER_ORDER 顺序
        if CHAPTER_ORDER:
            for key in CHAPTER_ORDER:
                cdir = chapters_dir / key
                if not cdir.exists():
                    continue
                main_md = cdir / f'{key}.md'
                if main_md.exists():
                    result.append(('chapter', main_md))
                for sec in sorted(cdir.glob('section*.md')):
                    result.append(('section', sec))
        else:
            # 兜底：按自然顺序
            for md in sorted(chapters_dir.rglob('*.md')):
                tag = 'chapter' if md.parent.name.startswith('chapter') and md.stem.startswith('chapter') else 'section'
                result.append((tag, md))
        appendix = self.p.project_root / 'appendix'
        if appendix.exists():
            for app in sorted(appendix.glob('*.md')):
                result.append(('appendix', app))
        self.logger.info('发现 %d 个 Markdown 文件', len(result))
        return result

    # ---------- 预处理 ----------
    def _standardize_headings(self, content: str, file_path: Path, file_type: str) -> str:
        name = file_path.name
        if file_type == 'preface':
            # 确保前言保持一级标题
            content = re.sub(r'^#\\s+(.+)', r'# \\1', content, count=1, flags=re.MULTILINE)
        elif file_type == 'chapter' and name.startswith('chapter'):
            m = re.search(r'chapter(\\d+)', name)
            if m:
                key = f'chapter{int(m.group(1)):02d}'
                if key in CHAPTER_ORDER:
                    title = CHAPTER_ORDER[key]['title']
                    content = re.sub(r'^#\\s+.*', f'# {title}', content, count=1, flags=re.MULTILINE)
        elif file_type == 'section' and name.startswith('section'):
            sm = re.search(r'section(\\d+)-(\\d+)', name)
            if sm:
                cno, sno = int(sm.group(1)), int(sm.group(2))
                content = re.sub(r'^#\\s+(.+)', f'## {cno}.{sno} \\\\1', content, count=1, flags=re.MULTILINE)
                content = re.sub(r'^##\\s+(?!{}\\.{})((?!\\d+\\.\\d+).+)'.format(cno, sno), r'### \\1', content, flags=re.MULTILINE)
        # 行级裁剪
        for pat in UNNECESSARY_SECTION_PATTERNS:
            content = re.sub(pat, '', content, flags=re.MULTILINE)
        # 规范空行
        return re.sub(r'\\n{3,}', '\\n\\n', content)

    def _unify_image_paths(self, content: str) -> str:
        for pattern, repl in IMAGE_PATH_PATTERNS:
            content = re.sub(pattern, repl, content, flags=re.IGNORECASE)
        return content

    def _filter_blocks(self, content: str) -> str:
        # “温和模式”仅应用少数可明确识别的小节删除；--aggressive 时才启用全部模式
        pats = SECTION_BLOCK_REMOVE_PATTERNS if self.aggressive else [p for p in SECTION_BLOCK_REMOVE_PATTERNS if '参考文献' not in p]
        for pat in pats:
            content = re.sub(pat, '', content, flags=re.DOTALL | re.MULTILINE)
        return re.sub(r'\\n{3,}', '\\n\\n', content)

    def _strip_yaml_frontmatter(self, content: str) -> str:
        norm = content.replace('\\r\\n', '\\n')
        if norm.startswith('---'):
            norm = re.sub(YAML_FRONTMATTER_RE, '', norm, count=1)
        return norm

    def preprocess_one(self, file_type: str, path: Path) -> str:
        raw = read_text_safe(path)
        raw_lines = raw.count('\\n') + 1
        txt = self._strip_yaml_frontmatter(raw)
        txt = self._standardize_headings(txt, path, file_type)
        txt = self._unify_image_paths(txt)
        txt = self._filter_blocks(txt)
        cleaned_lines = txt.count('\\n') + 1
        self.logger.debug('[%s] %s: raw=%d, cleaned=%d', file_type, path.name, raw_lines, cleaned_lines)
        return f'% [FILE-BEGIN] {path.name} raw={raw_lines} cleaned={cleaned_lines}\\n' + txt + f'\\n% [FILE-END] {path.name}\\n'

    # ---------- 合并 ----------
    def merge_all(self, files: List[Tuple[str, Path]]) -> str:
        parts: List[str] = []
        for ftype, fpath in files:
            try:
                parts.append(self.preprocess_one(ftype, fpath))
                if ftype in ('chapter', 'preface'):
                    parts.append('\\n\\n\\\\newpage\\n\\n')
            except Exception as e:
                self.logger.error('读取/预处理失败 %s: %s', fpath, e)
        merged = '\\n'.join(parts)
        write_text_safe(self.p.output_dir / 'merged.md', PROTECTIVE_COMMENT + merged)
        preview = merged[:8000]
        write_text_safe(self.p.output_dir / 'debug_merged_preview.md', preview)
        self.logger.info('合并完成，字符数=%d', len(merged))
        return merged

    # ---------- 图片复制（基于引用优先） ----------
    def collect_referenced_images(self, merged_md: str) -> List[str]:
        refs = re.findall(r'!\\[[^\\]]*\\]\\(([^)]+)\\)', merged_md)
        # 仅收集 images/ 开头或相对路径文件
        paths = []
        for r in refs:
            if r.startswith('http'):  # 跳过外链
                continue
            # 去掉可能的 title "..." 片段
            clean = r.split('"')[0].strip()
            paths.append(clean)
        return paths

    def copy_images(self, merged_md: str):
        refs = set(self.collect_referenced_images(merged_md))
        copied, missing = 0, []
        candidate_dirs = [
            self.p.source_dir / 'assets' / 'images',
            self.p.source_dir / 'chapters' / 'images',
            self.p.source_dir / 'images',
            self.p.project_root / 'images',
            self.p.project_root / '参考' / 'extracted_images_ch6',
            self.p.project_root / '参考' / 'images',
        ]
        self.p.images_dir.mkdir(parents=True, exist_ok=True)
        # 如果 merged.md 没有引用，则走全量扫描兜底
        if not refs:
            self.logger.warning('未从 merged.md 检测到图片引用，切换为目录扫描模式')
            for d in candidate_dirs:
                if not d.exists(): continue
                for f in d.rglob('*'):
                    if f.is_file() and f.suffix.lower() in IMG_EXTS:
                        target = self.p.images_dir / f.name
                        if not target.exists():
                            try:
                                shutil.copy2(f, target); copied += 1
                            except Exception as e:
                                self.logger.error('复制失败 %s: %s', f, e)
            self.logger.info('目录扫描模式复制完成: %d', copied)
            if copied == 0:
                self._create_placeholders()
            return

        # 基于引用逐个查找复制
        for ref in refs:
            ref_name = Path(ref).name
            found_file = None
            for d in candidate_dirs:
                cand = d / ref_name
                if cand.exists():
                    found_file = cand; break
            if not found_file:
                missing.append(ref)
                continue
            new_name = (f'ch6_{found_file.name}' if 'extracted_images_ch6' in str(found_file) else found_file.name)
            target = self.p.images_dir / new_name
            if target.exists():
                continue
            try:
                shutil.copy2(found_file, target); copied += 1
            except Exception as e:
                self.logger.error('复制失败 %s: %s', found_file, e)
        self.logger.info('图片复制完成: %d, 缺失: %d', copied, len(missing))
        if missing:
            write_text_safe(self.p.output_dir / 'missing_images.txt', '\\n'.join(sorted(missing)))
        if copied == 0:
            self._create_placeholders()

    def _create_placeholders(self):
        try:
            from PIL import Image, ImageDraw, ImageFont
            for n in ['placeholder.png','image_001.png']:
                p = self.p.images_dir / n
                if p.exists(): continue
                img = Image.new('RGB',(400,300),'#DDDDDD'); d = ImageDraw.Draw(img)
                try: font = ImageFont.load_default(); d.text((30,130), n, fill='black', font=font)
                except Exception: d.text((30,130), n, fill='black')
                img.save(p)
        except Exception:
            for n in ['placeholder.png','image_001.png']:
                p = self.p.images_dir / n
                if not p.exists(): p.write_text(f'Placeholder for {n}', encoding='utf-8')

    # ---------- Pandoc ----------
    def _build_pandoc_cmd(self, md_file: Path, fmt: str, tex_out: Path) -> List[str]:
        cmd = [
            'pandoc', str(md_file),
            '--from', fmt,
            '--to', 'latex',
            '--standalone',
            '--toc',
            '--top-level-division=chapter',
            '--metadata', 'title=智慧水利平台架构与开发',
            '--metadata', 'author=教材编写组',
            '--metadata', 'documentclass=book',
            '--output', str(tex_out),
        ]
        if self.template and self.template.exists():
            cmd.extend(['--template', str(self.template)])
        return cmd

    def convert_to_latex(self, merged: str) -> Optional[Path]:
        temp_md = self.p.output_dir / 'temp_merged.md'
        write_text_safe(temp_md, PROTECTIVE_COMMENT + merged)
        tex_out = self.p.output_dir / '教材.tex'

        # 首选格式
        fmt_primary = 'commonmark_x+pipe_tables+fenced_divs+definition_lists' if self.prefer_commonmark else PANDOC_FROM_FORMAT
        fmt_fallback = 'commonmark_x+pipe_tables+fenced_divs+definition_lists'

        for idx, fmt in enumerate([fmt_primary, fmt_fallback] if fmt_primary != fmt_fallback else [fmt_primary]):
            cmd = self._build_pandoc_cmd(temp_md, fmt, tex_out)
            code, out, err = run_cmd(cmd, cwd=self.p.output_dir, logger=self.logger)
            if code == 0 and tex_out.exists():
                self.logger.info('Pandoc 成功（格式=%s）', fmt)
                return tex_out
            else:
                self.logger.warning('Pandoc 失败（格式=%s，code=%s），尝试降级…', fmt, code)
                # 如果是扩展不支持导致的错误（如 exit 23），继续尝试降级
                continue
        self.logger.error('Pandoc 转换失败，已保留 temp_merged.md 以便排查')
        return None

    # ---------- LaTeX 后处理 ----------
    def postprocess_latex(self, tex_file: Path) -> Path:
        content = read_text_safe(tex_file)

        # 在 \documentclass 后注入 ctex（一次）
        if '\\usepackage{ctex}' not in content:
            content = re.sub(r'(\\documentclass\\[.*?\\]\\{.*?\\}\\s*)', r'\\1\\n\\usepackage[UTF8]{ctex}\\n', content, count=1)
        # 前言用 \chapter*，兼容 \section 或 \chapter 情况
        content = re.sub(r'\\section\\{前言\\}', r'\\chapter*{前言}', content)
        content = re.sub(r'\\chapter\\{前言\\}', r'\\chapter*{前言}', content)

        # 兜底：避免无意的 $ 破坏结构（忽略已转义）
        def _esc_dollar(m): return m.group(0) if m.group(0).startswith('\\\\') else '\\\\$'
        content = re.sub(r'(?<!\\\\)\\$', _esc_dollar, content)

        write_text_safe(tex_file, content)
        self.logger.info('LaTeX 后处理完成')
        return tex_file

    # ---------- 编译 ----------
    def compile_pdf(self, tex_file: Path) -> Optional[Path]:
        old = os.getcwd(); os.chdir(self.p.output_dir)
        engines = ['xelatex','pdflatex','lualatex']
        engine = None
        try:
            for c in engines:
                code, _, _ = run_cmd([c, '--version'], logger=self.logger)
                if code == 0: engine = c; break
            if not engine:
                self.logger.warning('未找到 LaTeX 编译器，跳过 PDF 生成')
                return None
            for i in range(2):
                self.logger.info('LaTeX 第 %d 次编译（%s）', i+1, engine)
                # 不捕获输出，避免编码异常阻断流程
                subprocess.run([engine,'-interaction=nonstopmode','-halt-on-error', tex_file.name],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            pdf = self.p.output_dir / '教材.pdf'
            if pdf.exists() and pdf.stat().st_size > 150 * 1024:
                self.logger.info('PDF 生成完成: %s', pdf)
                return pdf
            self.logger.warning('PDF 不完整，已保留 .tex')
            return None
        finally:
            os.chdir(old)

    # ---------- 主流程 ----------
    def run(self):
        files = self.discover()
        merged = self.merge_all(files)
        # 图片优先基于引用复制
        self.copy_images(merged)
        tex = self.convert_to_latex(merged)
        if tex is None:
            self.logger.error('停止：未生成 .tex 文件')
            return
        tex = self.postprocess_latex(tex)
        _ = self.compile_pdf(tex)
        # 运行健康报告
        self.health_report(tex)

    def health_report(self, tex_file: Path):
        report = []
        try:
            t = read_text_safe(tex_file)
            chapters = len(re.findall(r'\\chapter', t))
            sections = len(re.findall(r'\\section', t))
            report.append(f'chapters={chapters}, sections={sections}')
        except Exception:
            report.append('无法统计章节信息')
        miss = self.p.output_dir / 'missing_images.txt'
        if miss.exists():
            m = miss.read_text(encoding='utf-8', errors='ignore').strip().splitlines()
            report.append(f'missing_images={len(m)} (see {miss.name})')
        self.logger.info('HEALTH: %s', '; '.join(report))

# ---------- CLI ----------
def parse_args():
    ap = argparse.ArgumentParser(description='健壮的 Markdown→LaTeX 转换器')
    ap.add_argument('--project-root', type=Path, default=Path('.'), help='项目根目录（包含 docs/）')
    ap.add_argument('--source-dir', type=Path, default=None, help='源码目录（默认 <project-root>/docs）')
    ap.add_argument('--output-dir', type=Path, default=Path('输出'), help='输出目录')
    ap.add_argument('--prefer-commonmark', action='store_true', help='优先使用 commonmark_x 解析器')
    ap.add_argument('--aggressive', action='store_true', help='启用更强的区块删除（谨慎）')
    ap.add_argument('--template', type=Path, default=None, help='自定义 LaTeX 模板路径')
    ap.add_argument('--keep-tmp', action='store_true', help='保留中间文件（默认保留）')
    return ap.parse_args()

def main():
    args = parse_args()
    project_root = args.project_root.resolve()
    source_dir = args.source_dir.resolve() if args.source_dir else (project_root / 'docs').resolve()
    output_dir = args.output_dir if args.output_dir.is_absolute() else (project_root / args.output_dir)
    images_dir = output_dir / 'images'
    logs_dir = output_dir / 'logs'
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = Paths(project_root=project_root, source_dir=source_dir, output_dir=output_dir, images_dir=images_dir, logs_dir=logs_dir)
    conv = Converter(paths, aggressive=args.aggressive, prefer_commonmark=args.prefer_commonmark, template=args.template, keep_tmp=args.keep_tmp)
    conv.run()

if __name__ == '__main__':
    main()
