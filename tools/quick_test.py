#!/usr/bin/env python3
"""
快速测试脚本 - 验证转换器基本功能
"""

import os
import sys
import tempfile
from pathlib import Path

def create_test_content():
    """创建测试内容"""
    test_content = """# 第一章 测试章节

## 1.1 数学公式测试

行内公式：$x = y + z$

块级公式：
$$
E = mc^2
$$

## 1.2 代码测试

```python
def hello_world():
    print("Hello, World!")
```

行内代码：`print("test")`

## 1.3 图片测试

![测试图片](images/test.png)

## 1.4 告警框测试

!!! note "重要提示"

    这是一个重要的测试内容。

!!! warning "警告"

    这是警告信息。
"""
    return test_content

def main():
    """主测试函数"""
    print("🧪 运行快速测试...")
    
    # 创建临时测试环境
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # 创建测试目录结构
        test_source_dir = temp_path / "test_source"
        test_source_dir.mkdir()
        
        chapter01_dir = test_source_dir / "chapter01"
        chapter01_dir.mkdir()
        
        # 创建测试内容
        test_file = chapter01_dir / "chapter01.md"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(create_test_content())
        
        # 创建测试前言
        preface_file = test_source_dir / "preface.md"
        with open(preface_file, 'w', encoding='utf-8') as f:
            f.write("# 前言\n\n这是测试前言。\n")
        
        print(f"✅ 测试环境已创建: {temp_dir}")
        print(f"✅ 测试文件: {test_file}")
        
        # 导入并测试转换器
        try:
            from converter_config import ConverterConfig
            from main_converter import ConverterApplication
            
            # 创建测试配置 - 关闭PDF编译
            config = ConverterConfig(
                source_dir=str(test_source_dir),
                preface_file=str(preface_file),
                output_dir=str(temp_path / "output"),
                chapter_count=1
            )
            
            # 运行转换器（仅转换，不编译PDF）
            converter = ConverterApplication(config)
            
            # 只测试内容处理和tex生成部分
            preface_success = converter.convert_preface()
            chapter_success = converter.convert_chapter(1)
            main_tex_success = converter.generate_main_tex()
            
            success = preface_success and chapter_success and main_tex_success
            
            if success:
                print("✅ 快速测试通过！转换器工作正常")
                
                # 检查生成的文件
                output_dir = temp_path / "output"
                main_tex = output_dir / "main.tex"
                chapter_tex = output_dir / "chapters" / "chapter01.tex"
                
                if main_tex.exists():
                    print(f"✅ 主tex文件已生成: {main_tex}")
                if chapter_tex.exists():
                    print(f"✅ 章节tex文件已生成: {chapter_tex}")
                    
                # 显示部分内容进行验证
                if chapter_tex.exists():
                    with open(chapter_tex, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if '\\\\chapter{' in content:
                            print("✅ 章节标题转换正确")
                        if '\\\\begin{equation}' in content:
                            print("✅ 数学公式转换正确")
                        if '\\\\begin{tcolorbox}' in content:
                            print("✅ 告警框转换正确")
                        if '\\\\begin{lstlisting}' in content:
                            print("✅ 代码块转换正确")
                    
                return True
            else:
                print("❌ 快速测试失败")
                return False
                
        except Exception as e:
            print(f"❌ 测试出错: {e}")
            return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)