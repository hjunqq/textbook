#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智慧水利教材质量检查与修复工具
在转换前检查常见问题并提供修复建议

版本: v1.0
作者: AI Assistant  
日期: 2025年8月31日
"""

import os
import re
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple

class TextbookQualityChecker:
    """教材质量检查器"""
    
    def __init__(self):
        self.issues = []
        self.statistics = {
            'total_files': 0,
            'total_lines': 0,
            'total_words': 0,
            'code_blocks': 0,
            'images': 0,
            'tables': 0,
            'chapters': 0,
            'sections': 0
        }
        
        # 质量标准
        self.standards = {
            'min_chapter_words': 1000,
            'max_line_length': 120,
            'required_sections': ['学习目标', '本章小结'],
            'image_formats': ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.pdf'],
            'code_languages': ['python', 'javascript', 'java', 'csharp', 'sql', 'html', 'css']
        }
    
    def check_file_encoding(self, file_path: str) -> Dict[str, Any]:
        """检查文件编码"""
        try:
            # 尝试UTF-8编码读取
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            return {
                'encoding': 'utf-8',
                'confidence': 1.0,
                'issue': None
            }
        except UnicodeDecodeError:
            try:
                # 尝试GBK编码
                with open(file_path, 'r', encoding='gbk') as f:
                    content = f.read()
                    
                return {
                    'encoding': 'gbk',
                    'confidence': 0.8,
                    'issue': {
                        'type': 'encoding',
                        'severity': 'warning',
                        'file': file_path,
                        'message': f"文件编码为GBK，建议转换为UTF-8",
                        'fix': "将文件重新保存为UTF-8编码"
                    }
                }
            except Exception as e:
                return {
                    'encoding': 'unknown',
                    'confidence': 0,
                    'issue': {
                        'type': 'encoding',
                        'severity': 'error',
                        'file': file_path,
                        'message': f"无法识别文件编码: {e}",
                        'fix': "检查文件是否损坏"
                    }
                }
    
    def check_markdown_syntax(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """检查Markdown语法"""
        issues = []
        lines = content.split('\n')
        
        # 检查标题层级
        heading_levels = []
        for i, line in enumerate(lines, 1):
            if line.strip().startswith('#'):
                level = len(re.match(r'^#+', line.strip()).group())
                heading_levels.append((i, level))
                
                # 检查标题格式
                if not re.match(r'^#+\s+\S', line.strip()):
                    issues.append({
                        'type': 'heading_format',
                        'severity': 'warning',
                        'file': file_path,
                        'line': i,
                        'message': f"标题格式不正确: {line.strip()}",
                        'fix': "标题后应有空格，如: ## 标题内容"
                    })
        
        # 检查标题层级跳跃
        for i in range(1, len(heading_levels)):
            prev_level = heading_levels[i-1][1]
            curr_level = heading_levels[i][1]
            
            if curr_level > prev_level + 1:
                issues.append({
                    'type': 'heading_level_jump',
                    'severity': 'warning',
                    'file': file_path,
                    'line': heading_levels[i][0],
                    'message': f"标题层级跳跃过大: 从{prev_level}级跳到{curr_level}级",
                    'fix': f"建议使用{prev_level + 1}级标题"
                })
        
        return issues
    
    def check_images(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """检查图片问题"""
        issues = []
        
        # 查找所有图片引用
        image_pattern = r'!\[(.*?)\]\((.*?)\)'
        images = re.findall(image_pattern, content)
        
        for alt_text, image_path in images:
            # 检查图片文件是否存在
            if not os.path.isabs(image_path):
                full_path = Path(file_path).parent / image_path
            else:
                full_path = Path(image_path)
            
            if not full_path.exists():
                issues.append({
                    'type': 'missing_image',
                    'severity': 'error',
                    'file': file_path,
                    'message': f"图片文件不存在: {image_path}",
                    'fix': f"检查图片路径或添加缺失的图片文件"
                })
            
            # 检查图片格式
            if full_path.exists():
                file_ext = full_path.suffix.lower()
                if file_ext not in self.standards['image_formats']:
                    issues.append({
                        'type': 'unsupported_image_format',
                        'severity': 'warning',
                        'file': file_path,
                        'message': f"不支持的图片格式: {file_ext}",
                        'fix': f"建议转换为PNG或JPG格式"
                    })
            
            # 检查图片描述
            if not alt_text.strip():
                issues.append({
                    'type': 'missing_alt_text',
                    'severity': 'warning',
                    'file': file_path,
                    'message': f"图片缺少描述文字: {image_path}",
                    'fix': "添加有意义的图片描述"
                })
        
        return issues
    
    def check_code_blocks(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """检查代码块问题"""
        issues = []
        lines = content.split('\n')
        
        in_code_block = False
        code_block_start = 0
        
        for i, line in enumerate(lines, 1):
            if line.strip().startswith('```'):
                if not in_code_block:
                    # 开始代码块
                    in_code_block = True
                    code_block_start = i
                    
                    # 检查是否指定了语言
                    if line.strip() == '```':
                        issues.append({
                            'type': 'missing_code_language',
                            'severity': 'warning',
                            'file': file_path,
                            'line': i,
                            'message': "代码块未指定编程语言",
                            'fix': "添加语言标识，如: ```python"
                        })
                else:
                    # 结束代码块
                    in_code_block = False
        
        # 检查未闭合的代码块
        if in_code_block:
            issues.append({
                'type': 'unclosed_code_block',
                'severity': 'error',
                'file': file_path,
                'line': code_block_start,
                'message': "代码块未正确闭合",
                'fix': "添加结束标记 ```"
            })
        
        return issues
    
    def check_chapter_structure(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """检查章节结构"""
        issues = []
        filename = Path(file_path).name
        
        # 如果是章节主文件，检查必需的节
        if filename.startswith('chapter') and filename.endswith('.md'):
            for required_section in self.standards['required_sections']:
                if required_section not in content:
                    issues.append({
                        'type': 'missing_section',
                        'severity': 'warning',
                        'file': file_path,
                        'message': f"缺少必需的节: {required_section}",
                        'fix': f"添加 ## {required_section} 节"
                    })
        
        # 检查内容长度
        word_count = len(re.findall(r'[\u4e00-\u9fff\w]+', content))
        if word_count < self.standards['min_chapter_words']:
            issues.append({
                'type': 'insufficient_content',
                'severity': 'info',
                'file': file_path,
                'message': f"内容较少，仅{word_count}字",
                'fix': "考虑扩充内容"
            })
        
        return issues
    
    def check_links(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """检查链接问题"""
        issues = []
        
        # 检查内部链接
        internal_link_pattern = r'\[([^\]]+)\]\(([^)]+\.md[^)]*)\)'
        internal_links = re.findall(internal_link_pattern, content)
        
        for link_text, link_path in internal_links:
            # 移除锚点
            clean_path = link_path.split('#')[0]
            
            if not os.path.isabs(clean_path):
                full_path = Path(file_path).parent / clean_path
            else:
                full_path = Path(clean_path)
            
            if not full_path.exists():
                issues.append({
                    'type': 'broken_internal_link',
                    'severity': 'error',
                    'file': file_path,
                    'message': f"内部链接文件不存在: {clean_path}",
                    'fix': "检查链接路径或创建缺失的文件"
                })
        
        return issues
    
    def check_file(self, file_path: str) -> Dict[str, Any]:
        """检查单个文件"""
        file_issues = []
        
        # 检查文件编码
        encoding_result = self.check_file_encoding(file_path)
        if encoding_result['issue']:
            file_issues.append(encoding_result['issue'])
        
        # 读取文件内容
        try:
            with open(file_path, 'r', encoding=encoding_result['encoding']) as f:
                content = f.read()
        except Exception as e:
            return {
                'file': file_path,
                'issues': [{
                    'type': 'read_error',
                    'severity': 'error',
                    'message': f"无法读取文件: {e}",
                    'fix': "检查文件权限或编码"
                }],
                'statistics': {}
            }
        
        # 各项检查
        file_issues.extend(self.check_markdown_syntax(content, file_path))
        file_issues.extend(self.check_images(content, file_path))
        file_issues.extend(self.check_code_blocks(content, file_path))
        file_issues.extend(self.check_chapter_structure(content, file_path))
        file_issues.extend(self.check_links(content, file_path))
        
        # 统计信息
        lines = content.split('\n')
        words = len(re.findall(r'[\u4e00-\u9fff\w]+', content))
        code_blocks = len(re.findall(r'```', content)) // 2
        images = len(re.findall(r'!\[.*?\]\(.*?\)', content))
        tables = content.count('|')
        
        file_stats = {
            'lines': len(lines),
            'words': words,
            'code_blocks': code_blocks,
            'images': images,
            'tables': tables
        }
        
        return {
            'file': file_path,
            'issues': file_issues,
            'statistics': file_stats
        }
    
    def check_directory(self, directory: str) -> Dict[str, Any]:
        """检查整个目录"""
        print(f"检查目录: {directory}")
        
        markdown_files = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.md'):
                    markdown_files.append(os.path.join(root, file))
        
        print(f"找到 {len(markdown_files)} 个Markdown文件")
        
        all_issues = []
        total_stats = {
            'total_files': len(markdown_files),
            'total_lines': 0,
            'total_words': 0,
            'total_code_blocks': 0,
            'total_images': 0,
            'total_tables': 0
        }
        
        file_results = []
        
        for file_path in markdown_files:
            print(f"检查文件: {Path(file_path).name}")
            result = self.check_file(file_path)
            
            file_results.append(result)
            all_issues.extend(result['issues'])
            
            # 累加统计
            stats = result['statistics']
            total_stats['total_lines'] += stats.get('lines', 0)
            total_stats['total_words'] += stats.get('words', 0)
            total_stats['total_code_blocks'] += stats.get('code_blocks', 0)
            total_stats['total_images'] += stats.get('images', 0)
            total_stats['total_tables'] += stats.get('tables', 0)
        
        return {
            'directory': directory,
            'files': file_results,
            'all_issues': all_issues,
            'statistics': total_stats,
            'summary': self.generate_summary(all_issues)
        }
    
    def generate_summary(self, issues: List[Dict]) -> Dict[str, int]:
        """生成问题摘要"""
        summary = {
            'total': len(issues),
            'error': 0,
            'warning': 0,
            'info': 0
        }
        
        for issue in issues:
            severity = issue.get('severity', 'info')
            if severity in summary:
                summary[severity] += 1
        
        return summary
    
    def print_report(self, results: Dict[str, Any]):
        """打印检查报告"""
        print("\n" + "=" * 60)
        print("教材质量检查报告")
        print("=" * 60)
        
        stats = results['statistics']
        print(f"检查目录: {results['directory']}")
        print(f"文件总数: {stats['total_files']}")
        print(f"总行数: {stats['total_lines']:,}")
        print(f"总字数: {stats['total_words']:,}")
        print(f"代码块数: {stats['total_code_blocks']}")
        print(f"图片数: {stats['total_images']}")
        
        summary = results['summary']
        print(f"\n问题统计:")
        print(f"  总计: {summary['total']}")
        print(f"  错误: {summary['error']}")
        print(f"  警告: {summary['warning']}")
        print(f"  信息: {summary['info']}")
        
        if results['all_issues']:
            print(f"\n详细问题:")
            for i, issue in enumerate(results['all_issues'], 1):
                file_name = Path(issue['file']).name
                severity_icon = {'error': '❌', 'warning': '⚠️', 'info': 'ℹ️'}.get(issue['severity'], '?')
                print(f"{i:3d}. {severity_icon} [{file_name}] {issue['message']}")
                if 'line' in issue:
                    print(f"     行号: {issue['line']}")
                print(f"     建议: {issue['fix']}")
                print()
        else:
            print("\n🎉 未发现质量问题！")
    
    def save_report(self, results: Dict[str, Any], output_file: str):
        """保存检查报告"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"报告已保存到: {output_file}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='教材质量检查工具')
    parser.add_argument('directory', help='要检查的目录路径')
    parser.add_argument('--output', '-o', help='输出报告文件路径')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.directory):
        print(f"错误：目录不存在: {args.directory}")
        return
    
    # 创建检查器
    checker = TextbookQualityChecker()
    
    # 执行检查
    results = checker.check_directory(args.directory)
    
    # 显示报告
    checker.print_report(results)
    
    # 保存报告
    if args.output:
        checker.save_report(results, args.output)
    else:
        default_output = Path(args.directory) / "质量检查报告.json"
        checker.save_report(results, str(default_output))


if __name__ == '__main__':
    main()
