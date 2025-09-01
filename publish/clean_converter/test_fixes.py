#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
表格和编号修复测试工具
"""

def create_test_content():
    """创建包含问题的测试内容"""
    test_markdown = """# 第一章 智慧水利概述

## 1.1 概述

这是第一节的内容。

### 关键概念表格

下面是一个有问题的表格：

| 概念 | 定义 | 重要性
|水利信息化|运用信息技术改造传统水利|高
智慧水利 | 全面感知、实时分析 | 很高
| 数字孪生 | 物理世界数字化映射 | 中等

### 1.1.1 技术特点

另一个表格：

概念|说明
---|---
物联网|感知层核心技术
云计算|计算资源虚拟化

## 1.2 技术架构

技术架构的详细说明。

### 1.2.1 系统组成

系统组成内容。

## 本章小结

这个应该被删除。
"""
    return test_markdown

def test_fixes():
    """测试修复功能"""
    print("=" * 60)
    print("表格和编号修复测试")
    print("=" * 60)
    
    from pathlib import Path
    script_dir = Path(__file__).parent
    
    # 导入转换器
    import sys
    sys.path.append(str(script_dir))
    from single_chapter_converter import SingleChapterConverter
    
    # 创建转换器
    converter = SingleChapterConverter()
    
    # 创建测试内容
    test_content = create_test_content()
    print("原始内容:")
    print("-" * 30)
    print(test_content[:500] + "...")
    
    # 测试预处理
    fake_file_path = script_dir / "test_chapter01.md"
    processed_content = converter.preprocess_markdown(test_content, str(fake_file_path), "chapter01")
    
    print("\n" + "=" * 60)
    print("处理后内容:")
    print("-" * 30)
    print(processed_content)
    
    # 保存到文件以便检查
    output_file = script_dir / "test_fixes_result.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(processed_content)
    
    print(f"\n处理结果已保存到: {output_file}")
    
    # 检查关键修复点
    print("\n" + "=" * 60)
    print("修复检查:")
    print("-" * 30)
    
    lines = processed_content.split('\n')
    
    # 检查编号
    section_lines = [line for line in lines if line.startswith('##')]
    print(f"✓ 找到 {len(section_lines)} 个二级标题:")
    for line in section_lines:
        print(f"  {line}")
    
    # 检查表格
    table_lines = [line for line in lines if '|' in line and line.strip()]
    print(f"\n✓ 找到 {len(table_lines)} 行表格内容:")
    for line in table_lines[:5]:  # 只显示前5行
        print(f"  {line}")
    if len(table_lines) > 5:
        print(f"  ... 还有 {len(table_lines) - 5} 行")
    
    # 检查不必要章节是否被删除
    if "本章小结" not in processed_content:
        print(f"\n✓ '本章小结' 已被正确删除")
    else:
        print(f"\n❌ '本章小结' 未被删除")

if __name__ == '__main__':
    test_fixes()