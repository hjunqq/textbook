#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
教材质量自动检查工具
检查教材中的常见问题并提供修复建议
版本: v2.0
更新: 2025年8月7日
"""

import os
import re
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any, Tuple
import chardet


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
        
        # 质量标准配置
        self.standards = {
            'min_chapter_words': 2000,
            'max_line_length': 100,
            'required_sections': ['学习目标', '本章小结', '思考题'],
            'code_style_patterns': {
                'csharp': r'using\s+\w+;',
                'javascript': r'function\s+\w+\s*\(',
                'python': r'def\s+\w+\s*\(',
                'sql': r'SELECT\s+.*\s+FROM'
            }
        }
    
    def check_file_encoding(self, file_path: str) -> Dict[str, Any]:
        """检查文件编码"""
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read()
                result = chardet.detect(raw_data)
                
                encoding = result.get('encoding', 'unknown')
                confidence = result.get('confidence', 0)
                
                issue = None
                if encoding.lower() not in ['utf-8', 'utf-8-sig']:
                    issue = {
                        'type': 'encoding',
                        'severity': 'warning',
                        'file': file_path,
                        'message': f"文件编码为 {encoding}，建议使用 UTF-8",
                        'fix': f"将文件重新保存为 UTF-8 编码"
                    }
                
                return {
                    'encoding': encoding,
                    'confidence': confidence,
                    'issue': issue
                }
        except Exception as e:
            return {
                'encoding': 'error',
                'confidence': 0,
                'issue': {
                    'type': 'encoding',
                    'severity': 'error',
                    'file': file_path,
                    'message': f"无法检测文件编码: {e}",
                    'fix': "检查文件是否损坏或权限问题"
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
                        'type': 'markdown_syntax',
                        'severity': 'warning',
                        'file': file_path,
                        'line': i,
                        'message': "标题格式不规范，# 后应有空格",
                        'fix': "在 # 后添加空格，如：# 标题内容"
                    })
        
        # 检查标题跳级
        for i in range(1, len(heading_levels)):
            prev_level = heading_levels[i-1][1]
            curr_level = heading_levels[i][1]
            curr_line = heading_levels[i][0]
            
            if curr_level > prev_level + 1:
                issues.append({
                    'type': 'heading_structure',
                    'severity': 'warning',
                    'file': file_path,
                    'line': curr_line,
                    'message': f"标题跳级：从 {prev_level} 级跳到 {curr_level} 级",
                    'fix': f"使用渐进的标题层级"
                })
        
        # 检查代码块闭合
        code_block_starts = []
        for i, line in enumerate(lines, 1):
            if line.strip().startswith('```'):
                if code_block_starts and code_block_starts[-1] is not None:
                    # 找到闭合
                    code_block_starts[-1] = None
                else:
                    # 新的代码块开始
                    code_block_starts.append(i)
        
        # 检查未闭合的代码块
        for start_line in code_block_starts:
            if start_line is not None:
                issues.append({
                    'type': 'code_block',
                    'severity': 'error',
                    'file': file_path,
                    'line': start_line,
                    'message': "代码块未正确闭合",
                    'fix': "在代码块末尾添加 ```"
                })
        
        # 检查图片引用
        for i, line in enumerate(lines, 1):
            img_matches = re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', line)
            for alt_text, img_path in img_matches:
                if not alt_text.strip():
                    issues.append({
                        'type': 'image_alt',
                        'severity': 'warning',
                        'file': file_path,
                        'line': i,
                        'message': "图片缺少alt文本",
                        'fix': f"为图片添加描述性alt文本"
                    })
                
                # 检查图片文件是否存在
                if not img_path.startswith('http'):
                    full_img_path = os.path.join(os.path.dirname(file_path), img_path)
                    if not os.path.exists(full_img_path):
                        issues.append({
                            'type': 'missing_image',
                            'severity': 'error',
                            'file': file_path,
                            'line': i,
                            'message': f"图片文件不存在: {img_path}",
                            'fix': f"检查图片路径或添加缺失的图片文件"
                        })
        
        return issues
    
    def check_code_quality(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """检查代码质量"""
        issues = []
        
        # 提取所有代码块
        code_blocks = re.findall(r'```(\w+)?\n(.*?)```', content, re.DOTALL)
        
        for i, (language, code) in enumerate(code_blocks):
            line_num = content[:content.find(code)].count('\n') + 1
            
            # 检查代码块是否有语言标识
            if not language:
                issues.append({
                    'type': 'code_language',
                    'severity': 'warning',
                    'file': file_path,
                    'line': line_num,
                    'message': "代码块缺少语言标识",
                    'fix': "在 ``` 后添加语言标识，如：```python"
                })
            else:
                # 检查语言标识是否正确
                if language.lower() in self.standards['code_style_patterns']:
                    pattern = self.standards['code_style_patterns'][language.lower()]
                    if not re.search(pattern, code, re.IGNORECASE):
                        issues.append({
                            'type': 'code_style',
                            'severity': 'info',
                            'file': file_path,
                            'line': line_num,
                            'message': f"代码可能不符合 {language} 语言特征",
                            'fix': f"检查代码是否正确标识为 {language} 语言"
                        })
            
            # 检查代码长度
            code_lines = code.strip().split('\n')
            if len(code_lines) > 50:
                issues.append({
                    'type': 'code_length',
                    'severity': 'info',
                    'file': file_path,
                    'line': line_num,
                    'message': f"代码块过长 ({len(code_lines)} 行)，建议拆分",
                    'fix': "将长代码块拆分为多个小的代码块"
                })
            
            # 检查代码是否有注释
            if language and language.lower() in ['python', 'java', 'csharp', 'javascript']:
                comment_patterns = {
                    'python': r'#.*',
                    'java': r'//.*|/\*.*?\*/',
                    'csharp': r'//.*|/\*.*?\*/',
                    'javascript': r'//.*|/\*.*?\*/'
                }
                
                pattern = comment_patterns.get(language.lower())
                if pattern and len(code_lines) > 10 and not re.search(pattern, code, re.DOTALL):
                    issues.append({
                        'type': 'code_comments',
                        'severity': 'info',
                        'file': file_path,
                        'line': line_num,
                        'message': "代码块建议添加注释说明",
                        'fix': "在关键代码行添加注释"
                    })
        
        return issues
    
    def check_content_structure(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """检查内容结构"""
        issues = []
        
        # 统计字数
        word_count = len(re.findall(r'\S+', content))
        
        # 检查章节是否过短
        if '第' in os.path.basename(file_path) and '章' in os.path.basename(file_path):
            if word_count < self.standards['min_chapter_words']:
                issues.append({
                    'type': 'content_length',
                    'severity': 'warning',
                    'file': file_path,
                    'message': f"章节内容过短 ({word_count} 字)，建议不少于 {self.standards['min_chapter_words']} 字",
                    'fix': "增加更多的理论阐述、实例分析或实践练习"
                })
        
        # 检查必需的章节结构
        for required_section in self.standards['required_sections']:
            if required_section not in content:
                issues.append({
                    'type': 'missing_section',
                    'severity': 'warning',
                    'file': file_path,
                    'message': f"缺少推荐的章节: {required_section}",
                    'fix': f"添加 {required_section} 章节"
                })
        
        # 检查行长度
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if len(line) > self.standards['max_line_length'] and not line.strip().startswith('```'):
                issues.append({
                    'type': 'line_length',
                    'severity': 'info',
                    'file': file_path,
                    'line': i,
                    'message': f"行过长 ({len(line)} 字符)，建议不超过 {self.standards['max_line_length']} 字符",
                    'fix': "将长行拆分为多行"
                })
        
        return issues
    
    def update_statistics(self, content: str, file_path: str):
        """更新统计信息"""
        self.statistics['total_files'] += 1
        self.statistics['total_lines'] += len(content.split('\n'))
        self.statistics['total_words'] += len(re.findall(r'\S+', content))
        
        # 统计各种元素
        self.statistics['code_blocks'] += len(re.findall(r'```.*?```', content, re.DOTALL))
        self.statistics['images'] += len(re.findall(r'!\[.*?\]\(.*?\)', content))
        self.statistics['tables'] += len(re.findall(r'\|.*?\|', content))
        
        # 统计标题
        headers = re.findall(r'^#+\s+(.+)$', content, re.MULTILINE)
        for header in headers:
            if re.search(r'第\w+章', header):
                self.statistics['chapters'] += 1
            elif re.search(r'\d+\.\d+', header):
                self.statistics['sections'] += 1
    
    def check_file(self, file_path: str) -> List[Dict[str, Any]]:
        """检查单个文件"""
        file_issues = []
        
        # 检查文件编码
        encoding_result = self.check_file_encoding(file_path)
        if encoding_result['issue']:
            file_issues.append(encoding_result['issue'])
        
        # 读取文件内容
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # 尝试其他编码
            try:
                with open(file_path, 'r', encoding='gbk') as f:
                    content = f.read()
                file_issues.append({
                    'type': 'encoding',
                    'severity': 'warning',
                    'file': file_path,
                    'message': "文件使用GBK编码，建议转换为UTF-8",
                    'fix': "使用文本编辑器将文件保存为UTF-8编码"
                })
            except Exception as e:
                file_issues.append({
                    'type': 'file_read',
                    'severity': 'error',
                    'file': file_path,
                    'message': f"无法读取文件: {e}",
                    'fix': "检查文件编码或权限"
                })
                return file_issues
        
        # 更新统计信息
        self.update_statistics(content, file_path)
        
        # 各项质量检查
        file_issues.extend(self.check_markdown_syntax(content, file_path))
        file_issues.extend(self.check_code_quality(content, file_path))
        file_issues.extend(self.check_content_structure(content, file_path))
        
        return file_issues
    
    def check_directory(self, directory: str) -> Dict[str, Any]:
        """检查整个目录"""
        print(f"开始检查目录: {directory}")
        
        # 查找所有Markdown文件
        md_files = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.lower().endswith('.md'):
                    md_files.append(os.path.join(root, file))
        
        print(f"找到 {len(md_files)} 个Markdown文件")
        
        # 检查每个文件
        all_issues = []
        for md_file in md_files:
            print(f"检查文件: {os.path.relpath(md_file, directory)}")
            file_issues = self.check_file(md_file)
            all_issues.extend(file_issues)
        
        # 分类问题
        issues_by_type = {}
        issues_by_severity = {'error': [], 'warning': [], 'info': []}
        
        for issue in all_issues:
            issue_type = issue['type']
            severity = issue['severity']
            
            if issue_type not in issues_by_type:
                issues_by_type[issue_type] = []
            issues_by_type[issue_type].append(issue)
            issues_by_severity[severity].append(issue)
        
        return {
            'total_issues': len(all_issues),
            'issues_by_type': issues_by_type,
            'issues_by_severity': issues_by_severity,
            'statistics': self.statistics,
            'files_checked': len(md_files)
        }
    
    def generate_report(self, results: Dict[str, Any], output_file: str = None):
        """生成检查报告"""
        report = []
        
        report.append("教材质量检查报告")
        report.append("=" * 50)
        report.append("")
        
        # 总体统计
        report.append("总体统计:")
        stats = results['statistics']
        report.append(f"  检查文件数: {results['files_checked']}")
        report.append(f"  总行数: {stats['total_lines']:,}")
        report.append(f"  总字数: {stats['total_words']:,}")
        report.append(f"  章节数: {stats['chapters']}")
        report.append(f"  小节数: {stats['sections']}")
        report.append(f"  代码块数: {stats['code_blocks']}")
        report.append(f"  图片数: {stats['images']}")
        report.append(f"  表格数: {stats['tables']}")
        report.append("")
        
        # 问题统计
        report.append("问题统计:")
        report.append(f"  总问题数: {results['total_issues']}")
        
        severity_stats = results['issues_by_severity']
        report.append(f"  错误: {len(severity_stats['error'])}")
        report.append(f"  警告: {len(severity_stats['warning'])}")
        report.append(f"  信息: {len(severity_stats['info'])}")
        report.append("")
        
        # 问题类型分布
        report.append("问题类型分布:")
        for issue_type, issues in results['issues_by_type'].items():
            report.append(f"  {issue_type}: {len(issues)}")
        report.append("")
        
        # 详细问题列表
        if results['total_issues'] > 0:
            report.append("详细问题列表:")
            report.append("-" * 50)
            
            for severity in ['error', 'warning', 'info']:
                if severity_stats[severity]:
                    report.append(f"\n{severity.upper()} ({len(severity_stats[severity])}):")
                    
                    for issue in severity_stats[severity]:
                        report.append(f"  文件: {issue['file']}")
                        if 'line' in issue:
                            report.append(f"  行号: {issue['line']}")
                        report.append(f"  问题: {issue['message']}")
                        report.append(f"  修复: {issue['fix']}")
                        report.append("")
        
        # 改进建议
        report.append("改进建议:")
        report.append("-" * 30)
        
        if len(severity_stats['error']) > 0:
            report.append("1. 优先修复所有错误级别的问题")
        
        if len(severity_stats['warning']) > 0:
            report.append("2. 关注警告级别的问题，特别是编码和结构问题")
        
        common_issues = sorted(results['issues_by_type'].items(), 
                             key=lambda x: len(x[1]), reverse=True)[:3]
        
        if common_issues:
            report.append("3. 最常见的问题类型:")
            for issue_type, issues in common_issues:
                report.append(f"   - {issue_type}: {len(issues)} 个")
        
        # 质量评分
        total_possible_issues = stats['total_lines'] + stats['code_blocks'] + stats['chapters']
        if total_possible_issues > 0:
            quality_score = max(0, 100 - (results['total_issues'] / total_possible_issues * 100))
            report.append(f"\n质量评分: {quality_score:.1f}/100")
            
            if quality_score >= 90:
                report.append("评级: 优秀")
            elif quality_score >= 80:
                report.append("评级: 良好")
            elif quality_score >= 70:
                report.append("评级: 及格")
            else:
                report.append("评级: 需要改进")
        
        report_text = "\n".join(report)
        
        # 输出报告
        print(report_text)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_text)
            print(f"\n报告已保存到: {output_file}")
        
        return report_text


def main():
    parser = argparse.ArgumentParser(description='教材质量自动检查工具')
    parser.add_argument('directory', help='要检查的目录')
    parser.add_argument('-o', '--output', help='输出报告文件')
    parser.add_argument('--json', help='输出JSON格式报告')
    
    args = parser.parse_args()
    
    # 检查目录是否存在
    if not os.path.exists(args.directory):
        print(f"错误：目录不存在: {args.directory}")
        return 1
    
    # 创建检查器并执行检查
    checker = TextbookQualityChecker()
    results = checker.check_directory(args.directory)
    
    # 生成报告
    checker.generate_report(results, args.output)
    
    # 输出JSON格式报告
    if args.json:
        with open(args.json, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"JSON报告已保存到: {args.json}")
    
    # 返回退出码
    error_count = len(results['issues_by_severity']['error'])
    return 1 if error_count > 0 else 0


if __name__ == '__main__':
    exit(main())
