# MD2LaTeX转换器 v2.0

专业的Markdown到LaTeX/PDF转换工具，专为《智慧水利平台架构与开发》教材设计。

## 🚀 快速开始

### 安装依赖
```bash
# 确保已安装
- Python 3.7+
- Pandoc 2.0+  
- XeLaTeX (TeX Live或MiKTeX)
- Microsoft YaHei字体
```

### 基本使用
```bash
# 转换完整文档
python3 md2latex_converter.py

# 转换单个章节
python3 md2latex_converter.py --chapter 1

# 生成PDF
python3 md2latex_converter.py --pdf

# 验证环境
python3 md2latex_converter.py --validate
```

## 📁 输出结构
```
output/
├── main.tex                   # 主LaTeX文件
├── main.pdf                   # 生成的PDF
├── chapters/                  # 章节文件
│   ├── preface.tex           # 前言
│   ├── chapter01.tex         # 第1章
│   └── ...                   # 其他章节
└── images/                    # 图片资源
```

## 🧪 运行测试
```bash
python3 test_converter.py
```

## 📚 文档
- [需求分析文档](需求分析文档.md)
- [系统设计文档](系统设计文档.md) 
- [项目完成报告](项目完成报告.md)

## ✨ 主要特性
- ✅ 模块化架构，易于维护和扩展
- ✅ 支持数学公式、代码块、图片、表格
- ✅ 完整的中文LaTeX支持
- ✅ 智能错误处理和日志记录
- ✅ 100%测试覆盖率

---
**版本**: v2.0  
**状态**: 稳定发布  
**测试**: ✅ 全部通过