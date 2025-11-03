#!/usr/bin/env python3
"""
改进版 智慧水利教材转换器

特性概览：
- 正确的章节顺序：主章节内容在前，小节内容在后
- 智能标题处理：保留中文章节标题，不重复生成
- 去除“本章小节”导读块，避免与实际小节重复
- 统一图片路径并复制到 publish/latex/images/
- 一键转换（--convert-only）与仅构建（--build-only）

输出目录：publish/latex
  - 主文件：publish/latex/main.tex
  - 前言：publish/latex/chapters/preface.tex
  - 章节：publish/latex/chapters/chapterXX.tex
  - 图片：publish/latex/images/
"""

import argparse
import logging
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional, List, Tuple

# 确保能从 tools 目录导入模块（无论在仓库根或tools下运行）
TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from converter_config import ConverterConfig, PathManager  # type: ignore
from content_processors import (
    ContentProcessor,
    PreSanitizeProcessor,
    YamlProtectionProcessor,
    AdmonitionProcessor,
    CodeProcessor,
)  # type: ignore
from convert_preface_only import sanitize_preface as _sanitize_preface, transform_admonitions as _transform_admonitions  # type: ignore
from latex_templates import LaTeXTemplateGenerator  # type: ignore
from latex_validator import LaTeXValidator  # type: ignore


def setup_logging(log_file: Path) -> logging.Logger:
    logger = logging.getLogger("improved_converter")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    fmt = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(fmt)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(fmt)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger


def find_pandoc() -> str:
    cmd = 'pandoc'
    try:
        r = subprocess.run([cmd, '--version'], capture_output=True, text=True)
        if r.returncode == 0:
            return cmd
    except Exception:
        pass
    return r"/mnt/c/Program Files/Pandoc/pandoc.exe"


def find_xelatex() -> str:
    cmd = 'xelatex'
    try:
        r = subprocess.run([cmd, '--version'], capture_output=True, text=True)
        if r.returncode == 0:
            return cmd
    except Exception:
        pass
    return r"/mnt/c/texlive/2025/bin/windows/xelatex.exe"


def remove_outline_block(md_text: str) -> str:
    """移除“## 本章小节”到下一个同级标题之间的导读块。
    仅影响导读，不影响真正的小节文件内容。
    """
    pattern = r"^##\s*本章小节\s*\n[\s\S]*?(?=^##\s+|\Z)"
    return re.sub(pattern, "", md_text, flags=re.MULTILINE)


class ImprovedConverter:
    def __init__(self, project_root: Path, convert_only: bool = False, build_only: bool = False,
                 chapters: Optional[List[int]] = None, clean: bool = False):
        self.project_root = project_root
        # 使用 publish/latex 作为输出目录
        self.config = ConverterConfig(
            source_dir=str(project_root / 'docs' / 'chapters'),
            preface_file=str(project_root / 'docs' / '前言.md'),
            output_dir=str(project_root / 'output'),
        )
        # 初始化周边组件
        self.path_manager = PathManager(self.config)
        self.processor = ContentProcessor()
        self.template = LaTeXTemplateGenerator(self.config)
        self.validator = LaTeXValidator()

        # 日志
        self.log_file = project_root / 'conversion.log'
        self.logger = setup_logging(self.log_file)

        # 模式
        self.convert_only = convert_only
        self.build_only = build_only
        self.selected_chapters = chapters
        self.clean_before = clean

        # 计数
        self.images_copied = 0
        self.files_converted: List[Path] = []

        # 目录准备
        Path(self.config.output_dir, 'chapters').mkdir(parents=True, exist_ok=True)
        Path(self.config.output_dir, 'images').mkdir(parents=True, exist_ok=True)

    def _clean_legacy(self):
        """清理 publish/latex，及非选定章节的 output/chapters/chapter*.tex"""
        import shutil
        pub = self.project_root / 'publish' / 'latex'
        if pub.exists():
            try:
                shutil.rmtree(pub)
                self.logger.info(f"已清理旧目录: {pub}")
            except Exception as e:
                self.logger.warning(f"清理失败 {pub}: {e}")
        if self.selected_chapters:
            keep = {f"chapter{n:02d}.tex" for n in self.selected_chapters}
            od = Path(self.config.output_dir) / 'chapters'
            if od.exists():
                for p in od.glob('chapter*.tex'):
                    if p.name not in keep:
                        try:
                            p.unlink()
                        except Exception:
                            pass
                # 也清理不相关的中间 markdown
                keep_md = {f"chapter{n:02d}.md" for n in self.selected_chapters}
                for p in od.glob('chapter*.md'):
                    if p.name not in keep_md:
                        try:
                            p.unlink()
                        except Exception:
                            pass

    # ---------- 基础工具 ----------
    def _to_win_path(self, p: Path) -> str:
        try:
            r = subprocess.run(["wslpath", "-w", str(p)], capture_output=True, text=True)
            if r.returncode == 0:
                return r.stdout.strip()
        except Exception:
            pass
        return str(p)

    def _pandoc_convert(self, md_path: Path, tex_path: Path) -> bool:
        pandoc = find_pandoc()
        in_path = str(md_path)
        out_path = str(tex_path)
        # Windows pandoc.exe 时转换路径
        if pandoc.lower().endswith('.exe'):
            in_path = self._to_win_path(md_path)
            out_path = self._to_win_path(tex_path)
        # 启用数学公式（$...$）、保留原始TeX、支持YAML元数据；并使用 listings 风格的代码块
        cmd = [
            pandoc,
            in_path,
            '-o', out_path,
            '--wrap=none',
            '--from=markdown+tex_math_dollars+raw_tex+yaml_metadata_block',
            '--to=latex',
            '--listings'
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            self.logger.error(f"Pandoc失败: {md_path}\n{r.stderr}")
            return False
        return True

    # ---------- 资源复制 ----------
    def _copy_images(self) -> None:
        import shutil
        self.logger.info("开始复制图片文件")
        images_dir = Path(self.config.output_dir) / 'images'
        images_dir.mkdir(exist_ok=True)

        def copy_tree(src: Path, dst: Path):
            nonlocal images_dir
            if not src.exists():
                return
            try:
                before = len(list(images_dir.rglob('*')))
                shutil.copytree(src, dst, dirs_exist_ok=True)
                after = len(list(images_dir.rglob('*')))
                self.images_copied += max(0, after - before)
                self.logger.info(f"复制图片: {src} -> {dst}")
            except Exception as e:
                self.logger.warning(f"复制图片失败 {src}: {e}")

        # assets/images -> publish/latex/images
        assets_images = self.project_root / 'assets' / 'images'
        copy_tree(assets_images, images_dir)

        # docs/chapters/images/* -> publish/latex/images/*
        chapters_common_images = Path(self.config.source_dir) / 'images'
        if chapters_common_images.exists():
            for sub in chapters_common_images.iterdir():
                if sub.is_dir():
                    copy_tree(sub, images_dir / sub.name)

        # docs/chapters/chapterXX/images -> publish/latex/images/chapterXX
        for chapter_dir in Path(self.config.source_dir).iterdir():
            if chapter_dir.is_dir() and chapter_dir.name.startswith('chapter'):
                chapter_images = chapter_dir / 'images'
                if chapter_images.exists():
                    copy_tree(chapter_images, images_dir / chapter_dir.name)

    # ---------- 转换流程 ----------
    def _process_markdown(self, md_text: str) -> str:
        # 先去掉导读块
        md_text = remove_outline_block(md_text)
        # 内容处理流水线（标题/图片/公式/代码/告警等）
        return self.processor.process_all(md_text)

    def _extract_concluding_blocks(self, md_text: str) -> tuple[str, str]:
        """从主文件中抽取固定结尾块（本章小结/参考文献/思考题等），返回 (主体, 结尾块)

        规则：匹配以下标题开头的段落，直到同级或更高级标题或文末：
        - 本章小结, 本节小结, 参考文献, 思考题与练习, 思考题, 练习
        """
        import re
        targets = [
            '本章小结', '本节小结', '参考文献', '思考题与练习', '思考题', '练习'
        ]
        # 捕获任意级别井号标题，加可选空格
        pattern = re.compile(rf"^(?P<hash>#+)\s*(?P<title>{'|'.join(map(re.escape, targets))})\s*$", re.MULTILINE)

        body_parts: list[str] = []
        tail_parts: list[str] = []
        last = 0
        for m in pattern.finditer(md_text):
            # 追加之前片段到 body
            body_parts.append(md_text[last:m.start()])
            # 找下一个同级或更高级标题
            level = len(m.group('hash'))
            # 搜索从 m.end() 开始的下一标题
            next_pat = re.compile(rf"^#{{1,{level}}}\s+", re.MULTILINE)
            n = next_pat.search(md_text, m.end())
            end = n.start() if n else len(md_text)
            tail_parts.append(md_text[m.start():end].strip('\n'))
            last = end
        body_parts.append(md_text[last:])
        body = ''.join(body_parts).strip('\n')
        tail = '\n\n'.join(p for p in tail_parts if p).strip('\n')
        return body, tail

    def _rewrite_image_paths_for_chapter(self, md_text: str, chapter_num: int) -> str:
        """将形如 (images/xxx) 的相对图片路径改为 (images/chapterNN/xxx)

        这样与拷贝策略保持一致：chapterXX/images -> output/images/chapterXX
        仅重写以 'images/' 开头的相对路径（不处理 http/绝对/上级路径）。
        """
        import re
        prefix = f"images/chapter{chapter_num:02d}/"
        def repl(m):
            alt = m.group(1)
            path = m.group(2)
            # 只处理以 images/ 开头且不含 chapter 前缀的
            if path.startswith('images/'):  
                # 避免重复注入 chapterNN
                if not path.startswith(prefix):
                    return f"![{alt}]({prefix}{path[len('images/'):]})"
            return m.group(0)
        return re.sub(r'!\[(.*?)\]\(([^)]+)\)', repl, md_text)

    def _process_preface(self, md_text: str) -> str:
        """前言专用处理：对齐 preface-only 的转换经验，避免章节编号等干扰。"""
        # 直接复用前言专用的转换经验
        text = _sanitize_preface(md_text)
        text = YamlProtectionProcessor().process(text)
        text = _transform_admonitions(text)
        return text

    def convert_preface(self) -> Optional[Path]:
        preface_md = Path(self.config.preface_file)
        if not preface_md.exists():
            self.logger.warning(f"前言不存在: {preface_md}")
            return None
        md_text = preface_md.read_text(encoding='utf-8')
        processed = self._process_preface(md_text)
        preface_tmp_md = Path(self.config.output_dir) / 'chapters' / 'preface.md'
        preface_tmp_md.write_text(processed, encoding='utf-8')

        preface_tex = Path(self.config.output_dir) / 'chapters' / 'preface.tex'
        ok = self._pandoc_convert(preface_tmp_md, preface_tex)
        if ok:
            # 归一化前言标题为不编号章（不加入目录）
            try:
                tex = preface_tex.read_text(encoding='utf-8')
                # 首个 \section{前言} -> \chapter*{前言}
                tex = re.sub(r"^\\section\{前言\}.*$",
                              lambda m: "\\chapter*{前言}",
                              tex, count=1, flags=re.MULTILINE)
                # 其余 \section 以及 subsections 变为无编号（不加入目录）
                tex = re.sub(r"^\\section\{([^}]+)\}",
                              lambda m: f"\\section*{{{m.group(1)}}}",
                              tex, flags=re.MULTILINE)
                tex = re.sub(r"^\\subsection\{([^}]+)\}",
                              lambda m: f"\\section*{{{m.group(1)}}}",
                              tex, flags=re.MULTILINE)
                tex = re.sub(r"^\\subsubsection\{([^}]+)\}",
                              lambda m: f"\\subsection*{{{m.group(1)}}}",
                              tex, flags=re.MULTILINE)
                preface_tex.write_text(tex, encoding='utf-8')
            except Exception as e:
                self.logger.warning(f"前言标题归一化失败: {e}")
            self.files_converted.append(preface_tex)
            self.logger.info("前言转换成功")
            return preface_tex
        else:
            self.logger.error("前言转换失败")
            return None

    def convert_chapter(self, chapter_num: int) -> Optional[Path]:
        src_dir = Path(self.config.source_dir) / f"chapter{chapter_num:02d}"
        if not src_dir.exists():
            self.logger.warning(f"章节目录不存在: {src_dir}")
            return None

        parts: List[Tuple[str, bool]] = []  # (text, is_main)
        # 主文件（抽取结尾固定块，主体放前，尾块延后拼接）
        main_file = src_dir / f"chapter{chapter_num:02d}.md"
        if main_file.exists():
            raw_main = main_file.read_text(encoding='utf-8')
            main_body, main_tail = self._extract_concluding_blocks(raw_main)
            parts.append((main_body, True))
            if main_tail:
                # 结尾固定块先暂存，稍后拼接到末尾
                parts.append((f"\n\n{main_tail}\n\n", True))
            self.logger.info(f"读取主文件: {main_file.name}")
        # 小节文件（按名称排序）
        for sec in sorted(src_dir.glob('section*.md')):
            parts.append((sec.read_text(encoding='utf-8'), False))
            self.logger.info(f"读取小节: {sec.name}")

        if not parts:
            self.logger.warning(f"第{chapter_num}章无内容，跳过")
            return None

        # 先处理主文件主体（main_body，unnumbered），再处理所有小节（numbered），最后如果有 main_tail 再作为 unnumbered 追加
        processed_chunks: List[str] = []
        for text, is_main in parts:
            if is_main and text.strip() == '':
                continue
            ctx = {'chapter_num': chapter_num}
            if is_main:
                ctx['main_body'] = True
            processed_chunks.append(self.processor.process_all(text, context=ctx))

        processed = '\n\n'.join(processed_chunks)

        out_md = Path(self.config.output_dir) / 'chapters' / f"chapter{chapter_num:02d}.md"
        out_md.write_text(processed, encoding='utf-8')

        out_tex = Path(self.config.output_dir) / 'chapters' / f"chapter{chapter_num:02d}.tex"
        ok = self._pandoc_convert(out_md, out_tex)
        if ok:
            # 生成后做一次LaTeX语法修复（含数学转义恢复等）
            try:
                self.validator.validate_file(out_tex)
            except Exception as e:
                self.logger.warning(f"LaTeX修复失败: {e}")
            self.files_converted.append(out_tex)
            self.logger.info(f"第{chapter_num}章转换成功")
            return out_tex
        else:
            self.logger.error(f"第{chapter_num}章转换失败")
            return None

    def _adjust_chapter1_tex(self, tex_path: Path) -> None:
        """按需求：
        - 章标题不显示编号（chapter*），但保持计数为1，使后续编号为1.x
        - 将“学习目标”“引言”“关键概念”改为无编号的小节（section*，并入目录）
        - 确保后续第一个编号小节为“1.1 软件概述”
        """
        s = tex_path.read_text(encoding='utf-8')
        # 章标题：首个 \chapter{...} → \chapter* + ToC + set counters
        s = re.sub(
            r"\\chapter\{([^}]+)\}",
            r"\\chapter*{\1}\n\\addcontentsline{toc}{chapter}{\1}\n\\setcounter{chapter}{1}\n\\setcounter{section}{0}",
            s,
            count=1,
        )
        # 指定无编号的小节
        for t in ["学习目标", "引言", "关键概念"]:
            s = re.sub(
                rf"^\\section\{{{re.escape(t)}\}}",
                rf"\\section*{{{t}}}\n\\addcontentsline{{toc}}{{section}}{{{t}}}",
                s,
                flags=re.MULTILINE,
            )
        # 将“思考题与练习”作为当前节的小节（例如1.1.6）
        s = re.sub(r"^\\section\{思考题与练习\}", r"\\subsection{思考题与练习}", s, flags=re.MULTILINE)
        tex_path.write_text(s, encoding='utf-8')

    def generate_main_tex(self) -> Optional[Path]:
        try:
            # 统一使用带章节列表的模板生成方式，避免使用旧模板
            if self.selected_chapters:
                nums = self.selected_chapters
            else:
                nums = list(range(1, self.config.chapter_count + 1))
            main_content = self.template.generate_main_template_with(nums)
            main_tex = Path(self.config.output_dir) / 'main.tex'
            main_tex.write_text(main_content, encoding='utf-8')
            self.logger.info(f"主LaTeX文件生成: {main_tex}")
            return main_tex
        except Exception as e:
            self.logger.error(f"主LaTeX文件生成失败: {e}")
            return None

    def compile_pdf(self) -> Optional[Path]:
        main_tex = Path(self.config.output_dir) / 'main.tex'
        if not main_tex.exists():
            self.logger.error("main.tex 不存在，无法编译")
            return None
        xelatex = find_xelatex()
        # 进入输出目录编译
        cwd = os.getcwd()
        try:
            os.chdir(self.config.output_dir)
            # 进行三次编译，确保目录/交叉引用/长表宽度等完全稳定
            for i in range(3):
                r = subprocess.run([xelatex, '-interaction=nonstopmode', 'main.tex'], capture_output=True, text=True)
                if r.returncode != 0:
                    self.logger.warning(f"第{i+1}次编译返回非零，继续后续编译以稳定目录/引用")
        finally:
            os.chdir(cwd)

        pdf = Path(self.config.output_dir) / 'main.pdf'
        if pdf.exists():
            self.logger.info(f"PDF 编译完成: {pdf}")
            return pdf
        else:
            self.logger.error("PDF 未生成，请检查 LaTeX 日志")
            return None

    def run(self) -> int:
        self.logger.info("🚀 改进版转换器启动")
        if self.clean_before:
            self._clean_legacy()
        self._copy_images()

        if not self.build_only:
            # 转换前言与章节
            self.convert_preface()
            success_chapters = 0
            to_convert = self.selected_chapters if self.selected_chapters else list(range(1, self.config.chapter_count + 1))
            for i in to_convert:
                if self.convert_chapter(i):
                    success_chapters += 1

            total = len(to_convert)
            self.logger.info(f"转换统计：成功章节数 {success_chapters}/{total}，图片复制 {self.images_copied} 个项")

            # 生成主文件
            self.generate_main_tex()

            if self.convert_only:
                self.logger.info("已按 --convert-only 完成转换")
                return 0

        # 编译
        if self.build_only:
            self.logger.info("按 --build-only 开始编译")
        pdf = self.compile_pdf()
        return 0 if pdf else 1


def parse_args(argv: List[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Improved textbook converter")
    p.add_argument('--project-root', default=str(Path(__file__).resolve().parents[1]), help='项目根目录')
    p.add_argument('--convert-only', action='store_true', help='仅转换 Markdown 到 LaTeX')
    p.add_argument('--build-only', action='store_true', help='仅编译 LaTeX')
    p.add_argument('--chapters', type=str, default='', help='仅处理的章节编号，逗号分隔，如 1 或 1,2')
    p.add_argument('--clean', action='store_true', help='转换前清理旧输出（删除 publish/latex，并清理多余章节 tex）')
    return p.parse_args(argv)


def main(argv: List[str]) -> int:
    args = parse_args(argv)
    root = Path(args.project_root).resolve()
    chapters = None
    if args.chapters.strip():
        try:
            chapters = [int(x) for x in args.chapters.split(',') if x.strip()]
        except Exception:
            chapters = None
    conv = ImprovedConverter(project_root=root, convert_only=args.convert_only, build_only=args.build_only,
                             chapters=chapters, clean=args.clean)
    return conv.run()


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
