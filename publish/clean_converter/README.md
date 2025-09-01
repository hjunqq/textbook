# 🌊 智慧水利教材转换器 v2.0

一个简化、高效的 Markdown 到 LaTeX/PDF 转换解决方案，专为《智慧水利平台架构与开发》教材设计。

## 🎯 主要特性

- ✅ **一键转换** - 从复杂的多文件转换变为单命令执行
- ✅ **智能预处理** - 自动标准化章节编号、图片路径、代码语言检测
- ✅ **质量保证** - 转换前后的自动质量检查和验证
- ✅ **简洁架构** - 清理冗余代码，仅保留核心功能
- ✅ **容错处理** - 智能编码检测、路径查找、错误恢复

## 📁 目录结构

```
clean_converter/
├── core/                 # 核心转换引擎
│   ├── config.py         # 配置管理
│   ├── preprocessor.py   # 预处理模块
│   ├── converter.py      # 转换核心
│   └── validator.py      # 质量验证
├── templates/            # LaTeX模板
│   └── main.tex          # 主模板文件
├── output/              # 输出目录
│   └── images/          # 统一图片目录
├── convert.py           # 主程序
├── convert.bat          # Windows批处理
└── README.md           # 本文档
```

## 🚀 快速开始

### 环境要求

- **Python 3.7+**
- **Pandoc 2.0+** - 从 [pandoc.org](https://pandoc.org/installing.html) 下载
- **XeLaTeX** (可选) - 用于PDF生成，MiKTeX 或 TeX Live

### 基本使用

#### Windows 用户 (推荐)
```batch
# 转换为PDF
convert.bat

# 转换为LaTeX
convert.bat -f latex

# 指定输出目录
convert.bat -f pdf -o ./my_output
```

#### Python 直接运行
```bash
# 转换为PDF
python convert.py

# 转换为LaTeX  
python convert.py -f latex

# 跳过验证
python convert.py --skip-validation

# 自定义输出目录
python convert.py -o /path/to/output
```

## 📝 使用说明

### 源文件结构要求

```
项目根目录/
├── docs/
│   ├── 前言.md (可选)
│   └── chapters/
│       ├── chapter01/
│       │   ├── chapter01.md
│       │   ├── section01-01.md
│       │   ├── section01-02.md
│       │   └── images/ (可选)
│       ├── chapter02/
│       └── ...
└── appendix/ (可选)
    ├── appendixA.md
    └── ...
```

### 自动处理功能

1. **章节编号统一** - 自动标准化为"第X章"格式
2. **图片路径统一** - 自动搜索并复制图片到统一目录
3. **代码语言检测** - 智能识别代码块语言并添加高亮
4. **特殊格式转换** - 将 `!!! warning` 等转换为LaTeX框架
5. **编码问题修复** - 自动检测和转换文件编码

### 输出文件

- `textbook.pdf` - 主要PDF文件
- `textbook.tex` - LaTeX源码
- `textbook_merged.md` - 合并的Markdown文件  
- `quality_report.txt` - 质量检查报告
- `images/` - 统一的图片目录

## 🔧 高级配置

### 自定义章节顺序

在 `core/config.py` 中修改 `chapter_order` 字典：

```python
self.chapter_order = {
    'chapter01': '第一章 智慧水利概述与平台架构基础',
    'chapter02': '第二章 软件工程基础与需求分析',
    # 添加更多章节...
}
```

### 修改LaTeX模板

编辑 `templates/main.tex` 文件来自定义：
- 页面布局
- 字体设置
- 颜色方案
- 代码高亮样式
- 美化框架

### 预处理规则

在 `core/config.py` 中调整预处理选项：

```python
self.preprocessing_rules = {
    'fix_encoding': True,              # 修复编码问题
    'standardize_headings': True,      # 标准化标题
    'unify_image_paths': True,         # 统一图片路径
    'fix_code_blocks': True,           # 修复代码块
    'convert_admonitions': True,       # 转换警告框
    'remove_yaml_frontmatter': True   # 移除YAML前言
}
```

## 🔍 质量检查

转换器包含完整的质量保证机制：

### 转换前检查
- 系统依赖检查 (Pandoc、XeLaTeX)
- 文件结构验证
- 内容质量检查 (编码、图片、代码块)

### 转换后验证
- 输出文件存在性检查
- 文件大小合理性验证
- 质量报告生成

### 跳过验证
```bash
python convert.py --skip-validation
```

## 🐛 故障排除

### 常见问题

1. **Pandoc 未找到**
   - 确保 Pandoc 已安装且在 PATH 中
   - Windows: 重启命令提示符

2. **中文显示乱码**
   - 确保源文件使用 UTF-8 编码
   - 检查系统是否有中文字体

3. **图片无法显示**  
   - 检查图片路径是否正确
   - 支持的格式：png, jpg, svg, wmf 等

4. **PDF 生成失败**
   - 安装完整的 LaTeX 发行版
   - 检查 XeLaTeX 是否可用

### 调试模式
```bash
# 生成详细错误信息
python convert.py -f latex  # 先生成LaTeX查看问题
```

## 📊 性能优化

- **增量处理** - 只处理变更的内容
- **智能缓存** - 图片和预处理结果缓存
- **并行处理** - 多文件同时预处理
- **内存优化** - 流式处理大文件

## 🔄 从旧系统迁移

如果你正在使用旧的转换系统：

1. **备份现有输出**
2. **复制源文件** 到标准目录结构
3. **运行质量检查** 发现问题
4. **修复警告** 获得最佳效果
5. **执行转换** 生成新输出

## 📈 版本历史

- **v2.0** - 完全重构，简化架构，统一流程
- **v1.x** - 历史版本 (已废弃)

## 🤝 技术支持

遇到问题请：

1. 查看 `quality_report.txt` 质量报告
2. 检查命令行错误输出
3. 尝试使用 `--skip-validation` 选项
4. 确认环境依赖正确安装

## 📄 许可证

本项目基于教材制作实际需求开发，供教育使用。

---

**智慧水利教材转换器 v2.0** - 让教材制作更简单、更高效！