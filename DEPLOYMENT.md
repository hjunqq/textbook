# 📚 智慧水利教材部署指南

本文档介绍如何将《智慧水利平台架构与开发》教材部署到GitHub Pages。

## 🚀 自动部署配置

### 1. GitHub Pages 设置

1. **进入仓库设置**
   - 在GitHub仓库页面，点击 `Settings` 选项卡
   - 在左侧菜单中找到 `Pages` 选项

2. **配置部署源**
   - Source: 选择 `GitHub Actions`
   - 这将允许使用GitHub Actions工作流进行自动部署

3. **分支保护（可选）**
   - 如需保护主分支，可在 `Branches` 设置中配置分支保护规则

### 2. 工作流说明

工作流文件位于 `.github/workflows/deploy.yml`，包含以下特性：

#### 🔄 触发条件
- **自动触发**: 当代码推送到 `main` 分支时
- **手动触发**: 在 Actions 页面可手动运行工作流

#### 🛠️ 构建流程
1. **环境准备**
   - 使用 Ubuntu 最新版本
   - 配置 Node.js 18
   - 安装并配置 pnpm 8

2. **依赖管理**
   - 智能缓存 pnpm store 以加速构建
   - 使用 `pnpm install --frozen-lockfile` 确保依赖一致性

3. **站点构建**
   - 使用 `honkit build` 构建静态站点
   - 自动生成 `.nojekyll` 文件
   - 优化构建产物配置

4. **部署发布**
   - 自动上传构建产物到 GitHub Pages
   - 部署完成后显示访问地址

## 🔧 本地开发

### 启动开发服务器
```bash
# 安装依赖
pnpm install

# 启动本地服务器
pnpm exec honkit serve --port 4000

# 访问地址: http://localhost:4000
```

### 本地构建测试
```bash
# 构建静态站点
pnpm exec honkit build

# 预览构建产物
cd _book
python -m http.server 8000
# 访问地址: http://localhost:8000
```

## 📦 构建产物说明

构建后的静态站点包含：

- **HTML文件**: 所有章节和页面的HTML版本
- **CSS样式**: 响应式设计，支持移动端访问
- **JavaScript**: 搜索功能、导航交互、代码高亮
- **字体文件**: 优化的中文字体显示
- **图片资源**: 教材中的图表和示意图

## 🌐 访问地址

部署成功后，教材将在以下地址访问：
```
https://[username].github.io/[repository-name]/
```

例如：`https://yourname.github.io/smart-water-platform-book/`

## 📊 功能特性

### 🔍 搜索功能
- 全文搜索支持中文
- 实时搜索结果展示
- 快捷键支持 (Ctrl/Cmd + K)

### 📱 响应式设计
- 支持手机、平板、桌面访问
- 自适应布局和字体大小
- 触摸友好的交互设计

### 🎨 主题定制
- 专业的技术文档主题
- 代码高亮支持多种语言
- 数学公式渲染 (KaTeX)

### 📖 阅读体验
- 章节导航和目录
- 页面内跳转链接
- 代码复制功能
- 页面分割器

## 🔄 更新流程

### 内容更新
1. 在本地修改教材内容
2. 提交并推送到 `main` 分支
3. GitHub Actions 自动构建和部署
4. 几分钟后新内容即可在线访问

### 监控部署状态
- 在仓库的 `Actions` 页面查看工作流运行状态
- 绿色✅表示部署成功，红色❌表示部署失败
- 点击具体工作流可查看详细日志

## 🛠️ 故障排除

### 常见问题

1. **构建失败**
   - 检查 `package.json` 和 `pnpm-lock.yaml` 是否正确
   - 查看 Actions 日志中的错误信息
   - 确保所有 Markdown 文件语法正确

2. **页面无法访问**
   - 检查 GitHub Pages 设置是否正确
   - 确认仓库是公开的（或有 GitHub Pro）
   - 等待 DNS 传播（可能需要几分钟）

3. **样式显示异常**
   - 确保 `.nojekyll` 文件存在
   - 检查相对路径是否正确
   - 清除浏览器缓存

### 调试建议

1. **本地验证**
   ```bash
   # 本地构建测试
   pnpm exec honkit build
   
   # 检查构建产物
   ls -la _book/
   ```

2. **GitHub Actions 调试**
   - 在工作流中添加调试输出
   - 使用 `workflow_dispatch` 手动触发测试
   - 检查权限设置是否正确

## 📞 技术支持

如遇到问题，可以：

1. **查看文档**: 参考 HonKit 官方文档
2. **检查日志**: 查看 GitHub Actions 的详细日志
3. **社区支持**: 在 GitHub Issues 中寻求帮助

## 🎯 优化建议

### 性能优化
- 压缩图片资源以减少加载时间
- 使用 CDN 加速静态资源访问
- 启用浏览器缓存策略

### SEO优化
- 添加合适的 meta 标签
- 设置网站地图
- 优化页面标题和描述

### 用户体验
- 添加页面加载进度指示
- 实现离线访问支持
- 提供PDF下载选项

---

📚 **智慧水利平台架构与开发教材** - 为水利信息化人才培养贡献力量！ 