# 智慧水利教材转换工具

这个目录包含了用于将Markdown教材转换为PDF、LaTeX和Word格式的工具。

## 文件说明

### 核心工具
- `convert_complete.bat` - **推荐使用** 完整转换脚本，包含所有章节小节，修复格式问题
- `merge_chapters.py` - Python合并工具，智能处理admonition和格式
- `test_merge.bat` - 测试合并功能
- `convert_final.bat` - 旧版转换脚本（仅章节主文件）

### 配置文件
- `test-config.yaml` - 单章节测试用的Pandoc配置
- `test_single_chapter.md` - 测试用的示例章节

## 使用方法

### 1. 环境测试（推荐先运行）
```bash
cd tools
test_minimal.bat     # 基础功能测试
test_fixed.bat       # 配置文件测试
```

### 2. 转换完整教材（推荐）
```bash
cd tools
test_merge.bat       # 测试Python合并功能
convert_complete.bat # 生成包含所有章节小节的完整教材
```

## 输出文件

转换完成后，文件将保存在 `output` 目录中：
- `智慧水利教材.pdf` - PDF格式教材
- `智慧水利教材.tex` - LaTeX源文件
- `智慧水利教材.docx` - Word格式教材
- `merged_textbook.md` - 合并后的Markdown文件

## 环境要求

- Windows 操作系统
- Pandoc (https://pandoc.org/)
- XeLaTeX (推荐使用 TeX Live 或 MiKTeX)
- Python 3.x (可选，用于预处理)

## 故障排除

如果遇到问题：
1. 确保Pandoc和XeLaTeX已正确安装并添加到PATH
2. 检查中文字体是否已安装（Microsoft YaHei）
3. 运行 `test_single.bat` 先测试单章节转换