# -*- coding: utf-8 -*-
"""
简化的中文支持章节转换器
修复中文字体显示问题，支持多文件章节
"""

import os
import sys
import re
import logging
import subprocess
from pathlib import Path
from latex_config import (
    CHAPTER_MAPPING, 
    LATEX_TEMPLATE, 
    ADMONITION_PATTERNS,
    PANDOC_ARGS
)

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleChapterConverter:
    """简化的章节转换器，专注解决中文显示问题"""
    
    def __init__(self, source_dir: str = None, output_dir: str = None):
        """初始化转换器"""
        self.source_dir = Path(source_dir) if source_dir else Path(__file__).parent.parent.parent / 'docs'
        self.output_dir = Path(output_dir) if output_dir else Path(__file__).parent / '逐章节输出'
        
        # 从配置文件获取章节映射
        self.chapter_mapping = CHAPTER_MAPPING
        
        logger.info(f"初始化完成 - 源目录: {self.source_dir}, 输出目录: {self.output_dir}")
    
    def get_latex_template(self) -> str:
        """获取LaTeX模板"""
        return LATEX_TEMPLATE
    
    def clean_content(self, content: str) -> str:
        """清理内容"""
        # 移除HTML注释
        content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
        
        # 转换特殊块
        content = self.convert_admonitions(content)
        
        # 转换**加粗**为中文黑体
        content = re.sub(r'\*\*(.*?)\*\*', r'\\textbf{\1}', content)
        
        # 修复列表项换行问题 - 在数字列表项后添加换行
        content = re.sub(r'(\d+\.\s+\\textbf\{[^}]+\}：[^\n]+)', r'\1\n', content)
        
        # 移除多余空行
        content = re.sub(r'\n\n\n+', r'\n\n', content)
        
        return content.strip()
    
    def convert_admonitions(self, content: str) -> str:
        """转换特殊块语法"""
        for adm_type, config in ADMONITION_PATTERNS.items():
            pattern = config['pattern']
            color = config['color'] 
            title_default = config['title_default']
            
            def replacement_func(match):
                title = match.group(1) if match.group(1) else title_default
                body = match.group(2)
                
                # 处理嵌套的=== "标题"语法，转换为子标题并添加前后换行
                body = re.sub(r'^\s*=== "([^"]*)"', r'\n\n\\textbf{\1}\n\n', body, flags=re.MULTILINE)
                
                # 移除缩进（通常是4个空格）
                body = re.sub(r'^    ', '', body, flags=re.MULTILINE)
                
                # 确保段落之间有适当的空行，但避免开头有多余空行
                body = re.sub(r'\n\n\n+', r'\n\n', body)
                body = body.strip()
                
                return f'''\\begin{{tcolorbox}}[colback={color}!5!white,colframe={color}!75!black,title={title}]
{body}
\\end{{tcolorbox}}

'''
            
            content = re.sub(pattern, replacement_func, content)
        
        return content
    
    def convert_chapter(self, chapter_key: str) -> bool:
        """转换单个章节，支持多文件"""
        if chapter_key not in self.chapter_mapping:
            logger.error(f"未知章节: {chapter_key}")
            return False
        
        chapter_info = self.chapter_mapping[chapter_key]
        logger.info(f"开始转换章节: {chapter_info['title']}")
        
        # 创建输出目录
        chapter_output_dir = self.output_dir / chapter_key
        chapter_output_dir.mkdir(parents=True, exist_ok=True)
        
        # 合并多个文件内容
        combined_content = ""
        
        # 检查是否有多个文件
        if 'files' in chapter_info:
            # 多文件章节
            for file_path in chapter_info['files']:
                source_file = self.source_dir / file_path
                if not source_file.exists():
                    logger.error(f"源文件不存在: {source_file}")
                    return False
                
                logger.info(f"处理文件: {file_path}")
                file_content = source_file.read_text(encoding='utf-8')
                
                # 清理单个文件内容
                file_content = self.clean_content(file_content)
                
                # 添加到合并内容中
                if combined_content:
                    combined_content += "\n\n"
                combined_content += file_content
        else:
            # 单文件章节
            source_file = self.source_dir / chapter_info['file']
            if not source_file.exists():
                logger.error(f"源文件不存在: {source_file}")
                return False
            
            logger.info(f"处理主文件: {chapter_info['file']}")
            combined_content = source_file.read_text(encoding='utf-8')
            combined_content = self.clean_content(combined_content)
        
        # 保存合并后的Markdown
        md_file = chapter_output_dir / f"{chapter_key}.md"
        md_file.write_text(combined_content, encoding='utf-8')
        logger.info(f"保存合并的Markdown文件: {md_file}")
        
        # 转换为LaTeX
        tex_file = chapter_output_dir / f"{chapter_key}.tex"
        if not self.convert_to_latex(md_file, tex_file):
            return False
        
        # 生成PDF
        pdf_file = chapter_output_dir / f"{chapter_key}.pdf"
        if not self.compile_latex(tex_file, pdf_file):
            return False
        
        logger.info(f"章节 {chapter_info['title']} 转换成功: {pdf_file}")
        return True
    
    def convert_to_latex(self, md_file: Path, tex_file: Path) -> bool:
        """使用Pandoc转换为LaTeX"""
        try:
            logger.info("开始Pandoc转换...")
            
            cmd = [
                'pandoc',
                str(md_file),
                '--from=markdown',
                '--to=latex',
                '--output=' + str(tex_file),
                '--listings',
                '--number-sections'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
            
            if result.returncode != 0:
                logger.error(f"Pandoc转换失败: {result.stderr}")
                return False
            
            logger.info("Pandoc转换成功")
            
            # 应用LaTeX模板
            self.apply_latex_template(tex_file)
            
            return True
            
        except Exception as e:
            logger.error(f"转换过程出错: {e}")
            return False
    
    def apply_latex_template(self, tex_file: Path):
        """应用LaTeX模板"""
        content = tex_file.read_text(encoding='utf-8')
        
        # 由于Pandoc输出的可能不是完整文档，直接用内容构建新文档
        template = self.get_latex_template()
        new_content = template + content.strip() + '\n\n\\end{document}'
        
        # 保存
        tex_file.write_text(new_content, encoding='utf-8')
        logger.info("已应用LaTeX模板")
    
    def compile_latex(self, tex_file: Path, pdf_file: Path) -> bool:
        """编译LaTeX为PDF"""
        try:
            os.chdir(tex_file.parent)
            
            logger.info("使用XeLaTeX编译...")
            
            # 第一次编译
            cmd = ['xelatex', '-interaction=nonstopmode', tex_file.name]
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
            
            if result.returncode != 0:
                logger.warning("第一次编译有警告")
            
            # 第二次编译（确保目录正确）
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
            
            if pdf_file.exists():
                logger.info(f"PDF编译成功: {pdf_file}")
                return True
            else:
                logger.error("PDF文件未生成")
                return False
                
        except Exception as e:
            logger.error(f"LaTeX编译出错: {e}")
            return False

def main():
    """主函数"""
    if len(sys.argv) != 2:
        print("用法: python simple_converter.py <chapter_key>")
        print("可用章节: preface, chapter01, chapter02, chapter03")
        sys.exit(1)
    
    chapter_key = sys.argv[1]
    converter = SimpleChapterConverter()
    
    if converter.convert_chapter(chapter_key):
        print(f"章节 {chapter_key} 转换完成")
    else:
        print(f"章节 {chapter_key} 转换失败")
        sys.exit(1)

if __name__ == '__main__':
    main()
