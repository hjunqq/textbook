#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试脚本 - 分步骤测试转换流程
"""

import sys
import subprocess
from pathlib import Path

# 添加核心模块路径
sys.path.insert(0, str(Path(__file__).parent / 'core'))

from core.config import config

def test_step_by_step():
    """分步测试转换"""
    print("🧪 分步测试转换流程")
    print("=" * 50)
    
    # 确保输出目录存在
    config.output_dir.mkdir(exist_ok=True)
    (config.output_dir / "images").mkdir(exist_ok=True)
    
    # 步骤1：生成合并的markdown
    print("\n📝 步骤1：生成合并的Markdown文件")
    try:
        from core.converter import converter
        chapters = converter._discover_chapters()
        print(f"  发现文件: {len(chapters)} 个")
        
        merged_content = converter._process_and_merge_chapters(chapters)
        merged_file = config.get_output_path("textbook_merged.md")
        
        with open(merged_file, 'w', encoding='utf-8') as f:
            f.write(merged_content)
        
        print(f"  ✅ 合并文件已生成: {merged_file}")
        print(f"  文件大小: {merged_file.stat().st_size} bytes")
        
    except Exception as e:
        print(f"  ❌ 生成失败: {e}")
        return False
    
    # 步骤2：测试HTML转换（最简单）
    print("\n🌐 步骤2：测试HTML转换")
    html_file = config.output_dir / "test.html"
    cmd = [
        'pandoc',
        'textbook_merged.md',
        '-o', 'test.html',
        '--from=markdown',
        '--to=html',
        '--standalone'
    ]
    
    if run_pandoc_test(cmd, html_file):
        print(f"  ✅ HTML转换成功")
    else:
        print(f"  ❌ HTML转换失败")
        return False
    
    # 步骤3：测试LaTeX转换（不使用模板）
    print("\n📄 步骤3：测试基础LaTeX转换")
    latex_file = config.output_dir / "test_basic.tex"
    cmd = [
        'pandoc',
        'textbook_merged.md',
        '-o', 'test_basic.tex',
        '--from=markdown',
        '--to=latex',
        '--standalone'
    ]
    
    if run_pandoc_test(cmd, latex_file):
        print(f"  ✅ 基础LaTeX转换成功")
    else:
        print(f"  ❌ 基础LaTeX转换失败")
        return False
    
    # 步骤4：测试使用简化模板的LaTeX
    print("\n📚 步骤4：测试简化模板LaTeX转换")
    simple_template = config.templates_dir / "simple.tex"
    if simple_template.exists():
        latex_simple_file = config.output_dir / "test_simple.tex"
        cmd = [
            'pandoc',
            'textbook_merged.md',
            '-o', 'test_simple.tex',
            '--from=markdown',
            '--to=latex',
            '--template', '../templates/simple.tex',
            '--standalone'
        ]
        
        if run_pandoc_test(cmd, latex_simple_file):
            print(f"  ✅ 简化模板LaTeX转换成功")
        else:
            print(f"  ❌ 简化模板LaTeX转换失败")
            return False
    else:
        print(f"  ⚠️  简化模板不存在，跳过")
    
    # 步骤5：尝试PDF转换
    print("\n🎯 步骤5：测试PDF转换")
    pdf_file = config.output_dir / "test.pdf"
    cmd = [
        'pandoc',
        'textbook_merged.md',
        '-o', 'test.pdf',
        '--from=markdown',
        '--to=pdf',
        '--pdf-engine=xelatex'
    ]
    
    if run_pandoc_test(cmd, pdf_file, timeout=120):  # PDF转换可能需要更长时间
        print(f"  ✅ PDF转换成功")
        file_size = pdf_file.stat().st_size / 1024 / 1024  # MB
        print(f"  文件大小: {file_size:.2f} MB")
    else:
        print(f"  ❌ PDF转换失败")
        print(f"  💡 建议检查XeLaTeX安装和中文字体配置")
    
    print(f"\n🎉 测试完成！")
    print(f"📁 所有测试文件保存在: {config.output_dir}")
    return True

def run_pandoc_test(cmd, output_file, timeout=30):
    """运行Pandoc测试命令"""
    try:
        print(f"  执行: {' '.join(cmd[:3])} ...")  # 只显示主要命令
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True,
            encoding='utf-8', 
            cwd=config.output_dir,
            timeout=timeout
        )
        
        if result.returncode == 0 and output_file.exists():
            size = output_file.stat().st_size
            print(f"  生成文件: {output_file.name} ({size} bytes)")
            return True
        else:
            print(f"  失败 (返回码: {result.returncode})")
            if result.stderr:
                # 只显示前200字符的错误信息
                error_msg = result.stderr[:200].replace('\n', ' ')
                print(f"  错误: {error_msg}...")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"  超时 ({timeout}秒)")
        return False
    except Exception as e:
        print(f"  异常: {e}")
        return False

if __name__ == '__main__':
    test_step_by_step()