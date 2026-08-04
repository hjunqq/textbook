# 🚀 智慧水利教材转换器 - Windows版使用指南

## 🎯 问题解决

您遇到的问题是：**WSL环境无法直接调用Windows中的Pandoc和LaTeX**

## ✅ 解决方案

我为您创建了**Windows专用版本**，可以直接在Windows命令提示符中使用：

### 📁 新增文件
- `convert_windows.bat` - Windows批处理脚本  
- `core_win.py` - Windows环境专用Python脚本

## 🚀 使用方法

### 1. 在Windows命令提示符中运行

```batch
# 进入转换器目录
cd "D:\Projects\教材\智慧水利平台架构与开发\publish\clean_converter"

# 转换为PDF (默认)
convert_windows.bat

# 转换为LaTeX
convert_windows.bat latex
```

### 2. 系统要求检查

脚本会自动检查：
- ✅ Pandoc是否安装
- ✅ XeLaTeX是否安装 
- ✅ 源文件目录是否存在

### 3. 转换流程

1. **预处理阶段** (Python)
   - 发现和合并章节文件
   - 标准化标题格式
   - 统一图片路径并复制
   - 生成 `textbook_merged.md`

2. **转换阶段** (Windows Pandoc)
   - 使用Windows环境中的Pandoc
   - 支持中文字体和LaTeX包
   - 生成最终输出文件

## 📊 输出文件

转换完成后，在 `output/` 目录中：
- `textbook.pdf` - PDF教材 
- `textbook.tex` - LaTeX源码
- `textbook_merged.md` - 合并的Markdown
- `images/` - 统一的图片目录

## 🔧 故障排除

### 如果提示"Pandoc未安装"
1. 确认已从 https://pandoc.org/ 下载安装
2. 重启命令提示符
3. 运行 `pandoc --version` 验证

### 如果PDF转换失败
1. 确认已安装MiKTeX或TeX Live
2. 重启命令提示符  
3. 运行 `xelatex --version` 验证

### 如果找不到源文件
- 确认在 `clean_converter` 目录中运行脚本
- 检查 `../../docs/chapters/` 目录是否存在

## 🎉 优势

- **环境兼容** - 直接使用Windows中的工具
- **简单易用** - 一个命令完成转换
- **错误处理** - 详细的状态提示
- **路径修复** - 自动处理Windows路径

现在您可以直接在Windows中使用这个转换器了！