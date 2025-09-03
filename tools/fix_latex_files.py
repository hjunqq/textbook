#!/usr/bin/env python3
"""
智慧水利教材转换器 - LaTeX文件紧急修复工具
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
    """LaTeX文件修复器"""
    
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
        
        # 1. 修复过度转义的LaTeX命令
        content, count1 = self._fix_over_escaped_commands(content)
        file_fix_count += count1
        
        # 2. 修复tcolorbox语法错误
        content, count2 = self._fix_tcolorbox_syntax(content)
        file_fix_count += count2
        
        # 3. 修复章节标题格式
        content, count3 = self._fix_section_headers(content)
        file_fix_count += count3
        
        # 4. 修复markdown残留
        content, count4 = self._fix_markdown_residue(content)
        file_fix_count += count4
        
        # 5. 修复特殊字符和格式
        content, count5 = self._fix_special_characters(content)
        file_fix_count += count5
        
        # 6. 清理和优化格式
        content, count6 = self._clean_and_optimize(content)
        file_fix_count += count6
        
        self.fix_count += file_fix_count
        self.logger.info(f"  修复了 {file_fix_count} 个问题")
        
        return content
    
    def _fix_over_escaped_commands(self, content: str) -> Tuple[str, int]:
        """修复过度转义的LaTeX命令"""
        fixes = [
            # 修复过度转义的章节命令
            (r'\\textbackslash section\\{([^}]+)\\}', r'\\section{\1}'),
            (r'\\textbackslash chapter\\{([^}]+)\\}', r'\\chapter{\1}'),
            (r'\\textbackslash subsection\\{([^}]+)\\}', r'\\subsection{\1}'),
            (r'\\textbackslash subsubsection\\{([^}]+)\\}', r'\\subsubsection{\1}'),
            
            # 修复过度转义的环境命令
            (r'\\textbackslash begin\\{([^}]+)\\}', r'\\begin{\1}'),
            (r'\\textbackslash end\\{([^}]+)\\}', r'\\end{\1}'),
            
            # 修复其他常见命令
            (r'\\textbackslash ([a-zA-Z]+)\\{', r'\\\1{'),
        ]
        
        total_fixes = 0
        for pattern, replacement in fixes:
            matches = re.findall(pattern, content)
            content = re.sub(pattern, replacement, content)
            total_fixes += len(matches)
        
        return content, total_fixes
    
    def _fix_tcolorbox_syntax(self, content: str) -> Tuple[str, int]:
        """修复tcolorbox语法错误"""
        fixes = [
            # 修复错误的选项语法 {[}...{]}
            (r'\\begin\\{tcolorbox\\}\\{\\[\\]([^}]+?)\\{\\]\\}', r'\\begin{tcolorbox}[\1]'),
            
            # 修复缺失的闭合括号
            (r'\\begin\\{tcolorbox\\}\\[([^\\]]+?)\\]([^\\]+?)\\end\\{tcolorbox\\}', 
             r'\\begin{tcolorbox}[\1]\n\2\n\\end{tcolorbox}'),
            
            # 修复标题中的特殊字符
            (r'title=([^,\\]]+?)([,\\]])', self._clean_tcolorbox_title_match),
        ]
        
        total_fixes = 0
        for pattern, replacement in fixes:
            if callable(replacement):
                # 对于函数替换，需要特殊处理
                matches = list(re.finditer(pattern, content))
                for match in reversed(matches):  # 从后往前替换避免位置变化
                    new_text = replacement(match)
                    content = content[:match.start()] + new_text + content[match.end():]
                total_fixes += len(matches)
            else:
                matches = re.findall(pattern, content)
                content = re.sub(pattern, replacement, content)
                total_fixes += len(matches)
        
        return content, total_fixes
    
    def _clean_tcolorbox_title_match(self, match):
        """清理tcolorbox标题中的特殊字符"""
        title_part = match.group(1)
        ending = match.group(2)
        
        # 移除可能导致问题的字符
        clean_title = re.sub(r'[{}\\[\\]]', '', title_part)
        clean_title = clean_title.strip()
        
        return f'title={clean_title}{ending}'
    
    def _fix_section_headers(self, content: str) -> Tuple[str, int]:
        """修复章节标题格式"""
        fixes = [
            # 确保章节命令后有适当的换行
            (r'\\chapter\\{([^}]+)\\}\\s*(?!\\n\\n)', r'\\chapter{\1}\n\n'),
            (r'\\section\\{([^}]+)\\}\\s*(?!\\n\\n)', r'\\section{\1}\n\n'),
            (r'\\subsection\\{([^}]+)\\}\\s*(?!\\n\\n)', r'\\subsection{\1}\n\n'),
        ]
        
        total_fixes = 0
        for pattern, replacement in fixes:
            matches = re.findall(pattern, content)
            content = re.sub(pattern, replacement, content)
            total_fixes += len(matches)
        
        return content, total_fixes
    
    def _fix_markdown_residue(self, content: str) -> Tuple[str, int]:
        """修复markdown残留语法"""
        fixes = [
            # 修复markdown标题残留
            (r'\\#\\#\\#\\s*([^\\n]+)', r'\\subsection{\1}'),
            (r'\\#\\#\\s*([^\\n]+)', r'\\section{\1}'),
            (r'\\#\\s*([^\\n]+)', r'\\chapter{\1}'),
            
            # 修复markdown加粗语法
            (r'\\*\\*([^*]+?)\\*\\*', r'\\textbf{\1}'),
            
            # 修复特殊的分隔符
            (r'=== ``([^`]+?)``', r'\\subsection{\1}'),
            (r'=== ([^\\n]+)', r'\\subsection{\1}'),
            
            # 修复引号问题
            (r"''", r'``'),  # 英文引号
        ]
        
        total_fixes = 0
        for pattern, replacement in fixes:
            matches = re.findall(pattern, content)
            content = re.sub(pattern, replacement, content)
            total_fixes += len(matches)
        
        return content, total_fixes
    
    def _fix_special_characters(self, content: str) -> Tuple[str, int]:
        """修复特殊字符和转义问题"""
        fixes = [
            # 修复百分号转义
            (r'([^\\\\])%', r'\1\\%'),
            
            # 修复与号转义
            (r'([^\\\\])&', r'\1\\&'),
            
            # 修复井号转义
            (r'([^\\\\])#', r'\1\\#'),
            
            # 修复下划线转义
            (r'([^\\\\])_', r'\1\\_'),
            
            # 修复反斜杠问题（但不影响LaTeX命令）
            (r'(?<!\\\\)\\\\(?![a-zA-Z{}])', r'\\textbackslash'),
        ]
        
        total_fixes = 0
        for pattern, replacement in fixes:
            matches = re.findall(pattern, content)
            content = re.sub(pattern, replacement, content)
            total_fixes += len(matches)
        
        return content, total_fixes
    
    def _clean_and_optimize(self, content: str) -> Tuple[str, int]:
        """清理和优化格式"""
        original_length = len(content)
        
        # 清理多余的空行
        content = re.sub(r'\\n\\s*\\n\\s*\\n+', '\\n\\n', content)
        
        # 确保环境前后有适当间距
        content = re.sub(r'\\n(\\\\begin\\{[^}]+\\})', r'\\n\\n\1', content)
        content = re.sub(r'(\\\\end\\{[^}]+\\})\\n', r'\1\\n\\n', content)
        
        # 清理行尾空白
        content = re.sub(r'[ \\t]+$', '', content, flags=re.MULTILINE)
        
        # 计算优化次数（简单估算）
        optimization_count = max(0, original_length - len(content)) // 10
        
        return content, optimization_count

def main():
    """主函数"""
    print("智慧水利教材转换器 - LaTeX文件紧急修复工具")
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
    else:
        print("❌ 修复过程中出现问题")
        print("请检查错误信息并手动处理问题文件")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())