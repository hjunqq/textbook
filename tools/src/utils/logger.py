"""
日志管理模块
提供统一的日志记录功能
"""

import logging
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

class Logger:
    """统一的日志管理器"""
    
    _loggers: Dict[str, logging.Logger] = {}
    _configured = False
    
    def __init__(self, name: str, level: str = "INFO"):
        self.name = name
        self.level = level
        
        # 配置日志系统（只配置一次）
        if not Logger._configured:
            self._setup_logging()
            Logger._configured = True
        
        # 获取或创建logger
        if name not in Logger._loggers:
            Logger._loggers[name] = self._create_logger(name)
        
        self._logger = Logger._loggers[name]
    
    def _setup_logging(self):
        """设置全局日志配置"""
        # 创建logs目录
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # 设置日志格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 设置根日志器
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        
        # 清除现有的处理器
        root_logger.handlers.clear()
        
        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
        
        # 文件处理器 - 所有日志
        file_handler = logging.FileHandler(
            log_dir / f"converter_{datetime.now().strftime('%Y%m%d')}.log",
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
        
        # 错误日志文件处理器
        error_handler = logging.FileHandler(
            log_dir / f"errors_{datetime.now().strftime('%Y%m%d')}.log",
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        root_logger.addHandler(error_handler)
    
    def _create_logger(self, name: str) -> logging.Logger:
        """创建指定名称的logger"""
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, self.level.upper()))
        return logger
    
    def debug(self, message: str, *args, **kwargs):
        """记录调试信息"""
        self._logger.debug(message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs):
        """记录信息"""
        self._logger.info(message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        """记录警告"""
        self._logger.warning(message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        """记录错误"""
        self._logger.error(message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs):
        """记录严重错误"""
        self._logger.critical(message, *args, **kwargs)
    
    def exception(self, message: str, *args, **kwargs):
        """记录异常信息（包含堆栈跟踪）"""
        self._logger.exception(message, *args, **kwargs)

class ConversionLogger:
    """转换过程专用日志记录器"""
    
    def __init__(self):
        self.logger = Logger("ConversionProcess")
        self.start_time = None
        self.stats = {
            'chapters_processed': 0,
            'images_processed': 0,
            'code_blocks_processed': 0,
            'math_formulas_processed': 0,
            'errors': 0,
            'warnings': 0
        }
    
    def start_conversion(self, document_name: str):
        """开始转换日志"""
        self.start_time = datetime.now()
        self.logger.info(f"=" * 60)
        self.logger.info(f"开始转换文档: {document_name}")
        self.logger.info(f"开始时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info(f"=" * 60)
    
    def log_chapter_start(self, chapter_num: int, chapter_title: str):
        """记录章节开始"""
        self.logger.info(f"开始处理第{chapter_num}章: {chapter_title}")
    
    def log_chapter_complete(self, chapter_num: int, processing_time: float):
        """记录章节完成"""
        self.stats['chapters_processed'] += 1
        self.logger.info(f"第{chapter_num}章处理完成，耗时: {processing_time:.2f}秒")
    
    def log_processing_stats(self, processor_name: str, count: int):
        """记录处理统计"""
        if processor_name == "Image":
            self.stats['images_processed'] += count
        elif processor_name == "CodeBlock":
            self.stats['code_blocks_processed'] += count
        elif processor_name == "Math":
            self.stats['math_formulas_processed'] += count
        
        if count > 0:
            self.logger.info(f"{processor_name}处理器: 处理了 {count} 项")
    
    def log_error(self, error_msg: str):
        """记录错误"""
        self.stats['errors'] += 1
        self.logger.error(error_msg)
    
    def log_warning(self, warning_msg: str):
        """记录警告"""
        self.stats['warnings'] += 1
        self.logger.warning(warning_msg)
    
    def finish_conversion(self, success: bool, output_files: int):
        """结束转换日志"""
        end_time = datetime.now()
        total_time = end_time - self.start_time if self.start_time else 0
        
        self.logger.info(f"=" * 60)
        self.logger.info(f"转换完成: {'成功' if success else '失败'}")
        self.logger.info(f"结束时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info(f"总耗时: {total_time.total_seconds():.2f}秒")
        self.logger.info(f"输出文件: {output_files} 个")
        self.logger.info("处理统计:")
        self.logger.info(f"  - 章节: {self.stats['chapters_processed']}")
        self.logger.info(f"  - 图片: {self.stats['images_processed']}")
        self.logger.info(f"  - 代码块: {self.stats['code_blocks_processed']}")
        self.logger.info(f"  - 数学公式: {self.stats['math_formulas_processed']}")
        self.logger.info(f"  - 错误: {self.stats['errors']}")
        self.logger.info(f"  - 警告: {self.stats['warnings']}")
        self.logger.info(f"=" * 60)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return self.stats.copy()

class PerformanceLogger:
    """性能监控日志记录器"""
    
    def __init__(self):
        self.logger = Logger("Performance")
        self.timers = {}
    
    def start_timer(self, name: str):
        """开始计时"""
        self.timers[name] = datetime.now()
        self.logger.debug(f"开始计时: {name}")
    
    def end_timer(self, name: str) -> float:
        """结束计时并返回耗时"""
        if name not in self.timers:
            self.logger.warning(f"计时器 '{name}' 未启动")
            return 0.0
        
        start_time = self.timers[name]
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        del self.timers[name]
        
        self.logger.info(f"{name}: {duration:.3f}秒")
        return duration
    
    def log_memory_usage(self):
        """记录内存使用情况"""
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            
            self.logger.info(f"内存使用: {memory_info.rss / 1024 / 1024:.1f}MB")
            
        except ImportError:
            self.logger.debug("psutil未安装，无法监控内存使用")
        except Exception as e:
            self.logger.warning(f"获取内存信息失败: {e}")
    
    def log_file_sizes(self, files: list):
        """记录文件大小信息"""
        total_size = 0
        for file_path in files:
            if Path(file_path).exists():
                size = Path(file_path).stat().st_size
                total_size += size
                self.logger.debug(f"文件大小: {Path(file_path).name} - {size / 1024:.1f}KB")
        
        self.logger.info(f"总文件大小: {total_size / 1024 / 1024:.1f}MB")

class DebugLogger:
    """调试专用日志记录器"""
    
    def __init__(self, enabled: bool = False):
        self.logger = Logger("Debug")
        self.enabled = enabled
    
    def enable(self):
        """启用调试日志"""
        self.enabled = True
        self.logger.info("调试模式已启用")
    
    def disable(self):
        """禁用调试日志"""
        self.enabled = False
    
    def log_content_sample(self, title: str, content: str, max_length: int = 200):
        """记录内容样本"""
        if not self.enabled:
            return
        
        sample = content[:max_length] + "..." if len(content) > max_length else content
        self.logger.debug(f"{title} (前{min(len(content), max_length)}字符):")
        self.logger.debug(f"'{sample}'")
    
    def log_regex_match(self, pattern: str, content: str, matches: list):
        """记录正则表达式匹配结果"""
        if not self.enabled:
            return
        
        self.logger.debug(f"正则匹配: {pattern}")
        self.logger.debug(f"匹配数量: {len(matches)}")
        if matches:
            self.logger.debug(f"匹配样本: {matches[:3]}")  # 只显示前3个
    
    def log_processing_step(self, step_name: str, input_length: int, output_length: int):
        """记录处理步骤"""
        if not self.enabled:
            return
        
        change = output_length - input_length
        self.logger.debug(f"处理步骤: {step_name}")
        self.logger.debug(f"  输入长度: {input_length}")
        self.logger.debug(f"  输出长度: {output_length}")
        self.logger.debug(f"  变化: {'+' if change >= 0 else ''}{change}")

# 全局调试标志
DEBUG_MODE = False

def enable_debug_mode():
    """启用全局调试模式"""
    global DEBUG_MODE
    DEBUG_MODE = True
    
    # 设置所有logger为DEBUG级别
    logging.getLogger().setLevel(logging.DEBUG)
    
    logger = Logger("System")
    logger.info("全局调试模式已启用")

def disable_debug_mode():
    """禁用全局调试模式"""
    global DEBUG_MODE
    DEBUG_MODE = False
    
    # 恢复INFO级别
    logging.getLogger().setLevel(logging.INFO)
    
    logger = Logger("System") 
    logger.info("全局调试模式已禁用")