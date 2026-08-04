#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智慧水利教材转换器 - 测试套件
Test Suite for Textbook Converter

包含单元测试、集成测试、性能测试等
"""

import unittest
import tempfile
import shutil
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from textbook_converter import (
    TextbookConverter, ConversionConfig, Logger, SystemChecker,
    ContentProcessor, QualityAssurance, PandocConverter,
    OutputFormat, ConversionStatus, QualityLevel, ProgressTracker
)

class TestConversionConfig(unittest.TestCase):
    """测试转换配置"""
    
    def test_config_creation(self):
        """测试配置创建"""
        config = ConversionConfig(
            input_dir="/test/input",
            output_dir="/test/output",
            output_format="pdf"
        )
        
        self.assertEqual(config.input_dir, "/test/input")
        self.assertEqual(config.output_dir, "/test/output")
        self.assertEqual(config.output_format, "pdf")
        self.assertTrue(config.include_toc)
        self.assertTrue(config.number_sections)
        self.assertTrue(config.quality_check)
    
    def test_config_to_dict(self):
        """测试配置转字典"""
        config = ConversionConfig(
            input_dir="/test/input",
            output_dir="/test/output",
            chapters=["chapter01", "chapter02"]
        )
        
        config_dict = config.to_dict()
        self.assertIsInstance(config_dict, dict)
        self.assertIn("input_dir", config_dict)
        self.assertIn("chapters", config_dict)
        self.assertEqual(config_dict["chapters"], ["chapter01", "chapter02"])

class TestLogger(unittest.TestCase):
    """测试日志记录器"""
    
    def setUp(self):
        """设置测试环境"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.log_file = self.temp_dir / "test.log"
    
    def tearDown(self):
        """清理测试环境"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_logger_creation(self):
        """测试日志器创建"""
        logger = Logger(log_file=str(self.log_file), verbose=True)
        self.assertIsNotNone(logger.logger)
        self.assertTrue(logger.verbose)
        self.assertEqual(logger.log_file, str(self.log_file))
    
    def test_logger_methods(self):
        """测试日志方法"""
        logger = Logger()
        
        # 这些方法不应该抛出异常
        logger.info("Test info message")
        logger.warning("Test warning message")
        logger.error("Test error message")
        logger.success("Test success message")
        logger.debug("Test debug message")

class TestProgressTracker(unittest.TestCase):
    """测试进度跟踪器"""
    
    def test_progress_initialization(self):
        """测试进度初始化"""
        tracker = ProgressTracker(total_steps=10)
        self.assertEqual(tracker.total_steps, 10)
        self.assertEqual(tracker.current_step, 0)
    
    def test_progress_update(self):
        """测试进度更新"""
        tracker = ProgressTracker(total_steps=5)
        tracker.update(2, "Test step")
        
        progress = tracker.get_progress()
        self.assertEqual(progress['current_step'], 2)
        self.assertEqual(progress['percentage'], 40.0)
        self.assertFalse(progress['is_complete'])
    
    def test_progress_completion(self):
        """测试进度完成"""
        tracker = ProgressTracker(total_steps=3)
        tracker.update(3, "Final step")
        
        progress = tracker.get_progress()
        self.assertTrue(progress['is_complete'])

class TestSystemChecker(unittest.TestCase):
    """测试系统检查器"""
    
    def setUp(self):
        """设置测试环境"""
        self.logger = Logger()
        self.checker = SystemChecker(self.logger)
    
    @patch('subprocess.run')
    def test_check_command_success(self, mock_run):
        """测试命令检查成功"""
        mock_run.return_value.returncode = 0
        result = self.checker._check_command('pandoc')
        self.assertTrue(result)
    
    @patch('subprocess.run')
    def test_check_command_failure(self, mock_run):
        """测试命令检查失败"""
        mock_run.side_effect = FileNotFoundError()
        result = self.checker._check_command('nonexistent')
        self.assertFalse(result)

class TestContentProcessor(unittest.TestCase):
    """测试内容处理器"""
    
    def setUp(self):
        """设置测试环境"""
        self.logger = Logger()
        self.processor = ContentProcessor(self.logger)
        self.temp_dir = Path(tempfile.mkdtemp())
        self.output_dir = self.temp_dir / "output"
        self.output_dir.mkdir(exist_ok=True)
    
    def tearDown(self):
        """清理测试环境"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_yaml_frontmatter_removal(self):
        """测试YAML前言移除"""
        content = """---
title: Test
author: Test Author
---

# Main Content
This is the main content."""
        
        result = self.processor._remove_yaml_frontmatter(content)
        self.assertNotIn("---", result)
        self.assertIn("# Main Content", result)
    
    def test_code_language_detection(self):
        """测试代码语言检测"""
        # Python代码
        python_code = "def hello():\n    print('Hello')"
        self.assertEqual(self.processor._detect_code_language(python_code), 'python')
        
        # JavaScript代码
        js_code = "function hello() { console.log('Hello'); }"
        self.assertEqual(self.processor._detect_code_language(js_code), 'javascript')
        
        # SQL代码
        sql_code = "SELECT * FROM users WHERE id = 1"
        self.assertEqual(self.processor._detect_code_language(sql_code), 'sql')
    
    def test_heading_standardization(self):
        """测试标题标准化"""
        content = "# Original Title"
        file_path = Path("chapter01.md")
        
        result = self.processor._standardize_headings(content, file_path)
        self.assertIn("第1章", result)
    
    def test_admonition_processing(self):
        """测试提醒框处理"""
        content = """!!! warning "注意"
    这是一个警告信息"""
        
        result = self.processor._process_admonitions(content)
        self.assertIn("> **注意**", result)
        self.assertIn("> 这是一个警告信息", result)
    
    def test_statistics_tracking(self):
        """测试统计信息跟踪"""
        # 创建测试文件
        test_file = self.temp_dir / "test.md"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("# Test\n\n```python\nprint('hello')\n```\n")
        
        self.processor.process_markdown_file(test_file, self.output_dir)
        stats = self.processor.get_statistics()
        
        self.assertEqual(stats['files_processed'], 1)
        self.assertEqual(stats['code_blocks_found'], 1)

class TestQualityAssurance(unittest.TestCase):
    """测试质量保证"""
    
    def setUp(self):
        """设置测试环境"""
        self.logger = Logger()
        self.qa = QualityAssurance(self.logger)
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # 创建测试目录结构
        self.chapters_dir = self.temp_dir / "chapters"
        self.chapters_dir.mkdir(exist_ok=True)
        
        self.chapter01_dir = self.chapters_dir / "chapter01"
        self.chapter01_dir.mkdir(exist_ok=True)
    
    def tearDown(self):
        """清理测试环境"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_input_structure_validation_success(self):
        """测试输入结构验证成功"""
        result = self.qa.validate_input_structure(self.temp_dir)
        self.assertTrue(result)
    
    def test_input_structure_validation_failure(self):
        """测试输入结构验证失败"""
        nonexistent_dir = Path("/nonexistent/directory")
        result = self.qa.validate_input_structure(nonexistent_dir)
        self.assertFalse(result)
        self.assertGreater(len(self.qa.issues), 0)
    
    def test_markdown_file_validation(self):
        """测试Markdown文件验证"""
        # 创建测试文件
        test_file = self.chapter01_dir / "test.md"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("""# Title
            
## Subtitle

```python
def test():
    pass
```

![Test Image](image.png)
""")
        
        self.qa._validate_markdown_file(test_file)
        self.assertGreater(self.qa.stats['files_checked'], 0)
    
    def test_quality_level_assessment(self):
        """测试质量等级评估"""
        # 无问题情况
        quality = self.qa._get_overall_quality()
        self.assertEqual(quality, QualityLevel.EXCELLENT)
        
        # 有警告情况
        self.qa.warnings = ["Warning 1", "Warning 2", "Warning 3"]
        quality = self.qa._get_overall_quality()
        self.assertIn(quality, [QualityLevel.GOOD, QualityLevel.ACCEPTABLE])
        
        # 有问题情况
        self.qa.issues = ["Issue 1"]
        quality = self.qa._get_overall_quality()
        self.assertIn(quality, [QualityLevel.ACCEPTABLE, QualityLevel.POOR])

class TestPandocConverter(unittest.TestCase):
    """测试Pandoc转换器"""
    
    def setUp(self):
        """设置测试环境"""
        self.logger = Logger()
        self.converter = PandocConverter(self.logger)
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # 创建测试输入文件
        self.input_file = self.temp_dir / "input.md"
        with open(self.input_file, 'w', encoding='utf-8') as f:
            f.write("# Test Document\n\nThis is a test document.")
    
    def tearDown(self):
        """清理测试环境"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_template_config_exists(self):
        """测试模板配置存在"""
        self.assertIn('pdf', self.converter.conversion_templates)
        self.assertIn('latex', self.converter.conversion_templates)
        self.assertIn('html', self.converter.conversion_templates)
    
    @patch('subprocess.run')
    def test_conversion_success(self, mock_run):
        """测试转换成功"""
        mock_run.return_value.returncode = 0
        
        # 创建期望的输出文件
        output_file = self.temp_dir / "textbook.pdf"
        output_file.write_text("fake pdf content")
        
        config = ConversionConfig(
            input_dir=str(self.temp_dir),
            output_dir=str(self.temp_dir)
        )
        
        result = self.converter.convert(
            self.input_file, 'pdf', self.temp_dir, config
        )
        # Note: 在mock环境下这个测试可能需要调整
        mock_run.assert_called()

class TestTextbookConverter(unittest.TestCase):
    """测试主转换器"""
    
    def setUp(self):
        """设置测试环境"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.input_dir = self.temp_dir / "input"
        self.output_dir = self.temp_dir / "output"
        
        # 创建测试目录结构
        self.input_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        
        chapters_dir = self.input_dir / "chapters"
        chapters_dir.mkdir(exist_ok=True)
        
        chapter01_dir = chapters_dir / "chapter01"
        chapter01_dir.mkdir(exist_ok=True)
        
        # 创建测试文件
        with open(chapter01_dir / "chapter01.md", 'w', encoding='utf-8') as f:
            f.write("""# 智慧水利概述

这是第一章的内容。

## 1.1 概述

智慧水利是现代水利发展的重要方向。

```python
def hello_water():
    print("Hello, Smart Water!")
```
""")
        
        self.config = ConversionConfig(
            input_dir=str(self.input_dir),
            output_dir=str(self.output_dir),
            output_format='latex',  # 使用latex避免PDF依赖
            quality_check=False,    # 跳过复杂的质量检查
            verbose=True
        )
    
    def tearDown(self):
        """清理测试环境"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_converter_initialization(self):
        """测试转换器初始化"""
        converter = TextbookConverter(self.config)
        
        self.assertEqual(converter.status, ConversionStatus.PENDING)
        self.assertEqual(str(converter.input_dir), str(self.input_dir))
        self.assertEqual(str(converter.output_dir), str(self.output_dir))
        self.assertTrue(self.output_dir.exists())
    
    def test_source_files_discovery(self):
        """测试源文件发现"""
        converter = TextbookConverter(self.config)
        files = converter._discover_source_files()
        
        self.assertGreater(len(files), 0)
        file_types = [file_type for file_type, _ in files]
        self.assertIn('chapter', file_types)
    
    def test_content_processing(self):
        """测试内容处理"""
        converter = TextbookConverter(self.config)
        files = converter._discover_source_files()
        
        merged_content = converter._process_and_merge_files(files)
        self.assertIsInstance(merged_content, str)
        self.assertIn("智慧水利概述", merged_content)
        self.assertIn("```python", merged_content)
    
    def test_merged_file_saving(self):
        """测试合并文件保存"""
        converter = TextbookConverter(self.config)
        test_content = "# Test Content\n\nThis is test content."
        
        saved_file = converter._save_merged_content(test_content)
        self.assertIsNotNone(saved_file)
        self.assertTrue(saved_file.exists())
        
        with open(saved_file, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertEqual(content, test_content)

class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def setUp(self):
        """设置完整的测试环境"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.create_complete_test_structure()
    
    def tearDown(self):
        """清理测试环境"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_complete_test_structure(self):
        """创建完整的测试目录结构"""
        # 输入输出目录
        self.input_dir = self.temp_dir / "input"
        self.output_dir = self.temp_dir / "output"
        self.input_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        
        # 前言文件
        preface_content = """# 前言

本书介绍了智慧水利平台的架构与开发。

## 编写目的

为了帮助读者理解智慧水利系统。
"""
        with open(self.input_dir / "前言.md", 'w', encoding='utf-8') as f:
            f.write(preface_content)
        
        # 章节目录
        chapters_dir = self.input_dir / "chapters"
        chapters_dir.mkdir(exist_ok=True)
        
        # 创建两个测试章节
        for chapter_num in [1, 2]:
            chapter_key = f"chapter{chapter_num:02d}"
            chapter_dir = chapters_dir / chapter_key
            chapter_dir.mkdir(exist_ok=True)
            
            # 章节主文件
            chapter_content = f"""# 第{chapter_num}章 测试章节

这是第{chapter_num}章的内容。

## {chapter_num}.1 概述

本章介绍了相关概念。

```python
def chapter_{chapter_num}_example():
    print("This is chapter {chapter_num}")
    return True
```

![测试图片](test_image_{chapter_num}.png)

!!! info "信息"
    这是一个信息提示框。

## {chapter_num}.2 详细内容

更多的详细内容在这里。
"""
            with open(chapter_dir / f"{chapter_key}.md", 'w', encoding='utf-8') as f:
                f.write(chapter_content)
            
            # 节文件
            section_content = f"""# {chapter_num}.1 第一节

这是第{chapter_num}章第1节的内容。

### {chapter_num}.1.1 子节

子节的内容。

```javascript
function section_{chapter_num}_1() {{
    console.log("Section {chapter_num}.1");
}}
```
"""
            with open(chapter_dir / f"section{chapter_num:02d}-01.md", 'w', encoding='utf-8') as f:
                f.write(section_content)
        
        # 创建图片目录和示例图片
        images_dir = chapters_dir / "images"
        images_dir.mkdir(exist_ok=True)
        
        # 创建假的图片文件
        for i in [1, 2]:
            fake_image = images_dir / f"test_image_{i}.png"
            fake_image.write_bytes(b"fake image content")
    
    @patch('subprocess.run')
    def test_full_conversion_latex(self, mock_run):
        """测试完整的LaTeX转换流程"""
        # 模拟成功的pandoc调用
        mock_run.return_value.returncode = 0
        mock_run.return_value.stderr = ""
        mock_run.return_value.stdout = "Conversion successful"
        
        config = ConversionConfig(
            input_dir=str(self.input_dir),
            output_dir=str(self.output_dir),
            output_format='latex',
            quality_check=True,
            verbose=True
        )
        
        converter = TextbookConverter(config)
        
        # 创建预期的输出文件（模拟pandoc输出）
        expected_output = self.output_dir / "textbook.tex"
        expected_output.write_text("\\documentclass{article}\n\\begin{document}\nTest content\n\\end{document}")
        
        # 执行转换（跳过实际的pandoc调用）
        # 由于我们不能确保pandoc可用，我们测试转换流程的各个步骤
        
        # 1. 测试文件发现
        files = converter._discover_source_files()
        self.assertGreater(len(files), 0)
        
        # 2. 测试内容处理
        merged_content = converter._process_and_merge_files(files)
        self.assertIn("前言", merged_content)
        self.assertIn("第1章", merged_content)
        self.assertIn("第2章", merged_content)
        
        # 3. 测试文件保存
        merged_file = converter._save_merged_content(merged_content)
        self.assertTrue(merged_file.exists())
        
        # 验证合并内容质量
        with open(merged_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查内容完整性
        self.assertIn("# 前言", content)
        self.assertIn("def chapter_1_example", content)
        self.assertIn("def chapter_2_example", content)
        self.assertIn("function section_1_1", content)
        self.assertIn("images/img_", content)  # 图片路径被标准化

class TestPerformance(unittest.TestCase):
    """性能测试"""
    
    def setUp(self):
        """设置性能测试环境"""
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        """清理测试环境"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_large_file_processing_performance(self):
        """测试大文件处理性能"""
        logger = Logger()
        processor = ContentProcessor(logger)
        
        # 创建大文件（模拟）
        large_content = "# Test Chapter\n\n" + "This is content. " * 1000 + "\n"
        large_content += "```python\n" + "print('test')\n" * 100 + "```\n"
        
        test_file = self.temp_dir / "large_test.md"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(large_content)
        
        output_dir = self.temp_dir / "output"
        output_dir.mkdir(exist_ok=True)
        
        import time
        start_time = time.time()
        
        result = processor.process_markdown_file(test_file, output_dir)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        self.assertIsInstance(result, str)
        self.assertLess(processing_time, 5.0)  # 应该在5秒内完成
        self.assertIn("Test Chapter", result)

class TestErrorHandling(unittest.TestCase):
    """错误处理测试"""
    
    def setUp(self):
        """设置错误测试环境"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.logger = Logger()
    
    def tearDown(self):
        """清理测试环境"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_missing_input_directory(self):
        """测试输入目录不存在的错误处理"""
        config = ConversionConfig(
            input_dir="/nonexistent/directory",
            output_dir=str(self.temp_dir)
        )
        
        converter = TextbookConverter(config)
        result = converter.convert()
        
        self.assertFalse(result)
        self.assertEqual(converter.status, ConversionStatus.FAILED)
    
    def test_invalid_output_format(self):
        """测试无效输出格式的错误处理"""
        pandoc_converter = PandocConverter(self.logger)
        
        config = ConversionConfig(
            input_dir=str(self.temp_dir),
            output_dir=str(self.temp_dir)
        )
        
        test_file = self.temp_dir / "test.md"
        test_file.write_text("# Test")
        
        result = pandoc_converter.convert(
            test_file, "invalid_format", self.temp_dir, config
        )
        
        self.assertFalse(result)
    
    def test_corrupted_file_handling(self):
        """测试损坏文件的处理"""
        processor = ContentProcessor(self.logger)
        
        # 创建包含无效字符的文件
        corrupted_file = self.temp_dir / "corrupted.md"
        with open(corrupted_file, 'wb') as f:
            f.write(b'\x00\x01\x02\xff\xfe# Invalid content')
        
        output_dir = self.temp_dir / "output"
        output_dir.mkdir(exist_ok=True)
        
        result = processor.process_markdown_file(corrupted_file, output_dir)
        # 应该返回空字符串或处理后的内容，不应该崩溃
        self.assertIsInstance(result, str)

def create_test_suite():
    """创建完整的测试套件"""
    suite = unittest.TestSuite()
    
    # 基础组件测试
    suite.addTest(unittest.makeSuite(TestConversionConfig))
    suite.addTest(unittest.makeSuite(TestLogger))
    suite.addTest(unittest.makeSuite(TestProgressTracker))
    
    # 功能模块测试
    suite.addTest(unittest.makeSuite(TestSystemChecker))
    suite.addTest(unittest.makeSuite(TestContentProcessor))
    suite.addTest(unittest.makeSuite(TestQualityAssurance))
    suite.addTest(unittest.makeSuite(TestPandocConverter))
    
    # 主转换器测试
    suite.addTest(unittest.makeSuite(TestTextbookConverter))
    
    # 集成测试
    suite.addTest(unittest.makeSuite(TestIntegration))
    
    # 性能和错误处理测试
    suite.addTest(unittest.makeSuite(TestPerformance))
    suite.addTest(unittest.makeSuite(TestErrorHandling))
    
    return suite

def run_tests(verbosity=2):
    """运行所有测试"""
    print("🧪 开始运行智慧水利教材转换器测试套件")
    print("=" * 60)
    
    suite = create_test_suite()
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    print(f"🏁 测试完成")
    print(f"✅ 通过: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ 失败: {len(result.failures)}")
    print(f"💥 错误: {len(result.errors)}")
    
    if result.failures:
        print("\n🔴 失败的测试:")
        for test, traceback in result.failures:
            print(f"  - {test}")
    
    if result.errors:
        print("\n💥 错误的测试:")
        for test, traceback in result.errors:
            print(f"  - {test}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    if success:
        print("\n🎉 所有测试通过！")
    else:
        print(f"\n⚠️  有 {len(result.failures) + len(result.errors)} 个测试未通过")
    
    return success

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="运行教材转换器测试套件")
    parser.add_argument('-v', '--verbose', action='store_true', help="详细输出")
    parser.add_argument('--pattern', help="运行匹配模式的测试")
    
    args = parser.parse_args()
    
    if args.pattern:
        # 运行特定模式的测试
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromName(args.pattern)
        runner = unittest.TextTestRunner(verbosity=2 if args.verbose else 1)
        result = runner.run(suite)
    else:
        # 运行所有测试
        verbosity = 2 if args.verbose else 1
        success = run_tests(verbosity)
        exit(0 if success else 1)