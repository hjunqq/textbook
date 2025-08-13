# 智慧水利平台架构与开发 - LaTeX教材项目

基于最佳实践构建的专业教材LaTeX项目，包含完整的Markdown到LaTeX转换工作流程。

## 📁 项目结构

```
publish/latex/
├── main.tex                    # 主文档文件
├── templates/                  # LaTeX模板配置
│   ├── basic-config.tex        # 基础配置和样式
│   ├── code-highlighting.tex   # 代码高亮配置
│   ├── enhanced-components.tex # 美化组件
│   ├── copyright.tex           # 版权页
│   ├── preface.tex            # 前言
│   ├── bibliography.tex       # 参考文献
│   ├── appendices.tex         # 附录
│   └── glossary.tex           # 术语表
├── chapters/                   # 章节内容
│   ├── chapter01/             # 第一章
│   ├── chapter02/             # 第二章
│   ├── ...                    # 其他章节
│   └── chapter08/             # 第八章
├── images/                     # 图片资源
├── convert-chapters.bat        # Markdown转换脚本
├── optimize-latex.bat         # LaTeX优化脚本
├── compile.bat                # 编译脚本
├── generate-book.bat          # 一键生成脚本
└── README.md                  # 项目说明
```

## 🚀 快速开始

### 环境要求

1. **Pandoc**: 用于Markdown转LaTeX
   - 下载: https://pandoc.org/installing.html
   - 版本要求: 2.0+

2. **XeLaTeX**: 用于编译PDF
   - Windows: MiKTeX (https://miktex.org/) 或 TeX Live (https://www.tug.org/texlive/)
   - 推荐使用TeX Live完整版

3. **字体**: 确保系统安装中文字体
   - SimSun (宋体)
   - SimHei (黑体)
   - FangSong (仿宋)

### 使用方法

#### 方法一：一键生成（推荐）
```bash
# 在Windows中运行
generate-book.bat
```

#### 方法二：分步操作
```bash
# 1. 转换Markdown到LaTeX
convert-chapters.bat

# 2. 编译PDF
compile.bat
```

#### 方法三：手动操作
```bash
# 1. 转换单个章节
pandoc ../../chapters/chapter01/section01-01.md -o chapters/chapter01/section01-01.tex --from=markdown --to=latex --standalone=false --listings

# 2. 编译主文档
xelatex main.tex
xelatex main.tex  # 第二次编译处理交叉引用
xelatex main.tex  # 第三次编译完善目录
```

## ✨ 特色功能

### 1. 基于最佳实践的模板系统
- **中文支持**: 使用ctex包，完美支持中文排版
- **代码高亮**: 支持多种编程语言的语法高亮
- **美化组件**: 学习目标、重要概念、技术要点等专业组件
- **现代化样式**: 水利行业主题色彩和专业排版

### 2. 自动化转换工具
- **Pandoc集成**: 自动将Markdown转换为LaTeX
- **批量处理**: 支持多章节同时转换
- **格式优化**: 自动优化生成的LaTeX代码

### 3. 完整的文档结构
- **封面设计**: 专业的书籍封面
- **版权信息**: 标准的版权页面
- **目录系统**: 自动生成图表和代码清单目录
- **索引系统**: 支持术语索引和交叉引用

## 📝 内容组织

### 章节结构
每个章节包含：
- 学习目标框
- 关键概念说明
- 技术要点总结
- 实践案例分析
- 本章小结

### 代码示例
支持以下编程语言的语法高亮：
- JavaScript/TypeScript
- Java
- Python
- SQL
- XML/HTML
- JSON/YAML
- Bash/Shell
- Docker

### 美化组件
- `learningobjectives`: 学习目标
- `keyoncept`: 关键概念
- `techpoint`: 技术要点
- `practicecase`: 实践案例
- `thinkingquestion`: 思考题
- `attention`: 注意事项
- `tip`: 提示信息

## 🛠️ 自定义配置

### 修改主题色彩
编辑 `templates/basic-config.tex`:
```latex
% 主色调配置
\definecolor{primarycolor}{RGB}{30, 130, 200}      % 水利蓝
\definecolor{secondarycolor}{RGB}{0, 102, 153}     % 深水蓝
\definecolor{accentcolor}{RGB}{40, 167, 69}        % 环保绿
```

### 添加新的美化组件
编辑 `templates/enhanced-components.tex`:
```latex
\newtcolorbox{newbox}[1][]{
    enhanced,
    title={\faIcon\ 标题},
    % 其他配置...
}
```

### 自定义字体
编辑 `templates/basic-config.tex`:
```latex
\setCJKmainfont{您的字体名称}
\setmainfont{Your English Font}
```

## 📊 输出格式

### PDF输出
- **高质量排版**: 适合印刷和电子阅读
- **交互式目录**: 支持PDF书签导航
- **图表编号**: 自动编号和交叉引用
- **代码高亮**: 彩色语法高亮

### 生成文件
- `main.pdf`: 主要输出文件
- `main.aux`, `main.toc`, `main.lof`, `main.lot`: 辅助文件（自动清理）

## 🔧 故障排除

### 常见问题

1. **编译失败 - 字体问题**
   - 确保安装了必需的中文字体
   - 检查字体名称是否正确

2. **Pandoc转换错误**
   - 检查Markdown语法是否正确
   - 确保文件编码为UTF-8

3. **XeLaTeX编译慢**
   - 首次编译会安装缺失的包，需要网络连接
   - 使用MiKTeX时选择自动安装包

4. **图片显示问题**
   - 确保图片文件存在
   - 检查图片路径是否正确
   - 支持的格式：PNG, JPG, PDF

### 日志查看
编译出错时，查看 `main.log` 文件：
```bash
# 查看最后50行日志
powershell "Get-Content main.log | Select-Object -Last 50"
```

## 📚 参考资源

- [LaTeX官方文档](https://www.latex-project.org/help/documentation/)
- [ctex包使用说明](https://github.com/CTeX-org/ctex-kit)
- [Pandoc用户手册](https://pandoc.org/MANUAL.html)
- [XeLaTeX用户指南](http://tug.org/xetex/)

## 🤝 贡献指南

1. 遵循现有的代码风格和结构
2. 测试所有修改是否能正常编译
3. 更新相关文档
4. 提交前进行完整测试

## 📄 许可证

本项目基于教育目的开发，请遵守相关版权规定。

---

**创建时间**: 2025年8月7日  
**版本**: v1.0  
**基于**: 智慧水利平台架构与开发教材  
**技术栈**: LaTeX + XeLaTeX + Pandoc + 最佳实践模板
