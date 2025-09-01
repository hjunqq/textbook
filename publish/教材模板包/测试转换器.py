#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智慧水利教材转换器测试脚本
用于验证转换器的各项功能是否正常

版本: v1.0
日期: 2025年8月31日
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

def create_test_environment():
    """创建测试环境"""
    # 创建临时测试目录
    temp_dir = Path(tempfile.mkdtemp(prefix="textbook_test_"))
    
    # 创建测试文件结构
    docs_dir = temp_dir / "docs"
    chapters_dir = docs_dir / "chapters"
    
    docs_dir.mkdir(parents=True)
    chapters_dir.mkdir(parents=True)
    
    # 创建前言
    preface_content = """# 前言

这是一本关于智慧水利平台架构与开发的教材。

## 编写目的

本教材旨在帮助读者理解和掌握智慧水利平台的开发技术。
"""
    (docs_dir / "前言.md").write_text(preface_content, encoding='utf-8')
    
    # 创建第一章
    chapter01_dir = chapters_dir / "chapter01"
    chapter01_dir.mkdir()
    
    chapter01_content = """# 第一章 智慧水利概述

## 学习目标

通过本章学习，学生应能够：
1. 理解智慧水利的基本概念
2. 掌握平台架构的基本原理

## 1.1 基本概念

智慧水利是现代信息技术与传统水利工程的结合。

### 技术特点

- 🎯 目标明确
- 💡 技术先进
- 🔧 实用性强

!!! info "重要提示"
    请认真学习本章内容。

## 代码示例

```python
def hello_world():
    print("Hello, Smart Water!")
    return True
```

```javascript
function initPlatform() {
    console.log("Platform initialized");
}
```

## 本章小结

本章介绍了智慧水利的基本概念。
"""
    (chapter01_dir / "chapter01.md").write_text(chapter01_content, encoding='utf-8')
    
    # 创建第一节
    section01_content = """## 1.1 智慧水利技术基础

### 1.1.1 物联网技术

物联网技术是智慧水利的基础。

![物联网架构](images/iot_architecture.png)

### 1.1.2 大数据技术

大数据技术处理海量水利数据。

```sql
SELECT * FROM water_data 
WHERE date >= '2024-01-01'
ORDER BY timestamp;
```

### 小结

本节介绍了核心技术。
"""
    (chapter01_dir / "section01-01.md").write_text(section01_content, encoding='utf-8')
    
    # 创建测试图片
    assets_dir = docs_dir / "assets"
    assets_dir.mkdir()
    
    # 创建一个简单的测试图片（实际应用中应该是真实图片）
    test_image_content = "Test Image Content (PNG placeholder)"
    (assets_dir / "iot_architecture.png").write_text(test_image_content, encoding='utf-8')
    
    print(f"测试环境创建完成: {temp_dir}")
    return temp_dir

def test_converter(test_dir):
    """测试转换器"""
    print("开始测试转换器...")
    
    # 将当前工作目录切换到测试目录
    original_dir = os.getcwd()
    os.chdir(test_dir)
    
    try:
        # 导入转换器
        sys.path.insert(0, str(Path(__file__).parent))
        from 智慧水利教材终极转换器 import SmartWaterTextbookConverter
        
        # 创建转换器实例
        converter = SmartWaterTextbookConverter()
        
        # 测试章节发现
        print("测试章节发现...")
        try:
            chapters = converter.discover_chapters()
            print(f"✅ 发现章节: {len(chapters)} 个")
            for chapter in chapters:
                print(f"  - {Path(chapter).name}")
        except Exception as e:
            print(f"❌ 章节发现失败: {e}")
            return False
        
        # 测试预处理
        print("测试预处理...")
        try:
            test_content = "# 测试\n\n```\nprint('test')\n```\n\n![test](images/test.png)"
            processed = converter.preprocess_markdown(test_content, "test.md")
            print("✅ 预处理成功")
        except Exception as e:
            print(f"❌ 预处理失败: {e}")
            return False
        
        # 测试合并
        print("测试合并...")
        try:
            if chapters:
                merged = converter.merge_chapters(chapters[:1])  # 只测试第一个文件
                print("✅ 合并成功")
        except Exception as e:
            print(f"❌ 合并失败: {e}")
            return False
        
        print("✅ 转换器基础功能测试通过")
        return True
        
    except ImportError as e:
        print(f"❌ 导入转换器失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试过程出错: {e}")
        return False
    finally:
        os.chdir(original_dir)

def test_quality_checker(test_dir):
    """测试质量检查器"""
    print("开始测试质量检查器...")
    
    try:
        # 导入质量检查器
        sys.path.insert(0, str(Path(__file__).parent))
        from 教材质量检查器 import TextbookQualityChecker
        
        # 创建检查器实例
        checker = TextbookQualityChecker()
        
        # 测试检查
        chapters_dir = test_dir / "docs" / "chapters"
        if chapters_dir.exists():
            result = checker.check_directory(str(chapters_dir))
            print(f"✅ 质量检查完成，发现 {result['summary']['total']} 个问题")
            return True
        else:
            print("❌ 测试目录不存在")
            return False
        
    except ImportError as e:
        print(f"❌ 导入质量检查器失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 质量检查测试失败: {e}")
        return False

def cleanup_test_environment(test_dir):
    """清理测试环境"""
    try:
        shutil.rmtree(test_dir)
        print(f"✅ 测试环境清理完成: {test_dir}")
    except Exception as e:
        print(f"❌ 清理测试环境失败: {e}")

def main():
    """主测试函数"""
    print("=" * 60)
    print("智慧水利教材转换器功能测试")
    print("=" * 60)
    
    # 创建测试环境
    test_dir = create_test_environment()
    
    try:
        # 测试转换器
        converter_ok = test_converter(test_dir)
        
        # 测试质量检查器
        checker_ok = test_quality_checker(test_dir)
        
        # 总结
        print("\n" + "=" * 60)
        if converter_ok and checker_ok:
            print("✅ 所有测试通过！转换器可以正常使用")
        else:
            print("❌ 部分测试失败，请检查错误信息")
        print("=" * 60)
        
    finally:
        # 清理测试环境
        cleanup_test_environment(test_dir)

if __name__ == '__main__':
    main()
