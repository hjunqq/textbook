#!/usr/bin/env python3
"""
代码清理脚本 - 删除重复和过时的文件
"""

import os
import shutil
from pathlib import Path

def clean_tools_directory():
    """清理tools目录中的重复文件"""
    
    tools_dir = Path(".")
    
    # 要删除的文件列表 (重复、过时、测试文件)
    files_to_remove = [
        # Fixed版本文件
        "content_processors_fixed.py",
        "latex_templates_fixed.py", 
        "main_converter_fixed.py",
        "fix_latex_files_v2.py",
        
        # 中文转换器 (功能重复)
        "智能转换器.py",
        "简化转换器.py",
        
        # 重复的改进版本
        "improved_main_converter.py",
        
        # 临时和调试文件
        "debug_converter.py",
        "simple_fix.py",
        "fix_all_chapters.py",
        "simple_enhancer.py",
        
        # 临时输出文件
        "temp.pdf",
        "texput.log",
        
        # 重复的README文件
        "README_智能转换器.md",
        
        # 批处理文件 (保留主要的)
        "智能转换.bat"
    ]
    
    # 要删除的目录
    dirs_to_remove = [
        "temp",
        "__pycache__"
    ]
    
    # 要清理的输出文件（保留核心输出）
    output_files_to_remove = [
        "CONSERVATIVE.md",
        "FINAL_COMPLETE.md", 
        "TRULY_COMPLETE.md",
        "corrected_textbook.md",
        "debug_merged.md",
        "final_fixed_textbook.md",
        "final_textbook.md",
        "simple_textbook.md",
        "转换报告.md",
        "smart-config.yaml"
    ]
    
    print("开始清理tools目录...")
    
    # 删除重复文件
    for filename in files_to_remove:
        file_path = tools_dir / filename
        if file_path.exists():
            print(f"删除文件: {filename}")
            file_path.unlink()
    
    # 删除目录
    for dirname in dirs_to_remove:
        dir_path = tools_dir / dirname
        if dir_path.exists() and dir_path.is_dir():
            print(f"删除目录: {dirname}")
            shutil.rmtree(dir_path)
    
    # 清理输出目录中的临时文件
    output_dir = tools_dir / "output"
    if output_dir.exists():
        for filename in output_files_to_remove:
            file_path = output_dir / filename
            if file_path.exists():
                print(f"删除输出文件: output/{filename}")
                file_path.unlink()
    
    print("清理完成！")
    
    # 显示剩余的核心文件
    print("\n保留的核心文件:")
    core_files = [
        "main_converter.py",
        "converter_config.py", 
        "content_processors.py",
        "latex_templates.py",
        "latex_validator.py",
        "test_framework.py",
        "quick_test.py",
        "requirements.txt",
        "build_converter.bat"
    ]
    
    for filename in core_files:
        file_path = tools_dir / filename
        if file_path.exists():
            print(f"✓ {filename}")
        else:
            print(f"✗ {filename} (不存在)")

if __name__ == "__main__":
    clean_tools_directory()