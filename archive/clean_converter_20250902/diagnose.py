#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
环境诊断和修复脚本
"""

import subprocess
import sys
import os
from pathlib import Path

def diagnose_environment():
    """诊断转换环境"""
    print("🔍 智慧水利教材转换器 - 环境诊断")
    print("=" * 50)
    
    issues = []
    warnings = []
    
    # 1. 检查Python
    print("🐍 Python环境检查:")
    python_version = sys.version
    print(f"  版本: {python_version.split()[0]}")
    if sys.version_info >= (3, 7):
        print("  ✅ Python版本符合要求 (≥3.7)")
    else:
        issues.append("Python版本过低，需要3.7+")
        print("  ❌ Python版本过低，需要3.7+")
    
    # 2. 检查Pandoc
    print(f"\n📖 Pandoc检查:")
    try:
        result = subprocess.run(['pandoc', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"  ✅ 已安装: {version_line}")
        else:
            issues.append("Pandoc安装异常")
            print("  ❌ Pandoc安装异常")
    except FileNotFoundError:
        issues.append("Pandoc未安装")
        print("  ❌ Pandoc未安装")
        print("  💡 请访问 https://pandoc.org/installing.html 下载安装")
        
        # 提供具体的安装指导
        if os.name == 'nt':  # Windows
            print("  💡 Windows用户:")
            print("     1. 下载 pandoc-*-windows-x86_64.msi")
            print("     2. 双击安装")
            print("     3. 重启命令提示符")
        else:  # Linux/macOS
            print("  💡 Linux用户: sudo apt-get install pandoc")
            print("  💡 macOS用户: brew install pandoc")
    
    # 3. 检查XeLaTeX
    print(f"\n📝 XeLaTeX检查 (用于PDF生成):")
    try:
        result = subprocess.run(['xelatex', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"  ✅ 已安装: {version_line}")
        else:
            warnings.append("XeLaTeX安装异常")
            print("  ⚠️  XeLaTeX安装异常")
    except FileNotFoundError:
        warnings.append("XeLaTeX未安装")
        print("  ⚠️  XeLaTeX未安装 (无法生成PDF)")
        print("  💡 请安装TeX Live或MiKTeX")
        if os.name == 'nt':
            print("  💡 Windows: 下载MiKTeX (https://miktex.org/)")
        else:
            print("  💡 Linux: sudo apt-get install texlive-xetex")
            print("  💡 macOS: brew install --cask mactex")
    
    # 4. 检查工作目录
    print(f"\n📁 工作目录检查:")
    current_dir = Path.cwd()
    print(f"  当前目录: {current_dir}")
    
    expected_files = ['core/', 'templates/', 'convert.py']
    missing_files = []
    for file in expected_files:
        if not (current_dir / file).exists():
            missing_files.append(file)
    
    if not missing_files:
        print("  ✅ 转换器文件完整")
    else:
        issues.append(f"转换器文件缺失: {', '.join(missing_files)}")
        print(f"  ❌ 缺失文件: {', '.join(missing_files)}")
    
    # 5. 检查源文件
    print(f"\n📚 源文件检查:")
    source_indicators = [
        "../../docs/chapters/",
        "../../docs/前言.md",
        "../../../docs/chapters/"
    ]
    
    source_found = False
    for indicator in source_indicators:
        if Path(indicator).exists():
            source_found = True
            print(f"  ✅ 找到源文件目录: {Path(indicator).resolve()}")
            break
    
    if not source_found:
        warnings.append("未找到教材源文件")
        print("  ⚠️  未找到教材源文件目录")
        print("  💡 请确认在正确的目录中运行转换器")
    
    # 输出汇总
    print(f"\n📋 诊断汇总:")
    if issues:
        print(f"❌ 发现 {len(issues)} 个严重问题:")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
    
    if warnings:
        print(f"⚠️  发现 {len(warnings)} 个警告:")
        for i, warning in enumerate(warnings, 1):
            print(f"   {i}. {warning}")
    
    if not issues and not warnings:
        print("✅ 所有检查通过！")
        return True
    elif not issues:
        print("✅ 基本环境正常，可以进行转换")
        print("💡 警告不影响基本功能，建议修复以获得完整功能")
        return True
    else:
        print("❌ 请先解决严重问题后再进行转换")
        return False

def provide_solutions():
    """提供解决方案"""
    print(f"\n🛠️  快速解决方案:")
    print("1. 安装Pandoc (必需):")
    print("   - Windows: https://pandoc.org/installing.html")
    print("   - Linux: sudo apt-get install pandoc")  
    print("   - macOS: brew install pandoc")
    
    print(f"\n2. 安装LaTeX (PDF生成):")
    print("   - Windows: MiKTeX (https://miktex.org/)")
    print("   - Linux: sudo apt-get install texlive-xetex")
    print("   - macOS: MacTeX (https://www.tug.org/mactex/)")
    
    print(f"\n3. 验证安装:")
    print("   - 重启命令提示符")
    print("   - 运行: pandoc --version")
    print("   - 运行: xelatex --version")
    
    print(f"\n4. 开始转换:")
    print("   - python convert.py -f latex  (生成LaTeX)")
    print("   - python convert.py -f pdf    (生成PDF，需要XeLaTeX)")

if __name__ == '__main__':
    success = diagnose_environment()
    if not success:
        provide_solutions()
    else:
        print(f"\n🚀 环境正常！可以开始转换:")
        print("   python convert.py --help  # 查看帮助")
        print("   python quick_test.py      # 快速测试")