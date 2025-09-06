#!/usr/bin/env python3
"""
MD2LaTeX转换器 v2.0
重构版本 - 使用模块化架构

使用方法:
    python md2latex_converter.py                 # 转换完整文档
    python md2latex_converter.py --chapter 1     # 转换单个章节
    python md2latex_converter.py --preface       # 只转换前言
    python md2latex_converter.py --pdf           # 生成PDF
    python md2latex_converter.py --validate      # 验证环境
"""

import sys
import argparse
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.converter import ConverterApplication, ConversionResult
from src.core.config import ConfigManager
from src.utils.logger import Logger, enable_debug_mode

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="MD2LaTeX转换器 - Markdown到LaTeX/PDF转换工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    %(prog)s                    # 转换完整文档
    %(prog)s --chapter 1        # 转换第1章
    %(prog)s --preface          # 转换前言
    %(prog)s --pdf              # 生成PDF
    %(prog)s --validate         # 验证环境
    %(prog)s --debug            # 启用调试模式
        """
    )
    
    # 操作选项
    parser.add_argument('--chapter', type=int, metavar='N',
                       help='转换指定章节 (1-9)')
    parser.add_argument('--preface', action='store_true',
                       help='只转换前言')
    parser.add_argument('--pdf', action='store_true',
                       help='生成PDF文件')
    parser.add_argument('--validate', action='store_true',
                       help='验证运行环境')
    
    # 配置选项
    parser.add_argument('--config', metavar='FILE',
                       help='指定配置文件路径')
    parser.add_argument('--output-dir', metavar='DIR',
                       help='指定输出目录')
    
    # 调试选项
    parser.add_argument('--debug', action='store_true',
                       help='启用调试模式')
    parser.add_argument('--status', action='store_true',
                       help='显示转换器状态')
    parser.add_argument('--clean', action='store_true',
                       help='清理临时文件')
    
    return parser.parse_args()

def print_result(result: ConversionResult, logger: Logger):
    """打印转换结果"""
    if result.success:
        logger.info(f"✅ {result.message}")
        if result.output_files:
            logger.info(f"输出文件:")
            for file in result.output_files:
                logger.info(f"  - {file}")
        if result.execution_time > 0:
            logger.info(f"耗时: {result.execution_time:.2f}秒")
    else:
        logger.error(f"❌ {result.message}")
        if result.errors:
            logger.error("错误详情:")
            for error in result.errors:
                logger.error(f"  - {error}")
    
    if result.warnings:
        logger.warning("警告:")
        for warning in result.warnings:
            logger.warning(f"  - {warning}")

def main():
    """主函数"""
    args = parse_arguments()
    
    # 启用调试模式
    if args.debug:
        enable_debug_mode()
    
    logger = Logger("Main")
    logger.info("MD2LaTeX转换器 v2.0 启动")
    
    try:
        # 初始化转换器
        app = ConverterApplication(args.config)
        
        # 更新配置（如果有命令行参数）
        if args.output_dir:
            app.config.output_dir = args.output_dir
            app.path_manager = app.path_manager.__class__(app.config)
        
        # 验证环境
        if args.validate:
            logger.info("验证运行环境...")
            result = app.validate_environment()
            print_result(result, logger)
            return 0 if result.success else 1
        
        # 显示状态
        if args.status:
            status = app.get_status()
            logger.info("转换器状态:")
            for key, value in status.items():
                logger.info(f"  {key}: {value}")
            return 0
        
        # 清理临时文件
        if args.clean:
            app.cleanup_temp_files()
            logger.info("临时文件清理完成")
            return 0
        
        # 执行转换操作
        if args.preface:
            # 只转换前言
            logger.info("开始转换前言...")
            result = app.convert_preface()
            print_result(result, logger)
            return 0 if result.success else 1
        
        elif args.chapter:
            # 转换单个章节
            if not (1 <= args.chapter <= 9):
                logger.error("章节编号必须在1-9之间")
                return 1
            
            logger.info(f"开始转换第{args.chapter}章...")
            result = app.convert_single_chapter(args.chapter)
            print_result(result, logger)
            return 0 if result.success else 1
        
        elif args.pdf:
            # 生成PDF
            logger.info("开始生成PDF...")
            result = app.generate_pdf()
            print_result(result, logger)
            return 0 if result.success else 1
        
        else:
            # 转换完整文档
            logger.info("开始转换完整文档...")
            
            # 首先验证环境
            env_result = app.validate_environment()
            if not env_result.success:
                logger.error("环境验证失败，无法继续转换")
                print_result(env_result, logger)
                return 1
            
            # 执行完整转换
            result = app.convert_full_document()
            print_result(result, logger)
            
            # 如果转换成功，询问是否生成PDF
            if result.success:
                try:
                    response = input("\\n转换完成！是否生成PDF？(y/N): ").strip().lower()
                    if response in ['y', 'yes']:
                        logger.info("开始生成PDF...")
                        pdf_result = app.generate_pdf()
                        print_result(pdf_result, logger)
                        return 0 if pdf_result.success else 1
                except KeyboardInterrupt:
                    logger.info("用户取消操作")
                    return 0
            
            return 0 if result.success else 1
    
    except KeyboardInterrupt:
        logger.info("用户中断操作")
        return 1
    except Exception as e:
        logger.error(f"程序执行失败: {str(e)}")
        if args.debug:
            logger.exception("详细错误信息:")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)