# 教材模板包使用指南

## 📋 概述

本教材模板包是基于《三维协同设计与BIM技术》教材制作过程中积累的宝贵经验整理而成，提供了从Markdown到LaTeX、PDF、Word的完整工作流程，以及质量控制体系。

## 📁 目录结构

```
教材模板包/
├── LaTeX模板/                    # LaTeX模板文件
│   ├── 基础配置模板.tex           # 基础文档配置
│   └── 代码高亮配置.tex           # 代码语法高亮配置
├── 转换脚本/                     # 自动化转换工具
│   ├── 通用教材转换器.py          # Python转换脚本
│   └── 通用转换.bat              # Windows批处理脚本
├── 质量控制/                     # 质量检查工具
│   └── 质量检查器.py             # 自动化质量检查
├── 示例项目/                     # 示例教材项目
└── README.md                    # 本使用指南
```

---

## 🚀 快速开始

### 1. 环境准备

#### 必需软件
- **Python 3.7+**: 运行转换脚本
- **Pandoc**: 格式转换核心工具
  - 下载: https://pandoc.org/installing.html
- **XeLaTeX**: PDF编译 (可选)
  - Windows: MiKTeX 或 TeX Live
  - 下载: https://miktex.org/ 或 https://www.tug.org/texlive/

#### 验证安装
```bash
python --version
pandoc --version
xelatex --version  # 可选
```

### 2. 项目设置

#### 复制模板包
```bash
# 将教材模板包复制到新项目目录
cp -r 教材模板包/* 我的新教材/
cd 我的新教材/
```

#### 创建项目结构
```
我的新教材/
├── 第一章/
│   ├── 1.1节内容.md
│   ├── 1.2节内容.md
│   └── images/
├── 第二章/
│   └── ...
├── LaTeX模板/           # 从模板包复制
├── 转换脚本/           # 从模板包复制
└── 质量控制/           # 从模板包复制
```

### 3. 基础转换

#### 方法一：使用批处理脚本 (推荐Windows用户)
```bash
# 转换为PDF
转换脚本\通用转换.bat . -f pdf

# 转换为Word
转换脚本\通用转换.bat . -f docx

# 指定输出目录
转换脚本\通用转换.bat . -f pdf -o 输出目录
```

#### 方法二：使用Python脚本
```bash
# 基础转换
python 转换脚本/通用教材转换器.py . -f pdf

# 高级选项
python 转换脚本/通用教材转换器.py . -f docx -o 输出 -c config.json
```

---

## 📝 内容编写规范

### Markdown文件结构

#### 标准文件名格式
```
第X章/
├── 前言.md              # 章节概述
├── X.1.md               # 第一节
├── X.2.md               # 第二节
├── 本章小结.md          # 章节总结
├── 思考题.md            # 练习题
└── images/              # 图片资源
```

#### 内容结构模板
```markdown
# 第X章 章节标题

## 学习目标
- 掌握...
- 理解...
- 能够...

## X.1 节标题

### X.1.1 子节标题

**重点概念**：概念解释...

### 代码示例

```csharp
// C# 代码示例
using System;
namespace Example
{
    public class Program
    {
        static void Main()
        {
            Console.WriteLine("Hello World!");
        }
    }
}
```

### 图片引用
![图片描述](images/示例图片.png)

## 本章小结
本章主要讲述了...

## 思考题
1. 请解释...
2. 如何实现...
```

### 代码块规范

#### 支持的语言标识
- `csharp` - C# 代码
- `javascript` - JavaScript 代码
- `python` - Python 代码
- `java` - Java 代码
- `sql` - SQL 查询
- `xml` - XML/HTML 标记
- `css` - CSS 样式
- `json` - JSON 数据
- `terminal` - 命令行
- `pseudocode` - 伪代码

#### 代码块最佳实践
```markdown
<!-- 好的代码块 -->
```csharp
// 添加必要的注释
using System;

namespace TextbookExample
{
    /// <summary>
    /// 示例类说明
    /// </summary>
    public class Example
    {
        public void DoSomething()
        {
            Console.WriteLine("示例输出");
        }
    }
}
```

<!-- 避免过长的代码块 -->
如果代码超过50行，考虑：
1. 拆分为多个小块
2. 重点突出关键部分
3. 使用伪代码简化
```

---

## 🎨 LaTeX模板定制

### 基础配置

#### 修改配色方案
```latex
% 在基础配置模板.tex中修改
\definecolor{primarycolor}{RGB}{52, 152, 219}    % 主色调
\definecolor{secondarycolor}{RGB}{230, 126, 34}  % 辅助色
\definecolor{accentcolor}{RGB}{39, 174, 96}      % 强调色

% 针对不同学科的建议配色：
% 工程类：蓝色系 (52, 152, 219)
% 管理类：绿色系 (39, 174, 96)
% 艺术类：橙色系 (230, 126, 34)
% 医学类：红色系 (231, 76, 60)
```

#### 添加自定义环境
```latex
% 添加到基础配置模板.tex中
\newcommand{\casestudy}[1]{
    \begin{tcolorbox}[
        colback=accentcolor!10,
        colframe=accentcolor,
        title=\faFileAlt\ 案例研究,
        fonttitle=\bfseries,
    ]
    #1
    \end{tcolorbox}
}
```

### 代码高亮定制

#### 添加新语言支持
```latex
% 在代码高亮配置.tex中添加
\lstdefinestyle{新语言}{
    language=基础语言,
    morekeywords={关键字1, 关键字2, ...},
    morecomment=[l]{注释符号},
    morestring=[b]"字符串引号",
    keywordstyle=\color{codeblue}\bfseries,
    commentstyle=\color{codegreen}\itshape,
    stringstyle=\color{codered},
}

% 添加快捷命令
\newcommand{\新语言code}[1]{\lstinline[style=新语言]!#1!}
```

---

## 🔧 转换脚本配置

### 配置文件 (config.json)

```json
{
    "input_format": "markdown",
    "output_format": "pdf",
    "template_dir": "LaTeX模板",
    "output_dir": "输出",
    "source_encoding": "utf-8",
    "latex_engine": "xelatex",
    "pandoc_options": [
        "--toc",
        "--number-sections",
        "--standalone",
        "--highlight-style=tango"
    ],
    "chapters": [],
    "preprocessing": {
        "fix_encoding": true,
        "standardize_format": true,
        "optimize_images": true,
        "fix_code_blocks": true
    },
    "postprocessing": {
        "optimize_latex": true,
        "fix_chinese_fonts": true,
        "add_listings_config": true,
        "beautify_layout": true
    }
}
```

### 自定义处理逻辑

#### 修改预处理
```python
# 在通用教材转换器.py中修改
def custom_preprocess(self, content):
    # 添加自定义的内容处理逻辑
    # 例如：特定格式转换、术语标准化等
    return content
```

---

## 🔍 质量控制

### 自动质量检查

#### 运行质量检查
```bash
# 检查整个项目
python 质量控制/质量检查器.py .

# 输出详细报告
python 质量控制/质量检查器.py . -o 质量报告.txt

# 生成JSON报告
python 质量控制/质量检查器.py . --json 质量报告.json
```

#### 质量标准配置
```python
# 在质量检查器.py中修改标准
self.standards = {
    'min_chapter_words': 2000,      # 最少字数
    'max_line_length': 100,         # 最大行长度
    'required_sections': [          # 必需章节
        '学习目标', 
        '本章小结', 
        '思考题'
    ],
    'code_style_patterns': {        # 代码模式检查
        'csharp': r'using\s+\w+;',
        'javascript': r'function\s+\w+\s*\(',
        # 添加更多语言模式...
    }
}
```

### 常见问题及解决方案

#### 编码问题
```markdown
问题：文件编码不是UTF-8
解决：使用文本编辑器重新保存为UTF-8编码

问题：中文显示乱码
解决：确保所有文件使用UTF-8编码，LaTeX中配置中文字体
```

#### 转换问题
```markdown
问题：Pandoc转换失败
解决：
1. 检查Markdown语法是否正确
2. 确保代码块正确闭合
3. 检查图片路径是否存在

问题：PDF编译失败
解决：
1. 安装完整的LaTeX发行版
2. 检查中文字体是否安装
3. 查看编译日志定位错误
```

#### 代码高亮问题
```markdown
问题：代码不显示高亮
解决：
1. 确保代码块有语言标识
2. 检查listings配置是否正确加载
3. 验证语言标识是否支持

问题：代码格式错乱
解决：
1. 检查代码缩进是否一致
2. 确保特殊字符正确转义
3. 调整listings参数设置
```

---

## 📚 高级功能

### 批量转换

#### 多项目批量处理
```batch
REM 创建批量转换脚本
@echo off
for /d %%i in (第*章) do (
    echo 转换章节: %%i
    python 转换脚本/通用教材转换器.py "%%i" -f pdf -o "输出/%%i"
)
```

#### 多格式同时输出
```python
# 修改转换脚本支持多格式
formats = ['latex', 'pdf', 'docx']
for fmt in formats:
    converter.convert(source_dir, fmt)
```

### 模板扩展

#### 创建学科专用模板
```latex
% 数学教材模板扩展
\usepackage{amsmath, amssymb, amsthm}
\newtheorem{theorem}{定理}[chapter]
\newtheorem{lemma}{引理}[chapter]
\newtheorem{proof}{证明}[chapter]

% 实验教材模板扩展
\newcommand{\experiment}[2]{
    \begin{tcolorbox}[title=实验 #1: #2]
    % 实验内容
    \end{tcolorbox}
}
```

### 自动化集成

#### Git Hooks集成
```bash
#!/bin/bash
# .git/hooks/pre-commit
echo "运行质量检查..."
python 质量控制/质量检查器.py .
if [ $? -ne 0 ]; then
    echo "质量检查失败，请修复问题后再提交"
    exit 1
fi
```

#### CI/CD流水线
```yaml
# .github/workflows/build.yml
name: 教材构建
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: 安装依赖
      run: |
        sudo apt-get install pandoc texlive-xetex
        pip install -r requirements.txt
    - name: 质量检查
      run: python 质量控制/质量检查器.py .
    - name: 构建教材
      run: python 转换脚本/通用教材转换器.py . -f pdf
    - name: 上传输出
      uses: actions/upload-artifact@v2
      with:
        name: 教材PDF
        path: 输出/*.pdf
```

---

## 🛠️ 故障排除

### 环境问题

#### Windows环境
```cmd
REM 检查Python安装
python --version
pip --version

REM 检查Pandoc安装
pandoc --version

REM 检查LaTeX安装
xelatex --version
```

#### 字体问题
```latex
% 检查系统字体
% Windows系统通常包含：
% SimSun (宋体)
% SimHei (黑体)  
% KaiTi (楷体)
% FangSong (仿宋)

% 如果字体缺失，下载安装或修改配置：
\setCJKmainfont{替代字体名称}
```

### 权限问题

#### 文件权限
```bash
# Linux/Mac环境
chmod +x 转换脚本/*.py
chmod +x 质量控制/*.py

# Windows环境
# 以管理员身份运行命令提示符
```

### 性能优化

#### 大文件处理
```python
# 分章节处理大教材
def process_large_textbook(chapters):
    for chapter in chapters:
        # 单独处理每章
        convert_chapter(chapter)
    # 合并结果
    merge_results()
```

---

## 📞 技术支持

### 常用资源
- **Pandoc文档**: https://pandoc.org/MANUAL.html
- **LaTeX教程**: https://www.overleaf.com/learn
- **tcolorbox包**: https://ctan.org/pkg/tcolorbox
- **listings包**: https://ctan.org/pkg/listings

### 问题反馈
如果遇到模板包相关问题，请：
1. 检查本使用指南相关部分
2. 运行质量检查工具诊断问题
3. 查看转换脚本的详细错误输出
4. 记录问题环境和复现步骤

---

**版本**: v2.0  
**更新时间**: 2025年8月7日  
**适用范围**: 大学教材编写与制作  
**基于经验**: 《三维协同设计与BIM技术》教材制作流程
