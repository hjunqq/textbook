#!/usr/bin/env python3
"""
智慧水利教材简化转换器
专为Windows uv环境优化

特点：
- 无外部依赖
- 适配Windows编码
- 简化配置管理
- 健壮错误处理

作者：GitHub Copilot
创建时间：2025年9月3日
"""

import os
import re
from pathlib import Path
from typing import List, Optional, Tuple
import subprocess
import sys

class SimpleTextbookConverter:
    """简化教材转换器"""
    
    def __init__(self, base_dir: str = "."):
        """初始化转换器"""
        self.base_dir = Path(base_dir)
        self.tools_dir = Path(".")
        self.output_dir = Path("output")
        self.docs_dir = self.base_dir / "docs"
        self.chapters_dir = self.docs_dir / "chapters"
        
        # 创建输出目录
        self.output_dir.mkdir(exist_ok=True)
        
        # 转换统计
        self.stats = {
            'chapters_found': 0,
            'sections_found': 0,
            'problems_fixed': 0,
            'warnings': 0,
        }
        
        print("🚀 简化教材转换器启动")
        print(f"📁 工作目录: {Path.cwd()}")
        print(f"📂 文档目录: {self.docs_dir.absolute()}")
        print(f"📂 章节目录: {self.chapters_dir.absolute()}")
    
    def log(self, message: str, level: str = "INFO"):
        """简化日志"""
        icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌"}
        print(f"{icons.get(level, 'ℹ️')} {message}")
        
        if level == "WARNING":
            self.stats['warnings'] += 1
    
    def safe_read_file(self, file_path: Path) -> Optional[str]:
        """安全读取文件，处理编码问题"""
        if not file_path.exists():
            self.log(f"文件不存在: {file_path.name}", "WARNING")
            return None
        
        # 尝试多种编码
        encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                return content
            except UnicodeDecodeError:
                continue
            except Exception as e:
                self.log(f"读取失败 {file_path.name}: {e}", "ERROR")
                return None
        
        self.log(f"无法解码文件: {file_path.name}", "ERROR")
        return None
    
    def collect_content(self) -> str:
        """收集内容"""
        print("\n📚 收集内容...")
        all_content = []
        
        # 1. 前言
        preface = self.docs_dir / "前言.md"
        if preface.exists():
            content = self.safe_read_file(preface)
            if content:
                all_content.append(content)
                print("  ✅ 前言")
        
        # 2. 章节内容
        chapters = ['chapter01', 'chapter02', 'chapter03', 'chapter04', 'chapter05',
                   'chapter06', 'chapter07', 'chapter08', 'chapter09']
        
        for chapter in chapters:
            chapter_dir = self.chapters_dir / chapter
            if not chapter_dir.exists():
                continue
                
            print(f"  📖 {chapter}")
            
            # 主章节文件
            main_file = chapter_dir / f"{chapter}.md"
            if main_file.exists():
                content = self.safe_read_file(main_file)
                if content:
                    all_content.append(content)
                    self.stats['chapters_found'] += 1
            
            # section文件
            section_files = sorted(chapter_dir.glob("section*.md"))
            for section_file in section_files:
                content = self.safe_read_file(section_file)
                if content:
                    all_content.append(content)
                    self.stats['sections_found'] += 1
        
        result = '\n\n'.join(all_content)
        print(f"✅ 收集完成: {len(result):,} 字符")
        
        return result
    
    def clean_content(self, content: str) -> str:
        """清理内容"""
        print("\n🧹 清理内容...")
        original_len = len(content)
        
        # 修复章节结构
        print("  🔧 修复章节结构")
        # 先降级所有标题
        for level in range(6, 0, -1):
            old = '#' * level + ' '
            new = '#' * (level + 1) + ' '
            content = re.sub(f'^{re.escape(old)}', new, content, flags=re.MULTILINE)
        
        # 恢复主章节
        main_patterns = [
            (r'^## 前言$', '# 前言'),
            (r'^## 第[一二三四五六七八九十]章', lambda m: '#' + m.group(0)[1:]),
            (r'^## Chapter \d+', lambda m: '#' + m.group(0)[1:]),
        ]
        
        for pattern, replacement in main_patterns:
            if callable(replacement):
                content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
            else:
                content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        
        # 清理特殊字符
        print("  🧽 清理特殊字符")
        
        # 更彻底的数学公式清理
        print("    🧮 清理数学公式...")
        # 统计原始数学公式
        inline_math = len(re.findall(r'\$[^$]+\$', content))
        block_math = len(re.findall(r'\$\$[^$]+\$\$', content))
        
        # 移除所有数学公式标记
        content = re.sub(r'\$\$[^$]*\$\$', '[公式块]', content)
        content = re.sub(r'\$[^$]*\$', '[公式]', content)
        
        # 清理残留的LaTeX命令
        latex_commands = [
            r'\\frac\{[^}]*\}\{[^}]*\}',
            r'\\sqrt\{[^}]*\}',
            r'\\[a-zA-Z]+\{[^}]*\}',
            r'\\[a-zA-Z]+',
            r'\{[^}]*\}',  # 清理孤立的大括号
        ]
        
        for cmd in latex_commands:
            matches = len(re.findall(cmd, content))
            if matches > 0:
                content = re.sub(cmd, '[数学符号]', content)
                print(f"      清理 {cmd}: {matches} 个")
        
        math_count = inline_math + block_math
        
        # emoji和特殊符号
        emoji_pattern = r'[📱🔍📑💡🧮📊🌓📖🟢🔴🚨⚠️ℹ️🐛📝❌✅✓✗○□📚💻🎥💬🐍🔧📦🎨🗄📋]'
        emoji_count = len(re.findall(emoji_pattern, content))
        content = re.sub(emoji_pattern, '', content)
        
        # ASCII艺术
        content = re.sub(r'[├─│└┌┐┘┴┬┤]', '', content)
        
        # 图片处理
        img_count = len(re.findall(r'!\[[^\]]*\]\([^)]+\)', content))
        content = re.sub(r'!\[([^\]]*)\]\([^)]+\)', r'[图片: \1]', content)
        
        # admonition
        content = re.sub(r'!!! (\w+)', r'**\1**', content)
        
        self.stats['problems_fixed'] = math_count + emoji_count + img_count
        
        print(f"  📊 数学公式: {math_count}")
        print(f"  📊 特殊符号: {emoji_count}")
        print(f"  📊 图片: {img_count}")
        print(f"  📏 大小变化: {original_len:,} → {len(content):,}")
        
        return content
    
    def create_simple_config(self) -> Path:
        """创建简单配置"""
        config_file = self.output_dir / "simple-config.yaml"
        
        config_content = """from: markdown
to: pdf
pdf-engine: xelatex
metadata:
  title: "智慧水利平台架构与开发"
  author: "智慧水利教材编写组"
  lang: zh-CN
variables:
  documentclass: book
  fontsize: 12pt
  CJKmainfont: "Microsoft YaHei"
  mainfont: "Times New Roman"
  geometry: margin=2.5cm
  colorlinks: true
  linkcolor: blue
table-of-contents: true
toc-depth: 3
number-sections: true
"""
        
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        return config_file
    
    def convert_to_pdf(self, md_file: Path) -> bool:
        """转换为PDF"""
        print("\n📄 转换PDF...")
        
        config_file = self.create_simple_config()
        pdf_file = self.output_dir / "智慧水利教材_简化版.pdf"
        
        # 构建命令
        cmd = ['pandoc', str(md_file), '--defaults', str(config_file), '-o', str(pdf_file)]
        
        print(f"🔧 执行命令: {' '.join(cmd)}")
        
        try:
            # Windows环境设置
            startupinfo = None
            if sys.platform.startswith('win'):
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            # 设置环境变量
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',  # 忽略编码错误
                cwd=self.tools_dir,
                env=env,
                startupinfo=startupinfo,
                timeout=300  # 5分钟超时
            )
            
            if result.returncode == 0:
                if pdf_file.exists():
                    size = pdf_file.stat().st_size
                    print(f"✅ PDF生成成功!")
                    print(f"📁 文件位置: {pdf_file}")
                    print(f"📏 文件大小: {size:,} 字节")
                    return True
                else:
                    print("❌ PDF文件未生成")
                    return False
            else:
                print("❌ 转换失败")
                if result.stdout:
                    print(f"输出: {result.stdout}")
                if result.stderr:
                    print(f"错误: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ 转换超时")
            return False
        except Exception as e:
            print(f"❌ 转换异常: {e}")
            return False
    
    def run(self) -> bool:
        """运行转换"""
        print("="*50)
        print("🚀 开始简化转换流程")
        print("="*50)
        
        try:
            # 1. 收集内容
            content = self.collect_content()
            if not content.strip():
                print("❌ 没有收集到内容")
                return False
            
            # 2. 清理内容
            content = self.clean_content(content)
            
            # 3. 保存Markdown
            md_file = self.output_dir / "智慧水利教材_简化版.md"
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Markdown保存: {md_file}")
            
            # 4. 转换PDF
            success = self.convert_to_pdf(md_file)
            
            # 5. 显示统计
            print("\n📊 转换统计:")
            print(f"  章节: {self.stats['chapters_found']}")
            print(f"  小节: {self.stats['sections_found']}")  
            print(f"  修复: {self.stats['problems_fixed']}")
            print(f"  警告: {self.stats['warnings']}")
            
            return success
            
        except Exception as e:
            print(f"❌ 转换异常: {e}")
            return False

def main():
    """主函数"""
    print("📚 智慧水利教材简化转换器")
    print("🖥️  专为Windows uv环境优化")
    print()
    
    converter = SimpleTextbookConverter()
    success = converter.run()
    
    print("\n" + "="*50)
    if success:
        print("🎉 转换成功完成!")
        print("📂 请查看 output 目录中的结果文件")
    else:
        print("❌ 转换失败")
        print("💡 请检查:")
        print("   - Pandoc是否已安装")
        print("   - XeLaTeX是否可用")
        print("   - 源文件是否存在")
    print("="*50)
    
    return success

if __name__ == "__main__":
    main()
