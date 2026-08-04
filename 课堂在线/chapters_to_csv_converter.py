#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智慧水利平台架构与开发 - 课堂在线知识点导入转换器
将1-6章的markdown文件转换为符合课堂在线要求的Excel格式

课堂在线要求：
1. A列至G列对应知识点的层级关系，区间内每行只能填写一个知识点
2. H列至J列填写对应知识点的前置、后置和关联知识点，多个知识点之间用英文分号";"隔开
3. 任意两个知识点之间只能存在一种关系（前置、后置或关联），新导入的关系将覆盖旧关系
4. 固定标签包括：重点、难点、考点、课程思政，可根据需要自定义标签，多个标签之间用英文分号";"隔开
5. 认知维度包括：记忆、理解、应用、分析、评价、创造，每个知识点只能填入一个认知维度
6. 知识点分类包括：事实性、概念性、程序性、元认知，每个知识点只能填入一个分类
7. 知识点说明仅支持输入文本，暂不支持图片、公式等
"""

import csv
import re
import os
from pathlib import Path

def parse_markdown_table(content, chapter_name):
    """解析markdown表格内容"""
    lines = content.strip().split('\n')
    data_rows = []
    current_chapter = ""
    
    # 跳过说明文字，找到表格开始
    table_start = -1
    for i, line in enumerate(lines):
        if line.strip().startswith('| 一级知识点'):
            table_start = i
            break
    
    if table_start == -1:
        return []
    
    # 跳过表头和分隔符
    for i in range(table_start + 2, len(lines)):
        line = lines[i].strip()
        if line.startswith('|') and line.endswith('|') and '---' not in line:
            # 解析表格行
            cells = [cell.strip() for cell in line.split('|')[1:-1]]  # 去掉首尾的空字符串
            if len(cells) >= 15:  # 确保有足够的列
                data_rows.append([chapter_name] + cells)
        elif line.startswith('---') or line.startswith('>') or line.startswith('## '):
            # 遇到分隔符、说明文字或新章节，结束当前表格解析
            if line.startswith('## '):
                # 新的小节开始，继续查找下一个表格
                continue
        elif not line.strip():
            # 空行，跳过
            continue
    
    return data_rows

def convert_to_classroom_online_format(data_rows):
    """转换为课堂在线格式，确保每行只有一个知识点"""
    result_rows = []
    
    for row in data_rows:
        if len(row) < 16:  # 包含chapter_name，所以是16列
            continue
        
        chapter_name = row[0]
        # 提取各列数据
        level1 = row[1].strip()
        level2 = row[2].strip()
        level3 = row[3].strip()
        level4 = row[4].strip()
        level5 = row[5].strip()
        level6 = row[6].strip()
        level7 = row[7].strip()
        
        pre_knowledge = row[8].strip()
        post_knowledge = row[9].strip()
        related_knowledge = row[10].strip()
        tags = row[11].strip()
        cognitive = row[12].strip()
        classification = row[13].strip()
        teaching_goal = row[14].strip()
        description = row[15].strip()
        
        # 课堂在线格式要求：每行只能有一个知识点
        new_row = [''] * 15  # 初始化空行
        
        # 确定当前行应该填写哪一级知识点
        if level1 and not level2 and not level3 and not level4:
            # 一级知识点行
            new_row[0] = level1
        elif level2 and not level3 and not level4:
            # 二级知识点行  
            new_row[1] = level2
        elif level3 and not level4:
            # 三级知识点行
            new_row[2] = level3
            # 只有三级和四级才填写属性信息
            if tags or cognitive or classification or teaching_goal or description:
                new_row[7] = pre_knowledge
                new_row[8] = post_knowledge
                new_row[9] = related_knowledge
                new_row[10] = tags
                new_row[11] = cognitive
                new_row[12] = classification
                new_row[13] = teaching_goal
                new_row[14] = description
        elif level4:
            # 四级知识点行
            new_row[3] = level4
            # 填写属性信息
            new_row[7] = pre_knowledge
            new_row[8] = post_knowledge
            new_row[9] = related_knowledge
            new_row[10] = tags
            new_row[11] = cognitive
            new_row[12] = classification
            new_row[13] = teaching_goal
            new_row[14] = description
        
        # 如果是有效行，添加到结果中
        if any(new_row[:7]):  # 如果前7列中有任何内容
            result_rows.append(new_row)
    
    return result_rows

def process_chapter_file(file_path, chapter_name):
    """处理单个章节文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 解析表格
        data_rows = parse_markdown_table(content, chapter_name)
        
        # 转换格式
        converted_rows = convert_to_classroom_online_format(data_rows)
        
        return converted_rows
    
    except Exception as e:
        print(f"处理文件 {file_path} 时出错: {e}")
        return []

def main():
    """主函数"""
    base_dir = Path(__file__).parent
    
    # 定义章节文件
    chapter_files = [
        ("第_1_章按小节的知识点清单（可直接粘贴到模板）.md", "第1章 软件工程概述"),
        ("第_2_章_超细化大纲式知识点表（严格空白对齐）.md", "第2章 需求分析"),
        ("第_3_章_超细化大纲式知识点表（严格空白对齐）.md", "第3章 架构设计"),
        ("第_4_章_超细化大纲式知识点表（严格空白对齐）.md", "第4章 软件开发项目管理"),
        ("第_5_章_超细化大纲式知识点表（严格空白对齐）.md", "第5章 前端开发技术"),
        ("第_6_章_超细化大纲式知识点表（严格空白对齐）.md", "第6章 后端开发技术")
    ]
    
    # 定义列名
    columns = [
        '一级知识点', '二级知识点', '三级知识点', '四级知识点', 
        '五级知识点', '六级知识点', '七级知识点',
        '前置知识点', '后置知识点', '关联知识点',
        '标签', '认知维度', '分类', '教学目标', '知识点说明'
    ]
    
    all_rows = []
    
    # 处理每个章节
    for chapter_file, chapter_name in chapter_files:
        file_path = base_dir / chapter_file
        if file_path.exists():
            print(f"处理文件: {chapter_file}")
            chapter_rows = process_chapter_file(file_path, chapter_name)
            all_rows.extend(chapter_rows)
            print(f"  - 转换了 {len(chapter_rows)} 行数据")
        else:
            print(f"文件不存在: {chapter_file}")
    
    if not all_rows:
        print("没有找到有效的数据行")
        return
    
    # 输出CSV文件（可以用Excel打开）
    output_file = base_dir / "智慧水利平台架构与开发_课堂在线导入表格.csv"
    
    with open(output_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile)
        
        # 写入表头
        writer.writerow(columns)
        
        # 写入数据
        for row in all_rows:
            writer.writerow(row)
    
    print(f"\n转换完成！")
    print(f"总共处理了 {len(all_rows)} 行数据")
    print(f"输出文件: {output_file}")
    print(f"\n请检查生成的CSV文件，确保格式符合课堂在线的导入要求：")
    print("1. 每行只填写一个层级的知识点")
    print("2. 前置/后置/关联知识点用英文分号分隔")
    print("3. 标签用英文分号分隔")
    print("4. 认知维度和分类每个知识点只能填一个")
    print("\n注意：CSV文件可以用Excel打开，然后另存为xlsx格式")

if __name__ == "__main__":
    main()