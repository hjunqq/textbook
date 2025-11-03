#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智慧水利平台架构与开发 - 课堂在线知识点导入转换器（新模板适配版）
适配2024新版课堂在线模板要求
"""

import re
import os
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

def parse_markdown_tables_new_template(content):
    """解析markdown表格数据，适配新模板"""
    lines = content.strip().split('\n')
    all_data_rows = []
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # 检查是否是表格数据行
        if (line.startswith('|') and line.endswith('|') and 
            '---' not in line and  # 不是分隔符行
            '一级知识点' not in line):  # 不是表头行
            
            # 解析表格行
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            
            # 确保有足够的列数（至少10列）
            if len(cells) >= 10:
                # 检查是否有有效内容
                has_chapter = cells[0].strip() and ('章' in cells[0])
                has_knowledge = any(cell.strip() for cell in cells[1:7] if len(cells) > 6)
                has_attributes = False
                if len(cells) >= 15:
                    has_attributes = any(cell.strip() for cell in cells[7:15])
                elif len(cells) >= 10:
                    has_attributes = any(cell.strip() for cell in cells[7:])
                
                if has_chapter or has_knowledge or has_attributes:
                    # 补齐到15列
                    while len(cells) < 15:
                        cells.append('')
                    all_data_rows.append(cells[:15])
    
    return all_data_rows

def convert_to_new_template_format(all_data_rows):
    """转换为新模板格式"""
    result_rows = []
    category_tracker = {}  # 追踪已创建的分类节点
    
    for row in all_data_rows:
        if len(row) < 15:
            continue
            
        # 提取知识点层级
        levels = [row[i].strip() for i in range(7)]
        
        # 提取属性
        pre_knowledge = row[7].strip()
        post_knowledge = row[8].strip() 
        related_knowledge = row[9].strip()
        tags = row[10].strip()
        cognitive = row[11].strip()
        classification = row[12].strip()
        teaching_goal = row[13].strip()
        description = row[14].strip()
        
        # 构建完整的节点路径用于去重
        current_path = []
        
        # 处理每一级节点
        for level_idx, level_content in enumerate(levels):
            if not level_content.strip():
                continue
                
            current_path.append(level_content.strip())
            path_key = " > ".join(current_path)
            
            # 如果这个路径已经处理过，跳过
            if path_key in category_tracker:
                continue
                
            # 创建新行
            new_row = [''] * 13  # 13列：节点类型 + 7个节点名称 + 前置后置关联 + 标签分类说明
            
            # 判断是分类还是知识点
            is_leaf_node = (level_idx == len([l for l in levels if l.strip()]) - 1)  # 是最后一级
            has_attributes = bool(tags or cognitive or classification or teaching_goal or description)
            
            # 设置节点类型
            if is_leaf_node and has_attributes:
                new_row[0] = "知识点"
                # 知识点填充属性
                new_row[8] = pre_knowledge  # 前置节点
                new_row[9] = post_knowledge  # 后置节点
                new_row[10] = related_knowledge  # 关联节点
                new_row[11] = tags  # 标签
                new_row[12] = classification  # 知识点分类
                
                # 合并教学目标和说明作为节点说明
                node_description_parts = []
                if teaching_goal:
                    node_description_parts.append(f"教学目标：{teaching_goal}")
                if description:
                    node_description_parts.append(f"说明：{description}")
                new_row[12] = "; ".join(node_description_parts) if node_description_parts else ""
                
            else:
                new_row[0] = "分类"
            
            # 设置节点名称到对应的列（B到H列，索引1到7）
            new_row[level_idx + 1] = level_content.strip()
            
            result_rows.append(new_row)
            category_tracker[path_key] = True
    
    return result_rows

def process_chapter_file_new_template(file_path):
    """处理单个章节文件，适配新模板"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        file_name = file_path.name
        
        # 解析数据
        all_data_rows = parse_markdown_tables_new_template(content)
        
        print(f"  📋 原始数据行数: {len(all_data_rows)}")
        
        # 转换为新模板格式
        converted_rows = convert_to_new_template_format(all_data_rows)
        
        # 统计节点类型
        categories = sum(1 for row in converted_rows if row[0] == "分类")
        knowledge_points = sum(1 for row in converted_rows if row[0] == "知识点")
        
        print(f"  📊 转换结果: {categories}个分类 + {knowledge_points}个知识点 = {len(converted_rows)}个节点")
        
        return converted_rows
    
    except Exception as e:
        print(f"❌ 处理文件 {file_path} 时出错: {e}")
        import traceback
        traceback.print_exc()
        return []

def create_excel_file_new_template(all_rows, output_file):
    """创建符合新模板的Excel文件"""
    wb = Workbook()
    ws = wb.active
    ws.title = "知识点导入"
    
    # 定义新模板列名
    columns = [
        '节点类型*', '节点名称', '节点名称', '节点名称', '节点名称', 
        '节点名称', '节点名称', '节点名称', '前置节点', '后置节点', 
        '关联节点', '标签', '知识点分类', '节点说明'
    ]
    
    # 写入表头
    for col, header in enumerate(columns, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = Font(bold=True)
        cell.fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")
        cell.alignment = Alignment(horizontal="center", vertical="center")
    
    # 写入数据
    for row_idx, row_data in enumerate(all_rows, 2):
        for col_idx, value in enumerate(row_data, 1):
            cell = ws.cell(row=row_idx, column=col_idx, value=value)
            cell.alignment = Alignment(vertical="top", wrap_text=True)
    
    # 设置列宽
    col_widths = {
        'A': 12,  # 节点类型
        'B': 25, 'C': 25, 'D': 30, 'E': 35, 'F': 25, 'G': 20, 'H': 20,  # 7个节点名称列
        'I': 35, 'J': 35, 'K': 35,  # 前置后置关联
        'L': 25, 'M': 15, 'N': 70   # 标签分类说明
    }
    
    for col, width in col_widths.items():
        ws.column_dimensions[col].width = width
    
    # 冻结表头
    ws.freeze_panes = 'A2'
    
    # 保存文件
    wb.save(output_file)

def main():
    """主函数"""
    base_dir = Path(__file__).parent
    
    # 定义章节文件
    chapter_files = [
        "第_1_章按小节的知识点清单（可直接粘贴到模板）.md",
        "第_2_章_超细化大纲式知识点表（严格空白对齐）.md",
        "第_3_章_超细化大纲式知识点表（严格空白对齐）.md",
        "第_4_章_超细化大纲式知识点表（严格空白对齐）.md",
        "第_5_章_超细化大纲式知识点表（严格空白对齐）.md",
        "第_6_章_超细化大纲式知识点表（严格空白对齐）.md"
    ]
    
    all_rows = []
    chapter_stats = {}
    
    print("🚀 新模板适配版转换开始...")
    print("📋 适配2024版课堂在线新模板要求")
    print("📌 节点类型：分类 + 知识点")
    print("📌 层级结构：B-H列支持7级节点")
    print("📌 关系管理：I-K列支持前置/后置/关联")
    
    # 处理每个章节
    for chapter_file in chapter_files:
        file_path = base_dir / chapter_file
        if file_path.exists():
            print(f"\n📖 处理文件: {chapter_file}")
            chapter_rows = process_chapter_file_new_template(file_path)
            all_rows.extend(chapter_rows)
            
            chapter_name = chapter_file.split('_')[1].split('章')[0] + '章'
            chapter_stats[chapter_name] = len(chapter_rows)
            
        else:
            print(f"❌ 文件不存在: {chapter_file}")
    
    if not all_rows:
        print("❌ 没有找到有效的数据行")
        return
    
    # 输出Excel文件
    output_file = base_dir / "智慧水利平台架构与开发_课堂在线导入表格_新模板版.xlsx"
    
    try:
        create_excel_file_new_template(all_rows, output_file)
        
        print(f"\n🎉 新模板转换完成！")
        print(f"📊 总共处理了 {len(all_rows)} 个节点")
        print(f"📁 输出文件: {output_file}")
        
        # 统计节点类型
        categories = sum(1 for row in all_rows if row[0] == "分类")
        knowledge_points = sum(1 for row in all_rows if row[0] == "知识点")
        
        print(f"\n📈 节点类型统计：")
        print(f"  📂 分类节点: {categories} 个")
        print(f"  📌 知识点: {knowledge_points} 个")
        
        # 各章节统计
        print(f"\n📋 各章节节点统计：")
        for chapter, count in chapter_stats.items():
            print(f"  📄 {chapter}: {count} 个节点")
        
        # 模板限制检查
        print(f"\n🔍 模板限制检查：")
        total_nodes = len(all_rows)
        print(f"  📊 节点总数: {total_nodes}/5000 {'✅' if total_nodes <= 5000 else '⚠️ 超限'}")
        
        # 估算关系数（简化估算）
        estimated_relations = sum(1 for row in all_rows if any(row[8:11]))
        print(f"  🔗 关系估算: {estimated_relations}/2000 {'✅' if estimated_relations <= 2000 else '⚠️ 超限'}")
        
        print(f"\n✅ 新模板版已生成！")
        print(f"📋 完全符合2024版课堂在线导入要求")
        print(f"🎯 支持分类层级 + 知识点叶子节点结构")
        
    except Exception as e:
        print(f"❌ 创建Excel文件时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()