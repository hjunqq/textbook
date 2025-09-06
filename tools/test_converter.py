#!/usr/bin/env python3
"""
MD2LaTeX转换器测试脚本
用于测试重构后的转换器功能
"""

import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.converter import ConverterApplication
from src.core.config import ConverterConfig
from src.utils.logger import Logger, enable_debug_mode

def test_basic_functionality():
    """测试基本功能"""
    logger = Logger("Test")
    logger.info("开始基本功能测试...")
    
    try:
        # 创建转换器实例
        app = ConverterApplication()
        
        # 测试环境验证
        logger.info("1. 测试环境验证...")
        env_result = app.validate_environment()
        logger.info(f"   环境验证结果: {'通过' if env_result.success else '失败'}")
        
        # 测试状态获取
        logger.info("2. 测试状态获取...")
        status = app.get_status()
        logger.info(f"   转换器已初始化: {status.get('initialized', False)}")
        logger.info(f"   配置有效: {status.get('config_valid', False)}")
        logger.info(f"   输出目录存在: {status.get('output_dir_exists', False)}")
        
        # 测试配置管理
        logger.info("3. 测试配置管理...")
        config_errors = app.config.validate()
        logger.info(f"   配置验证错误数: {len(config_errors)}")
        if config_errors:
            for error in config_errors[:3]:  # 只显示前3个错误
                logger.info(f"   - {error}")
        
        logger.info("基本功能测试完成")
        return True
        
    except Exception as e:
        logger.error(f"基本功能测试失败: {e}")
        return False

def test_content_processors():
    """测试内容处理器"""
    logger = Logger("TestProcessors")
    logger.info("开始内容处理器测试...")
    
    try:
        from src.processors.content_processor import (
            MathProcessor, CodeBlockProcessor, ImageProcessor, 
            ChapterNumberProcessor, AdmonitionProcessor
        )
        
        # 测试数学公式处理器
        logger.info("1. 测试数学公式处理器...")
        math_processor = MathProcessor()
        test_math_content = "这是一个数学公式: $$E = mc^2$$ 和行内公式 $x^2$"
        result = math_processor.process(test_math_content)
        logger.info(f"   处理结果包含equation环境: {'equation' in result}")
        
        # 测试代码块处理器
        logger.info("2. 测试代码块处理器...")
        code_processor = CodeBlockProcessor()
        test_code_content = """```python
def hello():
    print("Hello World")
```"""
        result = code_processor.process(test_code_content)
        logger.info(f"   处理结果包含lstlisting: {'lstlisting' in result}")
        
        # 测试章节编号处理器
        logger.info("3. 测试章节编号处理器...")
        chapter_processor = ChapterNumberProcessor()
        test_chapter_content = "# 第一章 测试章节\n\n## 测试小节"
        result = chapter_processor.process(test_chapter_content)
        logger.info(f"   处理结果包含chapter命令: {'chapter' in result}")
        
        logger.info("内容处理器测试完成")
        return True
        
    except Exception as e:
        logger.error(f"内容处理器测试失败: {e}")
        return False

def test_template_engine():
    """测试模板引擎"""
    logger = Logger("TestTemplate")
    logger.info("开始模板引擎测试...")
    
    try:
        from src.templates.template_engine import TemplateEngine
        from src.core.config import DEFAULT_CONFIG
        
        # 创建模板引擎
        template_engine = TemplateEngine(DEFAULT_CONFIG)
        
        # 测试主模板渲染
        logger.info("1. 测试主模板渲染...")
        chapter_files = [
            ("preface", "前言"),
            ("chapter01", "第一章 测试章节")
        ]
        main_content = template_engine.render_main_template(chapter_files)
        logger.info(f"   主模板长度: {len(main_content)} 字符")
        logger.info(f"   包含documentclass: {'documentclass' in main_content}")
        
        # 测试章节模板渲染
        logger.info("2. 测试章节模板渲染...")
        chapter_content = template_engine.render_chapter_template(
            1, "第一章 测试", "这是测试内容"
        )
        logger.info(f"   章节模板包含测试内容: {'测试内容' in chapter_content}")
        
        logger.info("模板引擎测试完成")
        return True
        
    except Exception as e:
        logger.error(f"模板引擎测试失败: {e}")
        return False

def test_file_operations():
    """测试文件操作"""
    logger = Logger("TestFile")
    logger.info("开始文件操作测试...")
    
    try:
        from src.utils.file_manager import FileManager
        
        file_manager = FileManager()
        
        # 创建测试文件
        test_dir = Path("test_output")
        test_file = test_dir / "test.txt"
        test_content = "这是测试内容\\n包含中文字符"
        
        logger.info("1. 测试文件写入...")
        file_manager.write_file(test_file, test_content)
        logger.info(f"   测试文件已创建: {test_file.exists()}")
        
        logger.info("2. 测试文件读取...")
        read_content = file_manager.read_file(test_file)
        logger.info(f"   读取内容正确: {read_content == test_content}")
        
        # 清理测试文件
        logger.info("3. 清理测试文件...")
        file_manager.delete_file(test_file)
        if test_dir.exists() and not list(test_dir.iterdir()):
            test_dir.rmdir()
        
        logger.info("文件操作测试完成")
        return True
        
    except Exception as e:
        logger.error(f"文件操作测试失败: {e}")
        return False

def main():
    """主测试函数"""
    logger = Logger("MainTest")
    logger.info("=" * 60)
    logger.info("MD2LaTeX转换器 v2.0 测试套件")
    logger.info("=" * 60)
    
    # 启用调试模式
    enable_debug_mode()
    
    test_results = []
    
    # 执行各项测试
    tests = [
        ("基本功能测试", test_basic_functionality),
        ("内容处理器测试", test_content_processors),
        ("模板引擎测试", test_template_engine),
        ("文件操作测试", test_file_operations)
    ]
    
    for test_name, test_func in tests:
        logger.info(f"\\n开始 {test_name}...")
        try:
            result = test_func()
            test_results.append((test_name, result))
            status = "通过" if result else "失败"
            logger.info(f"{test_name}: {status}")
        except Exception as e:
            test_results.append((test_name, False))
            logger.error(f"{test_name}: 异常 - {e}")
    
    # 汇总结果
    logger.info("\\n" + "=" * 60)
    logger.info("测试结果汇总:")
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        logger.info(f"  {test_name}: {status}")
    
    logger.info(f"\\n总计: {passed}/{total} 个测试通过")
    logger.info("=" * 60)
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)