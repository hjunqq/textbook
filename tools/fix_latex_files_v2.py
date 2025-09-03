#!/usr/bin/env python3
"""
智慧水利教材转换器 - LaTeX文件紧急修复工具 v2.0
专门用于修复已生成的tex文件中的各种语法错误

使用方法：
python fix_latex_files.py [输出目录路径]

如果不指定路径，将使用默认的 output/chapters/ 目录
"""

import os
import re
import sys
import logging
from pathlib import Path
from typing import List, Tuple

class LatexFileFixer:
    """LaTeX文件修复器 - 修复版"""
    
    def __init__(self):
        self.logger = self._setup_logger()
        self.fix_count = 0
    
    def _setup_logger(self):
        """设置日志"""
        logger = logging.getLogger('LatexFixer')
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        return logger
    
    def fix_directory(self, directory_path: str) -> bool:
        """修复目录下的所有tex文件"""
        dir_path = Path(directory_path)
        if not dir_path.exists():
            self.logger.error(f"目录不存在: {directory_path}")
            return False
        
        tex_files = list(dir_path.glob('*.tex'))
        if not tex_files:
            self.logger.warning(f"未找到tex文件: {directory_path}")
            return False
        
        self.logger.info(f"找到 {len(tex_files)} 个tex文件")
        
        success_count = 0
        for tex_file in tex_files:
            if self.fix_file(tex_file):
                success_count += 1
        
        self.logger.info(f"修复完成: {success_count}/{len(tex_files)} 个文件")
        self.logger.info(f"总共修复了 {self.fix_count} 个问题")
        
        return success_count == len(tex_files)
    
    def fix_file(self, file_path: Path) -> bool:
        """修复单个tex文件"""
        try:
            self.logger.info(f"修复文件: {file_path.name}")
            
            # 读取文件
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # 备份原文件
            backup_path = file_path.with_suffix('.tex.backup')
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_content)
            
            # 应用修复
            fixed_content = self.apply_all_fixes(original_content, file_path.name)
            
            # 写回修复后的内容
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            
            self.logger.info(f"  ✅ 修复完成，备份保存为: {backup_path.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"  ❌ 修复失败: {e}")
            return False
    
    def apply_all_fixes(self, content: str, filename: str) -> str:
        """应用所有修复规则"""
        file_fix_count = 0
        
        # 1. 修复过度转义的LaTeX命令 - 简化版本
        content, count1 = self._fix_over_escaped_commands_simple(content)
        file_fix_count += count1
        
        # 2. 修复tcolorbox语法错误 - 简化版本
        content, count2 = self._fix_tcolorbox_syntax_simple(content)
        file_fix_count += count2
        
        # 3. 修复章节标题格式
        content, count3 = self._fix_section_headers_simple(content)
        file_fix_count += count3
        
        # 4. 修复markdown残留 - 简化版本
        content, count4 = self._fix_markdown_residue_simple(content)
        file_fix_count += count4
        
        # 5. 清理和优化格式
        content, count5 = self._clean_and_optimize_simple(content)
        file_fix_count += count5
        
        self.fix_count += file_fix_count
        self.logger.info(f"  修复了 {file_fix_count} 个问题")
        
        return content
    
    def _fix_over_escaped_commands_simple(self, content: str) -> Tuple[str, int]:
        """修复过度转义的LaTeX命令 - 简化版本"""
        total_fixes = 0
        
        # 使用简单的字符串替换而不是复杂的正则表达式
        fixes = [
            ('\\textbackslash section{', '\\section{'),
            ('\\textbackslash chapter{', '\\chapter{'),
            ('\\textbackslash subsection{', '\\subsection{'),
            ('\\textbackslash begin{', '\\begin{'),
            ('\\textbackslash end{', '\\end{'),
        ]
        
        for old, new in fixes:
            count = content.count(old)
            content = content.replace(old, new)
            total_fixes += count
        
        return content, total_fixes
    
    def _fix_tcolorbox_syntax_simple(self, content: str) -> Tuple[str, int]:
        """修复tcolorbox语法错误 - 简化版本"""
        total_fixes = 0
        
        # 修复常见的tcolorbox语法问题
        lines = content.split('\\n')
        fixed_lines = []
        
        for line in lines:
            original_line = line
            
            # 修复 {[} ... {]} 语法错误
            if '\\begin{tcolorbox}{[' in line and '{]}' in line:
                # 简单替换 {[} 为 [, {]} 为 ]
                line = line.replace('{[', '[').replace('{]}', ']')
                if line != original_line:
                    total_fixes += 1
            
            # 修复title中的特殊字符问题
            if 'title=' in line:
                # 简单清理
                import re
                try:
                    line = re.sub(r'title=([^,\\]]*?)([,\\]])', r'title=\\1\\2', line)
                except:
                    pass  # 如果正则失败，保持原样
            
            fixed_lines.append(line)
        
        return '\\n'.join(fixed_lines), total_fixes
    
    def _fix_section_headers_simple(self, content: str) -> Tuple[str, int]:
        """修复章节标题格式 - 简化版本"""
        total_fixes = 0
        
        # 确保章节命令后有换行
        section_commands = ['\\chapter{', '\\section{', '\\subsection{']
        
        for cmd in section_commands:
            lines = content.split('\\n')
            fixed_lines = []
            i = 0
            
            while i < len(lines):
                line = lines[i]
                if cmd in line and line.strip().endswith('}'):
                    # 这是一个完整的章节命令行
                    fixed_lines.append(line)
                    # 检查下一行是否为空行，如果不是则添加
                    if i + 1 < len(lines) and lines[i + 1].strip():
                        fixed_lines.append('')  # 添加空行
                        total_fixes += 1
                else:
                    fixed_lines.append(line)
                i += 1
            
            content = '\\n'.join(fixed_lines)
        
        return content, total_fixes
    
    def _fix_markdown_residue_simple(self, content: str) -> Tuple[str, int]:
        """修复markdown残留语法 - 简化版本"""
        total_fixes = 0
        
        # 简单的字符串替换
        fixes = [
            ('\\#\\#\\#', '###'),
            ('\\*\\*', '**'),
            ("''", '``'),
            ('=== ``', '=== '),
            ('``', '"'),  # 转换回双引号
        ]
        
        for old, new in fixes:
            count = content.count(old)
            content = content.replace(old, new)
            total_fixes += count
        
        return content, total_fixes
    
    def _clean_and_optimize_simple(self, content: str) -> Tuple[str, int]:
        """清理和优化格式 - 简化版本"""
        original_lines = len(content.split('\\n'))
        
        # 清理多余的空行
        lines = content.split('\\n')
        cleaned_lines = []
        prev_empty = False
        
        for line in lines:
            is_empty = not line.strip()
            
            if is_empty and prev_empty:
                continue  # 跳过连续的空行
            
            cleaned_lines.append(line)
            prev_empty = is_empty
        
        content = '\\n'.join(cleaned_lines)
        optimization_count = max(0, original_lines - len(cleaned_lines))
        
        return content, optimization_count

def main():
    """主函数"""
    print("智慧水利教材转换器 - LaTeX文件紧急修复工具 v2.0")
    print("=" * 60)
    
    # 获取目录路径
    if len(sys.argv) > 1:
        directory_path = sys.argv[1]
    else:
        directory_path = "output/chapters"
    
    print(f"目标目录: {directory_path}")
    print()
    
    # 创建修复器并执行修复
    fixer = LatexFileFixer()
    success = fixer.fix_directory(directory_path)
    
    print()
    if success:
        print("🎉 所有文件修复成功！")
        print("注意：原文件已备份为 *.tex.backup")
        print()
        print("主要修复内容：")
        print("1. 过度转义的LaTeX命令 (\\textbackslash section -> \\section)")
        print("2. tcolorbox语法错误")
        print("3. 章节标题格式")
        print("4. markdown语法残留")
        print("5. 多余的空行")
    else:
        print("❌ 修复过程中出现问题")
        print("请检查错误信息并手动处理问题文件")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())