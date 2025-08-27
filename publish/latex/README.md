# 智慧水利平台架构与开发教材 - LaTeX版本

## 项目结构

```
publish/latex/
├── main.tex                    # 主LaTeX文件
├── templates/
│   └── basic-config.tex       # 基础配置和样式定义
├── chapters/                   # 章节文件夹
│   ├── preface.tex            # 前言
│   ├── chapter01.tex          # 第1章 - 智慧水利概述与平台架构基础
│   ├── chapter02.tex          # 第2章 - 软件工程基础与需求分析
│   ├── chapter03.tex          # 第3章 - 软件模块详细设计
│   ├── chapter04.tex          # 第4章 - 数据库设计与实现
│   ├── chapter05.tex          # 第5章 - Web开发框架与技术
│   ├── chapter06.tex          # 第6章 - 3S技术集成与应用
│   ├── chapter07.tex          # 第7章 - 系统测试与部署
│   ├── chapter08.tex          # 第8章 - 系统维护与优化
│   ├── chapter09.tex          # 第9章 - 发展趋势与展望
│   ├── appendixA.tex          # 附录A
│   ├── appendixB.tex          # 附录B
│   └── appendixC.tex          # 附录C
├── images/                     # 图片资源
├── build/                      # 编译辅助文件
├── output/                     # 输出PDF文件
├── build.sh                    # Linux/macOS编译脚本
├── build.bat                   # Windows编译脚本
├── quick-build.sh             # Linux/macOS快速编译脚本
├── quick-build.bat            # Windows快速编译脚本
├── clean.sh                   # Linux/macOS清理脚本
├── clean.bat                  # Windows清理脚本
└── README.md                  # 本文件
```

## 编译要求

### 必需软件
- **XeLaTeX**: 用于编译中文LaTeX文档
- **TeX Live** (推荐) 或 **MiKTeX**: LaTeX发行版

### 中文字体要求
确保系统安装了以下中文字体：
- SimSun (宋体)
- SimHei (黑体)  
- KaiTi (楷体)
- FangSong (仿宋)

## 编译方法

### Windows系统
1. **完整编译**（推荐）：
   ```cmd
   build.bat
   ```

2. **快速预览**：
   ```cmd
   quick-build.bat
   ```

3. **清理临时文件**：
   ```cmd
   clean.bat
   ```

### Linux/macOS系统
1. **完整编译**（推荐）：
   ```bash
   chmod +x build.sh
   ./build.sh
   ```

2. **快速预览**：
   ```bash
   chmod +x quick-build.sh
   ./quick-build.sh
   ```

3. **清理临时文件**：
   ```bash
   chmod +x clean.sh
   ./clean.sh
   ```

### 手动编译
如果脚本无法运行，可以手动执行：
```bash
# 创建输出目录
mkdir -p output

# 编译（需要运行3次以正确生成目录和交叉引用）
xelatex -interaction=nonstopmode -output-directory=output main.tex
xelatex -interaction=nonstopmode -output-directory=output main.tex
xelatex -interaction=nonstopmode -output-directory=output main.tex
```

## 输出结果
编译成功后，PDF文件将位于 `output/main.pdf`

## 自定义配置

### 模板特性
本教材LaTeX模板包含以下特性：
- 中文友好的字体配置
- 水利工程主题的配色方案
- 丰富的教学用框架（学习目标、关键概念、实践练习等）
- 代码高亮支持
- 数学公式和定理环境
- 图表自动编号和交叉引用

### 可用的特殊环境
- `\learningobjectives{}` - 学习目标框
- `\keypoints{}` - 关键概念框
- `\practiceexercise{}` - 实践练习框
- `\attention{}` - 注意事项框
- `\chaptersummary{}` - 章节摘要框

### 强调命令
- `\highlight{文本}` - 蓝色高亮强调
- `\important{文本}` - 红色重要强调
- `\note{文本}` - 橙色注释说明
- `\code{代码}` - 行内代码

## 故障排除

### 常见问题
1. **中文显示乱码**
   - 确保系统安装了所需的中文字体
   - 检查文件编码是否为UTF-8

2. **编译失败**
   - 检查XeLaTeX是否正确安装
   - 查看编译日志文件（build/logs/）
   - 尝试清理临时文件后重新编译

3. **图片无法显示**
   - 确保图片文件存在于指定路径
   - 检查图片格式是否受支持（PNG、JPG、PDF、SVG）

4. **目录或交叉引用错误**
   - 运行完整编译脚本（build.bat/build.sh）
   - LaTeX需要多次编译才能正确生成目录和交叉引用

### 获取帮助
如果遇到问题，请：
1. 查看编译日志文件
2. 确认LaTeX环境配置正确
3. 检查文件路径和编码

## 版本信息
- **版本**: v1.0
- **更新时间**: 2025年8月
- **兼容性**: XeLaTeX + TeX Live 2023+