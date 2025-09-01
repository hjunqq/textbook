#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智慧水利教材转换器 - 主程序
一键转换Markdown教材为PDF或LaTeX
"""

import sys
import argparse
from pathlib import Path

# 添加核心模块路径
sys.path.insert(0, str(Path(__file__).parent / 'core'))

from core.config import config
from core.validator import validator
from core.converter import converter

def main():
    """主程序入口"""
    print("🌊 智慧水利教材转换器 v2.0")
    print("=" * 50)
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='智慧水利教材转换器')
    parser.add_argument('--format', '-f', choices=['pdf', 'latex'], 
                       default='pdf', help='输出格式 (默认: pdf)')
    parser.add_argument('--skip-validation', action='store_true',
                       help='跳过转换前验证')
    parser.add_argument('--output-dir', '-o', type=str,
                       help='输出目录 (可选)')
    
    args = parser.parse_args()
    
    # 设置输出目录
    if args.output_dir:
        custom_output = Path(args.output_dir)
        custom_output.mkdir(parents=True, exist_ok=True)
        config.output_dir = custom_output
        (config.output_dir / "images").mkdir(exist_ok=True)
        print(f"📁 输出目录: {config.output_dir}")
    
    try:
        # 1. 转换前质量检查
        if not args.skip_validation:
            print("\n🔍 第一步：转换前质量检查")
            validation_passed = validator.validate_before_conversion()
            
            if not validation_passed:
                print(f"\n❌ 质量检查发现 {validator.get_issues_count()} 个严重问题")
                print("请修复问题后重新运行，或使用 --skip-validation 跳过检查")
                return 1
            
            if validator.get_warnings_count() > 0:
                print(f"\n⚠️  发现 {validator.get_warnings_count()} 个警告，但可以继续转换")
                response = input("是否继续？(y/N): ").lower().strip()
                if response not in ['y', 'yes']:
                    print("转换已取消")
                    return 0
        else:
            print("⏭️  跳过转换前质量检查")
        
        # 2. 执行转换
        print(f"\n🔄 第二步：转换为 {args.format.upper()}")
        success = converter.convert_textbook(args.format)
        
        if not success:
            print("\n❌ 转换失败！")
            return 1
        
        # 3. 转换后验证
        print(f"\n✅ 第三步：转换后验证")
        validation_passed = validator.validate_after_conversion(args.format)
        
        if validation_passed:
            print("\n🎉 转换完成！")
            print(f"📁 输出目录: {config.output_dir}")
            
            # 显示生成的文件
            if args.format == 'pdf':
                output_file = config.get_output_path("textbook.pdf")
            else:
                output_file = config.get_output_path("textbook.tex")
            
            if output_file.exists():
                file_size = output_file.stat().st_size / 1024  # KB
                print(f"📄 生成文件: {output_file} ({file_size:.1f} KB)")
            
            return 0
        else:
            print("\n⚠️  转换完成但验证发现问题")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n⏹️  转换被用户中断")
        return 0
    except Exception as e:
        print(f"\n❌ 转换过程出现异常: {e}")
        import traceback
        traceback.print_exc()
        return 1

def show_help():
    """显示帮助信息"""
    help_text = """
🌊 智慧水利教材转换器使用指南

基本用法:
  python convert.py                    # 转换为PDF
  python convert.py -f latex          # 转换为LaTeX
  python convert.py -o /path/to/output # 指定输出目录

选项:
  -f, --format     输出格式 [pdf|latex] (默认: pdf)
  -o, --output-dir 输出目录
  --skip-validation 跳过转换前验证

示例:
  python convert.py -f pdf -o ./my_output
  python convert.py --skip-validation

系统要求:
  - Python 3.7+
  - Pandoc 2.0+
  - XeLaTeX (用于PDF生成)

目录结构:
  docs/chapters/chapter01/    # 章节文件
  docs/chapters/chapter02/    # 更多章节...
  docs/前言.md                # 前言文件 (可选)
  appendix/                   # 附录文件 (可选)

转换流程:
  1. 自动发现章节文件
  2. 预处理和标准化内容
  3. 合并所有内容
  4. 使用Pandoc转换
  5. 后处理和优化
  6. 质量验证

输出文件:
  - textbook.pdf/tex         # 主要输出文件
  - textbook_merged.md       # 合并的Markdown文件
  - quality_report.txt       # 质量报告
  - images/                  # 统一的图片目录

更多信息请参考 README.md
"""
    print(help_text)

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help', 'help']:
        show_help()
        sys.exit(0)
    
    exit_code = main()
    sys.exit(exit_code)