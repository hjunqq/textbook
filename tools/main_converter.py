"""
智慧水利教材转换器 - 主应用程序
软件工程设计：外观模式 + 命令模式
"""

import os
import sys
import logging
import subprocess
from pathlib import Path
from typing import Optional, List

from converter_config import ConverterConfig, PathManager, DEFAULT_CONFIG
from content_processors import ContentProcessor
from latex_templates import LaTeXTemplateGenerator, LaTeXPostProcessor

class ConverterApplication:
    """转换器主应用程序"""
    
    def __init__(self, config: Optional[ConverterConfig] = None):
        self.config = config or DEFAULT_CONFIG
        self.path_manager = PathManager(self.config)
        self.content_processor = ContentProcessor()
        self.template_generator = LaTeXTemplateGenerator(self.config)
        self.post_processor = LaTeXPostProcessor()
        
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
                '--standalone',
                '--from=markdown-yaml_metadata_block',  # 禁用YAML元数据块解析
                '--to=latex'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
            
            if result.returncode == 0:
                self.logger.debug(f"Pandoc转换成功: {input_path} -> {output_path}")
                return True
            else:
                self.logger.error(f"Pandoc转换失败: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Pandoc转换出错: {e}")
            return False
    
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
    
    def convert_all(self) -> bool:
        """转换所有内容"""
        self.logger.info("🚀 开始完整转换流程")
        
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