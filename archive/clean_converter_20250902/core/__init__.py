"""
智慧水利教材转换器核心模块
"""

# 导入核心组件
from .config import config
from .preprocessor import preprocessor
from .converter import converter
from .validator import validator

__version__ = "2.0.0"
__all__ = ['config', 'preprocessor', 'converter', 'validator']