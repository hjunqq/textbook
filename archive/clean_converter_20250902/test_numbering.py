#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
编号处理测试脚本 - 验证章节编号去重是否正确
"""

import re

def test_numbering_removal():
    """测试编号移除功能"""
    print("测试章节编号去重功能")
    print("=" * 40)
    
    # 测试用例
    test_cases = [
        ("## 1.1 概述", "## 概述"),
        ("## 1.2 基本概念", "## 基本概念"),
        ("### 1.2.1 定义", "### 定义"),
        ("### 1.2.2 特点", "### 特点"),
        ("#### 1.2.2.1 详细说明", "#### 详细说明"),
        ("## 2.3 技术架构", "## 技术架构"),
        ("## 小结", "## 小结"),  # 无编号的应该保持不变
        ("## 本章小结", ""),     # 应该被删除
        ("## 思考题与练习", "")   # 应该被删除
    ]
    
    for i, (input_text, expected) in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {input_text}")
        
        content = input_text
        
        # 应用编号移除逻辑
        content = re.sub(r'^##\s+\d+\.\d+\s+(.+)', r'## \1', content, flags=re.MULTILINE)
        content = re.sub(r'^###\s+\d+\.\d+\.\d+\s+(.+)', r'### \1', content, flags=re.MULTILINE)
        content = re.sub(r'^####\s+\d+\.\d+\.\d+\.\d+\s+(.+)', r'#### \1', content, flags=re.MULTILINE)
        
        # 过滤不必要的章节
        unnecessary_sections = [
            r'^##\s+本章小结.*$',
            r'^##\s+重点难点.*$', 
            r'^##\s+思考题与练习.*$',
            r'^##\s+本节小结.*$',
            r'^##\s+参考文献.*$'
        ]
        
        for pattern in unnecessary_sections:
            content = re.sub(pattern, '', content, flags=re.MULTILINE)
        
        result = content.strip()
        
        if result == expected:
            print(f"  ✅ 正确: '{result}'")
        else:
            print(f"  ❌ 错误: 期望 '{expected}', 实际 '{result}'")

def create_test_markdown():
    """创建测试用的Markdown文件"""
    test_content = """# 第一章 智慧水利概述与平台架构基础

## 1.1 概述

这是概述内容。

### 1.1.1 背景

背景介绍。

### 1.1.2 意义

意义说明。

## 1.2 基本概念

基本概念内容。

### 1.2.1 定义

定义说明。

#### 1.2.1.1 详细定义

详细定义内容。

### 1.2.2 特点

特点说明。

## 1.3 技术架构

技术架构内容。

## 本章小结

这个章节应该被移除。

## 思考题与练习

这个章节也应该被移除。
"""
    
    from pathlib import Path
    
    script_dir = Path(__file__).parent
    test_file = script_dir / "test_numbering.md"
    
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    print(f"\n创建测试文件: {test_file}")
    
    # 应用标准化处理
    from single_chapter_converter import SingleChapterConverter
    
    converter = SingleChapterConverter()
    processed_content = converter.standardize_chapters(test_content, str(test_file))
    
    # 保存处理后的结果
    result_file = script_dir / "test_numbering_result.md"
    with open(result_file, 'w', encoding='utf-8') as f:
        f.write(processed_content)
    
    print(f"处理结果保存到: {result_file}")
    print("\n处理后的内容:")
    print("-" * 40)
    print(processed_content)

if __name__ == '__main__':
    test_numbering_removal()
    print("\n" + "=" * 40)
    create_test_markdown()