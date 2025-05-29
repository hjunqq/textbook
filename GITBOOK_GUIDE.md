# GitBook 迁移和使用指南

## 概述

本指南将帮助您完成从 MkDocs 到 GitBook 的迁移过程，以及如何使用 GitBook 构建和发布智慧水利平台架构与开发教材。

## 迁移完成的内容

### ✅ 已完成的迁移任务

1. **配置文件更新**
   - ✅ 更新 `book.json` - 添加了适合教材的插件和配置
   - ✅ 更新 `package.json` - 添加了 GitBook 相关脚本
   - ✅ 保持 `SUMMARY.md` 目录结构

2. **样式文件创建**
   - ✅ `styles/website.css` - 网站版本样式
   - ✅ `styles/ebook.css` - 电子书版本样式
   - ✅ `styles/pdf.css` - PDF 输出样式

3. **文档结构调整**
   - ✅ 将 `docs/chapters/` 复制到根目录 `chapters/`
   - ✅ 将 `docs/appendix/` 复制到根目录 `appendix/`
   - ✅ 将 `docs/assets/` 复制到根目录 `assets/`
   - ✅ 更新 `README.md` 作为 GitBook 首页

4. **数学公式支持**
   - ✅ 配置 `katex` 插件支持 LaTeX 数学公式
   - ✅ 保持现有的数学公式格式

5. **图片和资源**
   - ✅ 保持现有的 SVG 图片
   - ✅ 图片路径已适配 GitBook 结构

## 安装和使用

### 1. 环境准备

```bash
# 安装 Node.js (版本 >= 12)
# 访问 https://nodejs.org/ 下载安装

# 安装 GitBook CLI
npm install -g gitbook-cli

# 验证安装
gitbook --version
```

### 2. 项目初始化

```bash
# 在项目目录中安装依赖
npm install

# 安装 GitBook 插件
npm run install
# 或者
gitbook install
```

### 3. 本地开发

```bash
# 启动本地服务器（推荐）
npm run dev

# 或者分步执行
gitbook install
gitbook serve

# 访问 http://localhost:4000
```

### 4. 构建静态文件

```bash
# 构建静态网站
npm run build
# 或者
gitbook build

# 输出到 _book 目录
```

### 5. 导出电子书

```bash
# 创建输出目录
mkdir -p output

# 导出 PDF（需要安装 Calibre）
npm run pdf

# 导出 EPUB
npm run epub

# 导出 MOBI
npm run mobi
```

## GitBook 插件功能

### 已配置的插件

1. **sharing-plus** - 社交分享功能
2. **expandable-chapters** - 可展开章节
3. **chapter-fold** - 章节折叠
4. **splitter** - 侧边栏大小调整
5. **copy-code-button** - 代码复制按钮
6. **anchor-navigation-ex** - 锚点导航
7. **highlight** - 代码高亮
8. **katex** - 数学公式支持
9. **search-pro** - 增强搜索
10. **github** - GitHub 集成
11. **edit-link** - 编辑链接
12. **page-toc-button** - 页面目录
13. **back-to-top-button** - 返回顶部
14. **advanced-emoji** - 表情符号支持

### 插件配置说明

```json
{
  "katex": {
    // 支持 LaTeX 数学公式
    // 行内公式：\\( formula \\)
    // 块级公式：\\[ formula \\]
  },
  "anchor-navigation-ex": {
    // 浮动目录导航
    "mode": "float",
    "showGoTop": true
  },
  "github": {
    // GitHub 仓库链接
    "url": "https://github.com/yourname/smart-water-platform-book"
  }
}
```

## 数学公式使用

GitBook 支持 KaTeX 渲染数学公式：

### 行内公式
```markdown
这是行内公式：\\(E = mc^2\\)
```

### 块级公式
```markdown
\\[
\\frac{\\partial u}{\\partial t} = \\alpha \\nabla^2 u
\\]
```

### 复杂公式示例
```markdown
\\[
m_p = \\sqrt{\\frac{\\sum_{i=1}^{n}((\\Delta x_i)^2 + (\\Delta y_i)^2)}{n}}
\\]
```

## 样式自定义

### 网站样式 (styles/website.css)
- 图片样式优化
- 代码块样式
- 表格样式
- 水利专业术语高亮

### 电子书样式 (styles/ebook.css)
- 适合阅读的字体设置
- 分页控制
- 脚注样式

### PDF 样式 (styles/pdf.css)
- A4 页面设置
- 页眉页脚
- 打印优化

## 部署选项

### 1. GitHub Pages
```bash
# 构建静态文件
npm run build

# 部署到 gh-pages 分支
git subtree push --prefix=_book origin gh-pages
```

### 2. GitBook.com
1. 连接 GitHub 仓库
2. 自动构建和发布
3. 支持域名绑定

### 3. Netlify/Vercel
1. 连接 Git 仓库
2. 设置构建命令：`gitbook build`
3. 设置发布目录：`_book`

## 常见问题

### 1. 插件安装失败
```bash
# 清理缓存
rm -rf node_modules
npm cache clean --force

# 重新安装
npm install
gitbook install
```

### 2. 数学公式不显示
- 确保使用 `\\(` 和 `\\)` 包围行内公式
- 确保使用 `\\[` 和 `\\]` 包围块级公式
- 检查 `katex` 插件是否正确安装

### 3. 图片路径问题
- 确保图片路径相对于根目录
- 检查 `assets/` 目录是否在根目录
- 验证图片文件是否存在

### 4. 中文字体问题
- PDF 导出需要系统支持中文字体
- 可以在 CSS 中指定字体 fallback

## 与 MkDocs 的差异

| 特性 | MkDocs | GitBook |
|------|--------|---------|
| 配置文件 | mkdocs.yml | book.json |
| 文档结构 | docs/ 目录 | 根目录 |
| 数学公式 | pymdownx.arithmatex | katex 插件 |
| 主题系统 | Material 主题 | 内置主题 + 插件 |
| 构建命令 | mkdocs build | gitbook build |
| 本地服务 | mkdocs serve | gitbook serve |

## 文件清理

如果需要清理迁移过程中的临时文件：

```bash
# 清理构建文件
npm run clean

# 手动清理
rm -rf _book
rm -rf node_modules
```

## 下一步计划

1. **内容检查** - 验证所有章节内容是否正确显示
2. **链接修复** - 检查内部链接是否正常工作
3. **样式优化** - 根据实际效果调整 CSS 样式
4. **部署配置** - 设置自动化部署流程
5. **域名绑定** - 配置自定义域名（如需要）

## 技术支持

如遇到问题，可以：
1. 查看 GitBook 官方文档：https://docs.gitbook.com/
2. 检查插件文档和 GitHub issues
3. 参考本指南的常见问题部分

---

**开始使用：**
```bash
npm run dev
```

然后访问 http://localhost:4000 查看效果。 