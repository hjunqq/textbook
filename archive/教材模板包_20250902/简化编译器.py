#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的LaTeX编译器
专门用于解决编码问题和简化编译过程
"""

import os
import subprocess
from pathlib import Path
import shutil

def simple_latex_compile():
    """简化的LaTeX编译过程"""
    print("🔧 简化LaTeX编译器启动...")
    
    # 定位文件
    output_dir = Path("E:/2025/教材/智慧水利平台架构与开发/publish/latex_output")
    tex_file = output_dir / "教材.tex"
    
    if not tex_file.exists():
        print(f"❌ LaTeX文件不存在: {tex_file}")
        return False
    
    print(f"📄 找到LaTeX文件: {tex_file}")
    print(f"📁 工作目录: {output_dir}")
    
    # 切换到输出目录
    original_dir = os.getcwd()
    os.chdir(output_dir)
    
    try:
        print("\n🚀 开始编译...")
        
        # 使用简单的命令行调用，避免Python编码问题
        for i in range(3):
            print(f"\n📝 第{i+1}次编译...")
            
            # 直接调用xelatex，不捕获输出
            cmd = ['xelatex', '-interaction=nonstopmode', '教材.tex']
            print(f"执行命令: {' '.join(cmd)}")
            
            result = os.system(f'xelatex -interaction=nonstopmode "教材.tex"')
            
            if result == 0:
                print(f"✅ 第{i+1}次编译成功")
            else:
                print(f"⚠️  第{i+1}次编译有警告 (返回码: {result})")
        
        # 检查结果
        pdf_path = Path("教材.pdf")
        if pdf_path.exists():
            file_size = pdf_path.stat().st_size / (1024*1024)
            print(f"\n🎉 PDF文件生成成功!")
            print(f"📊 文件路径: {output_dir / '教材.pdf'}")
            print(f"📏 文件大小: {file_size:.1f} MB")
            
            # 复制一份到桌面以便查看
            desktop = Path.home() / "Desktop" / "智慧水利教材.pdf"
            try:
                shutil.copy2(pdf_path, desktop)
                print(f"📋 已复制到桌面: {desktop}")
            except:
                print("📋 无法复制到桌面，请直接查看输出目录")
            
            return True
        else:
            print("❌ PDF文件未生成")
            
            # 检查日志文件
            log_file = Path("教材.log")
            if log_file.exists():
                print("📝 查看日志文件末尾:")
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    for line in lines[-20:]:  # 显示最后20行
                        print(f"   {line.rstrip()}")
            
            return False
    
    finally:
        os.chdir(original_dir)

def check_latex_environment():
    """检查LaTeX环境"""
    print("🔍 检查LaTeX环境...")
    
    try:
        result = subprocess.run(['xelatex', '--version'], 
                              capture_output=True, text=True, encoding='utf-8', errors='ignore')
        if result.returncode == 0:
            print("✅ XeLaTeX已安装")
            version_line = result.stdout.split('\n')[0]
            print(f"   版本: {version_line}")
        else:
            print("❌ XeLaTeX未找到")
            return False
    except:
        print("❌ 无法检查XeLaTeX")
        return False
    
    try:
        result = subprocess.run(['pandoc', '--version'], 
                              capture_output=True, text=True, encoding='utf-8', errors='ignore')
        if result.returncode == 0:
            print("✅ Pandoc已安装")
        else:
            print("❌ Pandoc未找到")
    except:
        print("❌ 无法检查Pandoc")
    
    return True

def main():
    print("=" * 50)
    print("智慧水利教材 - 简化编译器")
    print("=" * 50)
    
    if not check_latex_environment():
        print("请确保已正确安装LaTeX环境")
        return
    
    success = simple_latex_compile()
    
    if success:
        print("\n🎊 编译完成! 请查看生成的PDF文件")
    else:
        print("\n💥 编译失败，请检查错误信息")

if __name__ == "__main__":
    main()
