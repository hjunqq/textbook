# 智慧水利教材转换器 v1.0

专业的Markdown转LaTeX/PDF转换工具，专为《智慧水利平台架构与开发》教材设计。

## ✨ 特性

- 🔄 **模块化架构**: 基于软件工程原则的组件化设计
- 📖 **章节处理**: 独立处理每个章节，生成规范的LaTeX项目结构
- 🧮 **数学公式**: 自动转换Markdown数学公式为LaTeX equation环境
- 💻 **代码高亮**: 支持多语言代码块转换为listings环境
- 🖼️ **图片处理**: 自动转换图片为LaTeX figure环境
- 📋 **告警框**: MkDocs admonition语法转换为tcolorbox
- 🌏 **中文支持**: 完整的中文LaTeX支持
- 🧪 **测试框架**: 全面的单元测试和集成测试

## 📋 系统要求

### 必需软件
- **Python 3.7+**
- **Pandoc 2.0+** - [下载地址](https://pandoc.org/installing.html)
- **LaTeX发行版** (推荐MiKTeX或TeX Live)
  - 需要XeLaTeX引擎
  - 需要中文字体支持

### Windows推荐配置
```bash
# 1. 安装Python (从python.org下载)
# 2. 安装MiKTeX (从miktex.org下载)
# 3. 安装Pandoc (从pandoc.org下载)
```

## 🚀 快速开始

### 1. 环境验证
```bash
# 在命令行中验证安装
python --version
pandoc --version  
xelatex --version
```

### 2. 运行转换器
```bash
# Windows - 完整转换流程
build_converter.bat

# 或直接运行转换器
python main_converter.py
```

### 3. 运行测试
```bash
# 单独运行测试套件
python test_framework.py

# 快速功能测试
python quick_test.py
```

## 📁 转换器文件结构

```
tools/                             # 🧹 已清理，只保留核心转换器
├── main_converter.py              # ⭐️ 主应用程序
├── converter_config.py            # ⭐️ 配置管理
├── content_processors.py          # ⭐️ 内容处理器
├── latex_templates.py             # ⭐️ LaTeX模板生成
├── test_framework.py              # ⭐️ 测试框架
├── quick_test.py                  # ⭐️ 快速测试
├── build_converter.bat            # ⭐️ Windows构建脚本
├── requirements.txt               # ⭐️ 依赖说明
├── README.md                      # 📖 本文档
├── CONVERSION_COMPLETE.md         # 📋 完成报告
└── test-config.yaml              # ⚙️ 测试配置
```

## ⚙️ 配置选项

在 `converter_config.py` 中可以配置：

```python
@dataclass
class ConverterConfig:
    source_dir: str = "../docs/chapters"        # 源文件目录
    preface_file: str = "../docs/前言.md"       # 前言文件
    output_dir: str = "output"                  # 输出目录
    
    # LaTeX设置
    documentclass: str = "book"                 # 文档类
    font_family: str = "Microsoft YaHei"       # 字体
    paper_size: str = "a4paper"                # 纸张大小
    font_size: str = "12pt"                    # 字体大小
    
    # 处理选项
    enable_math_processing: bool = True         # 数学公式处理
    enable_figure_processing: bool = True       # 图片处理
    enable_code_processing: bool = True         # 代码处理
    enable_admonition_processing: bool = True   # 告警框处理
```

## 🔧 转换流程

1. **内容处理**: 
   - 章节编号转换 (`# 第一章` → `\chapter{第一章}`)
   - 数学公式转换 (`$$...$$` → `\begin{equation}...\end{equation}`)
   - 代码块转换 (````python` → `\begin{lstlisting}[language=Python]`)
   - 图片转换 (`![](path)` → `\begin{figure}...\end{figure}`)
   - 告警框转换 (`!!! note` → `\begin{tcolorbox}`)

2. **Pandoc转换**: Markdown → LaTeX (.tex)

3. **XeLaTeX编译**: LaTeX → PDF

## 📊 输出文件

转换完成后，`output/` 目录包含：

```
output/
├── main.tex                   # 主LaTeX文件
├── main.pdf                   # 最终PDF文件
├── chapters/                  # 章节文件夹
│   ├── preface.tex           # 前言
│   ├── chapter01.tex         # 第1章
│   ├── chapter02.tex         # 第2章
│   └── ...                   # 其他章节
└── images/                    # 图片目录（自动创建）
```

## 🐛 故障排除

### 常见问题

**1. "Missing $ inserted" 错误**
- 原因: 源markdown中包含裸露的LaTeX命令
- 解决: 转换器会自动处理，确保数学处理器开启

**2. "Undefined control sequence \tightlist"**
- 原因: Pandoc生成命令但LaTeX不识别
- 解决: 转换器自动添加兼容性定义

**3. 中文字体问题**
- 原因: 系统缺少中文字体
- 解决: 安装Microsoft YaHei或修改配置中的字体设置

**4. 章节数量不正确**
- 原因: 章节文件命名或结构问题
- 解决: 检查 `source_dir` 中的文件结构

### 日志文件
转换过程中的详细日志保存在 `converter.log`，包含：
- 处理进度信息
- 错误详情
- 性能统计

---

**智慧水利教材转换器** - 让教材转换更简单、更可靠！