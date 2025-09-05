"""
智慧水利教材转换器 - 主应用程序
软件工程设计：外观模式 + 命令模式
"""

import os
import sys
import re
import logging
import subprocess
from pathlib import Path
from typing import Optional, List

from converter_config import ConverterConfig, PathManager, DEFAULT_CONFIG
from content_processors import ContentProcessor
from latex_templates import LaTeXTemplateGenerator, LaTeXPostProcessor
from latex_validator import LaTeXValidator
from simple_enhancer import SimpleContentEnhancer

class ConverterApplication:
    """转换器主应用程序"""
    
    def __init__(self, config: Optional[ConverterConfig] = None):
        self.config = config or DEFAULT_CONFIG
        self.path_manager = PathManager(self.config)
        self.content_processor = ContentProcessor()
        self.enhancer = SimpleContentEnhancer()
        self.template_generator = LaTeXTemplateGenerator(self.config)
        self.post_processor = LaTeXPostProcessor()
        self.latex_validator = LaTeXValidator()
        
        # 配置日志
        self._setup_logging()
        self.logger = logging.getLogger(__name__)
    
    def _setup_logging(self):
        """配置日志系统"""
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[
                logging.FileHandler('converter.log', encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    def convert_preface(self) -> bool:
        """转换前言"""
        self.logger.info("开始转换前言")
        
        preface_path = Path(self.config.preface_file)
        if not preface_path.exists():
            self.logger.warning(f"前言文件不存在: {preface_path}")
            return False
        
        try:
            # 读取前言内容
            with open(preface_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 处理内容
            processed_content = self.content_processor.process_all(content)
            
            # 后处理
            final_content = self.post_processor.post_process(processed_content)
            
            # 保存处理后的markdown
            preface_md_path = Path(self.config.output_dir) / "chapters" / "preface.md"
            with open(preface_md_path, 'w', encoding='utf-8') as f:
                f.write(final_content)
            
            # 转换为LaTeX
            preface_tex_path = Path(self.config.output_dir) / "chapters" / "preface.tex"
            success = self._pandoc_convert(preface_md_path, preface_tex_path)
            
            if success:
                self.logger.info("前言转换成功")
                return True
            else:
                self.logger.error("前言转换失败")
                return False
                
        except Exception as e:
            self.logger.error(f"转换前言时出错: {e}")
            return False
    
    def convert_chapter(self, chapter_num: int) -> bool:
        """转换单个章节"""
        self.logger.info(f"开始转换第{chapter_num}章")
        
        chapter_dir = self.path_manager.get_source_chapter_dir(chapter_num)
        if not chapter_dir.exists():
            self.logger.warning(f"第{chapter_num}章目录不存在: {chapter_dir}")
            return False
        
        try:
            # 收集章节内容
            content_parts = []
            
            # 主章节文件
            main_file = chapter_dir / f"chapter{chapter_num:02d}.md"
            if main_file.exists():
                with open(main_file, 'r', encoding='utf-8') as f:
                    content_parts.append(f.read())
                self.logger.info(f"  已读取主文件: {main_file.name}")
            
            # 小节文件
            section_files = sorted(chapter_dir.glob("section*.md"))
            for section_file in section_files:
                with open(section_file, 'r', encoding='utf-8') as f:
                    content_parts.append(f.read())
                self.logger.info(f"  已读取小节: {section_file.name}")
            
            if not content_parts:
                self.logger.warning(f"第{chapter_num}章没有内容")
                return False
            
            # 合并内容
            merged_content = '\n\n'.join(content_parts)
            
            # 添加章节模板头部
            chapter_title = self.config.get_chapter_title(chapter_num)
            chapter_header = self.template_generator.generate_chapter_template(chapter_num, chapter_title)
            full_content = chapter_header + merged_content
            
            # 处理内容
            processed_content = self.content_processor.process_all(full_content)
            
            # 后处理
            final_content = self.post_processor.post_process(processed_content)
            
            # 保存处理后的markdown
            chapter_md_path = Path(self.config.output_dir) / "chapters" / f"chapter{chapter_num:02d}.md"
            with open(chapter_md_path, 'w', encoding='utf-8') as f:
                f.write(final_content)
            
            # 转换为LaTeX
            chapter_tex_path = self.path_manager.get_output_chapter_tex(chapter_num)
            success = self._pandoc_convert(chapter_md_path, chapter_tex_path)
            
            if success:
                self.logger.info(f"第{chapter_num}章转换成功")
                return True
            else:
                self.logger.error(f"第{chapter_num}章转换失败")
                return False
                
        except Exception as e:
            self.logger.error(f"转换第{chapter_num}章时出错: {e}")
            return False
    
    def _pandoc_convert(self, input_path: Path, output_path: Path) -> bool:
        """使用pandoc转换文件"""
        try:
            cmd = [
                'pandoc',
                str(input_path),
                '-o', str(output_path),
                '--wrap=none',
                '--from=markdown-yaml_metadata_block',  # 禁用YAML元数据块解析
                '--to=latex'
                # 移除--standalone，生成章节片段而非完整文档
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
            
            if result.returncode == 0:
                self.logger.debug(f"Pandoc转换成功: {input_path} -> {output_path}")
                # 后处理生成的LaTeX以修复问题
                self._post_process_tex(output_path)
                return True
            else:
                self.logger.error(f"Pandoc转换失败: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Pandoc转换出错: {e}")
            return False
    
    def _post_process_tex(self, tex_path: Path) -> None:
        """后处理LaTeX文件以修复转义和格式问题"""
        try:
            with open(tex_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 修复过度转义的LaTeX命令
            fixes = [
                # 修复章节命令的过度转义
                (r'\\textbackslash chapter\{', r'\\chapter{'),
                (r'\\textbackslash section\{', r'\\section{'),
                (r'\\textbackslash subsection\{', r'\\subsection{'),
                
                # 修复数学环境的过度转义  
                (r'\\textbackslash begin\{equation\}', r'\\begin{equation}'),
                (r'\\textbackslash end\{equation\}', r'\\end{equation}'),
                
                # 修复代码环境的过度转义
                (r'\\textbackslash begin\{lstlisting\}', r'\\begin{lstlisting}'),
                (r'\\textbackslash end\{lstlisting\}', r'\\end{lstlisting}'),
                
                # 修复tcolorbox的过度转义
                (r'\\textbackslash begin\{tcolorbox\}', r'\\begin{tcolorbox}'),
                (r'\\textbackslash end\{tcolorbox\}', r'\\end{tcolorbox}'),
                
                # 修复图片环境的过度转义
                (r'\\textbackslash begin\{figure\}', r'\\begin{figure}'),
                (r'\\textbackslash end\{figure\}', r'\\end{figure}'),
                (r'\\textbackslash centering', r'\\centering'),
                (r'\\textbackslash includegraphics', r'\\includegraphics'),
                (r'\\textbackslash caption\{', r'\\caption{'),
                
                # 修复表格环境过度转义
                (r'\\textbackslash begin\{table\}', r'\\begin{table}'),
                (r'\\textbackslash end\{table\}', r'\\end{table}'),
                (r'\\textbackslash begin\{tabular\}', r'\\begin{tabular}'),
                (r'\\textbackslash end\{tabular\}', r'\\end{tabular}'),
                (r'\\textbackslash begin\{longtable\}', r'\\begin{longtable}'),
                (r'\\textbackslash end\{longtable\}', r'\\end{longtable}'),
                
                # 修复其他常见的过度转义
                (r'\\textbackslash texttt\{', r'\\texttt{'),
                (r'\\textbackslash textbf\{', r'\\textbf{'),
                (r'\\textbackslash textit\{', r'\\textit{'),
                (r'\\textbackslash n', r'\\n'),
                
                # 修复通用的textbackslash模式
                (r'\\textbackslash ([a-zA-Z]+)\{', r'\\\1{'),
                
                # 修复表格内的特殊情况
                (r'\\textbackslash begin\\{figure\\}\\{\\[\\}htbp\\{\\}\\}', r'\\begin{figure}[htbp]'),
                (r'\\textbackslash end\\{figure\\}', r'\\end{figure}'),
                (r'\\textbar\\{\\}', r'|'),
                
                # 修复双重转义
                (r'\\\\\\\\', r'\\\\'),
            ]
            
            for pattern, replacement in fixes:
                content = re.sub(pattern, replacement, content)
            
            # 保存修复后的内容
            with open(tex_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # 执行增强内容处理
            with open(tex_path, 'r', encoding='utf-8') as f:
                tex_content = f.read()
                
            # 提取章节号
            chapter_num = self._extract_chapter_number(tex_path)
            
            # 应用增强处理
            if chapter_num:
                enhanced_content = self.enhancer.enhance_chapter(tex_content, chapter_num)
            else:
                enhanced_content = tex_content  # 前言不需要特殊处理
            
            # 保存增强处理后的内容
            with open(tex_path, 'w', encoding='utf-8') as f:
                f.write(enhanced_content)
            
            # 执行LaTeX语法验证和进一步修复
            self.latex_validator.validate_file(tex_path)
                
            self.logger.debug(f"LaTeX后处理、增强处理和语法验证完成: {tex_path}")
            
        except Exception as e:
            self.logger.error(f"LaTeX后处理失败 {tex_path}: {e}")
    
    def _extract_chapter_number(self, tex_path: Path) -> Optional[int]:
        """从文件路径提取章节号"""
        try:
            filename = tex_path.stem
            if filename.startswith('chapter'):
                chapter_str = filename.replace('chapter', '').lstrip('0')
                if chapter_str:
                    return int(chapter_str)
            return None
        except (ValueError, AttributeError):
            return None
    
    def generate_main_tex(self) -> bool:
        """生成主LaTeX文件"""
        self.logger.info("生成主LaTeX文件")
        
        try:
            main_template = self.template_generator.generate_main_template()
            main_tex_path = self.path_manager.get_main_tex_path()
            
            with open(main_tex_path, 'w', encoding='utf-8') as f:
                f.write(main_template)
            
            self.logger.info(f"主LaTeX文件已生成: {main_tex_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"生成主LaTeX文件时出错: {e}")
            return False
    
    def compile_latex(self) -> bool:
        """编译LaTeX生成PDF"""
        self.logger.info("开始编译LaTeX")
        
        main_tex_path = self.path_manager.get_main_tex_path()
        if not main_tex_path.exists():
            self.logger.error("主LaTeX文件不存在")
            return False
        
        try:
            # 切换到输出目录
            original_cwd = os.getcwd()
            os.chdir(self.config.output_dir)
            
            # 第一次编译
            self.logger.info("第一次XeLaTeX编译")
            result1 = subprocess.run(
                ['xelatex', '-interaction=nonstopmode', 'main.tex'],
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            
            if result1.returncode != 0:
                self.logger.error("第一次编译失败")
                self.logger.error(result1.stderr)
                os.chdir(original_cwd)
                return False
            
            # 第二次编译（生成正确的目录）
            self.logger.info("第二次XeLaTeX编译")
            result2 = subprocess.run(
                ['xelatex', '-interaction=nonstopmode', 'main.tex'],
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            
            os.chdir(original_cwd)
            
            if result2.returncode == 0:
                pdf_path = Path(self.config.output_dir) / "main.pdf"
                if pdf_path.exists():
                    self.logger.info(f"PDF编译成功: {pdf_path}")
                    return True
                else:
                    self.logger.error("PDF文件未生成")
                    return False
            else:
                self.logger.error("第二次编译失败")
                self.logger.error(result2.stderr)
                return False
                
        except Exception as e:
            self.logger.error(f"编译LaTeX时出错: {e}")
            os.chdir(original_cwd)
            return False
    
    def _copy_images(self) -> None:
        """复制图片文件到输出目录"""
        self.logger.info("开始复制图片文件")
        
        # 确保images目录存在
        images_dir = Path(self.config.output_dir) / 'images'
        images_dir.mkdir(exist_ok=True)
        
        import shutil
        
        # 复制assets中的图片
        source_images = Path(self.config.source_dir).parent / 'assets' / 'images'
        if source_images.exists():
            try:
                shutil.copytree(source_images, images_dir, dirs_exist_ok=True)
                self.logger.info(f"Assets图片复制完成: {source_images} -> {images_dir}")
            except Exception as e:
                self.logger.warning(f"复制assets图片时出错: {e}")
        
        # 复制chapters中的图片
        chapters_images = Path(self.config.source_dir) / 'images'
        if chapters_images.exists():
            try:
                # 逐个复制章节图片目录
                for chapter_img_dir in chapters_images.iterdir():
                    if chapter_img_dir.is_dir():
                        dest_dir = images_dir / chapter_img_dir.name
                        shutil.copytree(chapter_img_dir, dest_dir, dirs_exist_ok=True)
                        self.logger.info(f"章节图片复制完成: {chapter_img_dir} -> {dest_dir}")
            except Exception as e:
                self.logger.warning(f"复制章节图片时出错: {e}")
        
        # 也检查各个章节目录中的images文件夹
        source_root = Path(self.config.source_dir)
        for chapter_dir in source_root.iterdir():
            if chapter_dir.is_dir() and chapter_dir.name.startswith('chapter'):
                chapter_images = chapter_dir / 'images'
                if chapter_images.exists():
                    try:
                        dest_dir = images_dir / chapter_dir.name
                        dest_dir.mkdir(exist_ok=True)
                        shutil.copytree(chapter_images, dest_dir, dirs_exist_ok=True)
                        self.logger.info(f"章节专属图片复制完成: {chapter_images} -> {dest_dir}")
                    except Exception as e:
                        self.logger.warning(f"复制{chapter_dir.name}图片时出错: {e}")

    def convert_all(self) -> bool:
        """转换所有内容"""
        self.logger.info("🚀 开始完整转换流程")
        
        # 首先复制图片文件
        self._copy_images()
        
        # 转换前言
        preface_success = self.convert_preface()
        
        # 转换所有章节
        chapter_results = []
        for i in range(1, self.config.chapter_count + 1):
            success = self.convert_chapter(i)
            chapter_results.append((i, success))
        
        # 统计转换结果
        successful_chapters = [num for num, success in chapter_results if success]
        failed_chapters = [num for num, success in chapter_results if not success]
        
        self.logger.info(f"转换结果统计:")
        self.logger.info(f"  前言: {'✅' if preface_success else '❌'}")
        self.logger.info(f"  成功章节: {successful_chapters}")
        if failed_chapters:
            self.logger.warning(f"  失败章节: {failed_chapters}")
        
        # 生成主LaTeX文件
        main_tex_success = self.generate_main_tex()
        
        # 执行最终的LaTeX语法验证
        self.logger.info("执行最终LaTeX语法验证")
        output_dir = Path(self.config.output_dir)
        validation_results = self.latex_validator.validate_directory(output_dir)
        self.logger.info(f"语法验证完成: 检查了{validation_results['validated']}个文件，修复了{validation_results['fixed']}个文件")
        
        # 编译PDF
        if main_tex_success:
            pdf_success = self.compile_latex()
        else:
            pdf_success = False
        
        # 最终结果
        overall_success = (
            preface_success and 
            len(successful_chapters) >= self.config.chapter_count * 0.8 and  # 至少80%章节成功
            main_tex_success and 
            pdf_success
        )
        
        if overall_success:
            self.logger.info("🎉 转换流程全部成功！")
        else:
            self.logger.error("❌ 转换流程存在问题")
        
        return overall_success

def main():
    """主函数"""
    print("智慧水利教材转换器 v1.0")
    print("="*50)
    
    # 创建转换器实例
    converter = ConverterApplication()
    
    # 执行转换
    success = converter.convert_all()
    
    if success:
        print("\n🎉🎉🎉 转换成功完成！🎉🎉🎉")
        print(f"输出目录: {converter.config.output_dir}")
        print("生成的文件:")
        print("  - main.tex (主LaTeX文件)")
        print("  - main.pdf (最终PDF)")
        print("  - chapters/*.tex (各章节LaTeX文件)")
    else:
        print("\n❌ 转换过程中出现问题")
        print("请检查日志文件 converter.log 获取详细信息")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())