#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速验证脚本 - 仅测试前几个文件
"""

import sys
import subprocess
from pathlib import Path

# 添加核心模块路径
sys.path.insert(0, str(Path(__file__).parent / 'core'))

from core.config import config

def quick_test():
    """快速验证转换功能"""
    print("⚡ 快速转换验证")
    print("=" * 40)
    
    # 确保输出目录存在
    config.output_dir.mkdir(exist_ok=True)
    (config.output_dir / "images").mkdir(exist_ok=True)
    
    # 创建测试用的小文件
    test_content = """# 智慧水利平台架构与开发

## 第一章 概述

这是一个测试文档，用于验证转换功能。

### 1.1 基本概念

智慧水利是现代水利发展的重要方向。

### 1.2 技术架构

系统采用分层架构设计：

1. 数据层
2. 服务层  
3. 应用层

```javascript
// 示例代码
function init() {
    console.log("系统初始化");
}
```

### 1.3 图片测试

这里应该有一个图片：

![测试图片](images/placeholder.png)

## 小结

测试文档创建完成。
"""
    
    print("📝 创建测试文档...")
    test_md = config.output_dir / "test_small.md"
    with open(test_md, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    # 创建占位图片
    placeholder_img = config.output_dir / "images" / "placeholder.png"
    if not placeholder_img.exists():
        # 创建一个简单的1x1像素PNG（最小PNG文件）
        png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x00\x01\x00\x00\x00\x00\x90wS\xde\x00\x00\x00\x00IEND\xaeB`\x82'
        with open(placeholder_img, 'wb') as f:
            f.write(png_data)
        print("  ✅ 创建占位图片")
    
    print(f"  ✅ 测试文档: {test_md} ({len(test_content)} 字符)")
    
    # 测试1: HTML转换
    print("\n🌐 测试HTML转换...")
    html_result = test_conversion('html', 'test_small.md', 'test.html')
    
    # 测试2: LaTeX转换  
    print("\n📄 测试LaTeX转换...")
    latex_result = test_conversion('latex', 'test_small.md', 'test.tex')
    
    # 测试3: PDF转换
    print("\n🎯 测试PDF转换...")
    pdf_result = test_conversion('pdf', 'test_small.md', 'test.pdf', timeout=60)
    
    # 汇总结果
    print(f"\n📊 测试结果:")
    print(f"  HTML: {'✅ 成功' if html_result else '❌ 失败'}")
    print(f"  LaTeX: {'✅ 成功' if latex_result else '❌ 失败'}")
    print(f"  PDF: {'✅ 成功' if pdf_result else '❌ 失败'}")
    
    if html_result and latex_result:
        print(f"\n🎉 基本转换功能正常！")
        print(f"📁 测试文件位置: {config.output_dir}")
        
        if not pdf_result:
            print(f"💡 PDF转换失败可能是XeLaTeX配置问题")
            print(f"💡 请检查LaTeX环境和中文字体")
    else:
        print(f"\n❌ 基本转换功能存在问题")
        print(f"💡 请检查Pandoc安装和配置")

def test_conversion(output_format, input_file, output_file, timeout=30):
    """测试单个转换"""
    try:
        if output_format == 'pdf':
            cmd = [
                'pandoc', input_file, '-o', output_file,
                '--from=markdown', '--to=pdf',
                '--pdf-engine=xelatex'
            ]
        else:
            cmd = [
                'pandoc', input_file, '-o', output_file,
                '--from=markdown', f'--to={output_format}',
                '--standalone'
            ]
        
        print(f"  执行转换...")
        result = subprocess.run(
            cmd, capture_output=True, text=True,
            encoding='utf-8', cwd=config.output_dir,
            timeout=timeout
        )
        
        output_path = config.output_dir / output_file
        if result.returncode == 0 and output_path.exists():
            size = output_path.stat().st_size
            print(f"  ✅ 成功 ({size} bytes)")
            return True
        else:
            print(f"  ❌ 失败 (返回码: {result.returncode})")
            if result.stderr:
                error_lines = result.stderr.strip().split('\n')
                print(f"  错误: {error_lines[0][:100]}...")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"  ❌ 超时 ({timeout}秒)")
        return False
    except Exception as e:
        print(f"  ❌ 异常: {e}")
        return False

if __name__ == '__main__':
    quick_test()