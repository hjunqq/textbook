# 智慧水利教材转换器 - 使用指南

## 📚 概述

智慧水利教材转换器是一个专业的文档转换工具，专门用于将 Markdown 格式的教材内容转换为多种输出格式（PDF、LaTeX、HTML、DOCX等）。该工具采用企业级架构设计，具备完整的质量控制、错误处理和进度监控功能。

### 🎯 主要特性

- **多格式支持**: PDF、LaTeX、HTML、DOCX、EPUB
- **智能预处理**: 自动标准化内容格式、修复常见问题
- **质量保证**: 全流程质量检查和验证
- **进度监控**: 实时转换进度和详细状态报告
- **模块化设计**: 可扩展的组件化架构
- **命令行接口**: 支持批处理和自动化集成
- **详细日志**: 完整的操作记录和错误诊断
- **图片处理**: 自动图片收集、转换和路径标准化

## 🚀 快速开始

### 环境要求

**系统要求:**
- Python 3.7+
- 操作系统: Windows/Linux/macOS

**必需依赖:**
- [Pandoc](https://pandoc.org/) - 文档转换引擎
- [XeLaTeX](https://www.xelatex.org/) - PDF生成引擎（可选，仅PDF输出需要）

### 基本使用

```bash
# 转换为PDF（默认）
python textbook_converter.py -i docs -o output

# 转换为LaTeX
python textbook_converter.py -i docs -o output -f latex

# 详细输出模式
python textbook_converter.py -i docs -o output -f pdf -v

# 指定章节转换
python textbook_converter.py -i docs -o output --chapters chapter01,chapter02
```

## 📁 目录结构要求

转换器要求输入目录具有以下标准结构：

```
input_directory/
├── 前言.md                    # 前言文件（可选）
├── chapters/                   # 章节目录
│   ├── chapter01/
│   │   ├── chapter01.md       # 章节主文件
│   │   ├── section01-01.md    # 节文件
│   │   ├── section01-02.md    # 节文件
│   │   └── images/            # 章节图片（可选）
│   ├── chapter02/
│   │   ├── chapter02.md
│   │   └── ...
│   └── images/                # 共享图片目录（可选）
└── appendix/                   # 附录目录（可选）
    ├── appendixA.md
    └── appendixB.md
```

### 文件命名规范

- **章节目录**: `chapter01`, `chapter02`, ..., `chapter99`
- **章节主文件**: `chapter01.md`, `chapter02.md`, ...
- **节文件**: `section01-01.md`, `section01-02.md`, ...
- **附录文件**: `appendixA.md`, `appendixB.md`, ...

## 🛠️ 命令行参数

### 必需参数

- `-i, --input`: 输入目录路径
- `-o, --output`: 输出目录路径

### 可选参数

- `-f, --format`: 输出格式 (pdf/latex/html/docx/epub，默认: pdf)
- `-t, --template`: 模板名称 (默认: default)
- `--chapters`: 指定转换的章节，逗号分隔
- `--no-toc`: 不生成目录
- `--no-numbers`: 不对章节编号
- `--no-quality-check`: 跳过质量检查
- `-v, --verbose`: 详细输出模式
- `--version`: 显示版本信息

## 📝 内容格式规范

### Markdown 规范

转换器支持标准 Markdown 语法，并额外支持以下扩展：

#### 1. 标题结构
```markdown
# 章节标题（自动编号）
## 节标题  
### 小节标题
#### 子小节标题
```

#### 2. 代码块
```markdown
\```python
def hello_world():
    print("Hello, World!")
\```
```

**支持的语言标识:**
- `python`, `javascript`, `java`, `sql`, `html`, `css`, `bash`, `json`
- 自动语言检测（当未指定语言时）

#### 3. 图片引用
```markdown
![图片描述](path/to/image.png)
![图片描述](./images/diagram.svg)
```

**支持的图片格式:**
- PNG, JPG, JPEG, GIF, SVG, BMP, WebP

#### 4. 提醒框语法
```markdown
!!! info "信息"
    这是一个信息提示框。

!!! warning "警告"
    这是一个警告提示框。
```

**支持的提醒框类型:**
- `info`, `warning`, `note`, `tip`, `important`, `danger`

## 🔍 质量控制

### 转换前检查

1. **系统环境检查**
   - Pandoc 安装和版本
   - XeLaTeX 可用性（PDF输出）

2. **输入结构验证**
   - 目录结构完整性
   - 必需文件存在性

3. **内容质量检查**
   - 文件编码问题
   - 图片引用完整性
   - 代码块语法正确性

### 质量等级评估

- **Excellent**: 无问题、无警告
- **Good**: 少量警告（≤3个）
- **Acceptable**: 中等警告（4-10个）
- **Poor**: 大量警告或少量错误
- **Failed**: 严重错误，无法转换

## 📊 进度监控

转换过程包含8个主要步骤：

1. **检查系统环境** (12.5%)
2. **验证输入结构** (25.0%)  
3. **检查内容质量** (37.5%)
4. **收集源文件** (50.0%)
5. **预处理内容** (62.5%)
6. **保存合并文件** (75.0%)
7. **执行格式转换** (87.5%)
8. **生成质量报告** (100.0%)

## 📄 输出文件

转换完成后，输出目录将包含：

```
output_directory/
├── textbook.pdf              # 主输出文件
├── textbook_merged.md        # 合并的Markdown文件
├── images/                   # 处理后的图片
│   ├── img_001.png
│   ├── img_002.svg
│   └── ...
├── conversion.log            # 详细转换日志
├── conversion_report.json    # 转换报告
└── quality_report.json       # 质量报告
```

## 🐛 常见问题与解决方案

### 1. Pandoc 相关问题

**问题**: `Pandoc未安装或不在PATH中`
**解决方案**:
```bash
# Ubuntu/Debian
sudo apt-get install pandoc

# macOS
brew install pandoc

# Windows - 从 https://pandoc.org/installing.html 下载安装
```

### 2. 编码问题

**问题**: `文件编码可能有问题`
**解决方案**:
- 确保所有Markdown文件使用UTF-8编码

### 3. 图片问题

**问题**: `图片文件未找到`
**解决方案**:
- 检查图片路径是否正确
- 确保图片文件存在于指定位置

### 4. 性能问题

**问题**: `转换速度慢`
**解决方案**:
- 使用 `--no-quality-check` 跳过详细质量检查
- 仅转换需要的章节 `--chapters chapter01,chapter02`

## 🧪 测试与验证

### 运行测试套件

```bash
# 运行所有测试
python test_converter.py

# 详细测试输出
python test_converter.py -v
```

## 📞 技术支持

### 获取帮助

- **命令行帮助**: `python textbook_converter.py --help`
- **测试问题**: `python test_converter.py -v`
- **版本信息**: `python textbook_converter.py --version`

---

**版本**: 3.0.0  
**更新时间**: 2025-01-01  
**维护者**: Claude Code Assistant