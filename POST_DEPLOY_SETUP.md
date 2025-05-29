# 📝 部署后配置指南

恭喜！您已经成功设置了智慧水利教材的自动部署系统。现在需要完成一些最终配置步骤。

## 🚀 GitHub 仓库设置

### 1. 上传代码到 GitHub

```bash
# 初始化 Git 仓库（如果还没有的话）
git init

# 添加所有文件
git add .

# 提交更改
git commit -m "🎉 智慧水利教材初始版本 - 支持GitHub Pages自动部署"

# 关联远程仓库（替换为您的实际仓库地址）
git remote add origin https://github.com/您的用户名/您的仓库名.git

# 推送到 GitHub
git push -u origin main
```

### 2. 配置 GitHub Pages

1. **进入仓库设置**
   - 访问您的GitHub仓库
   - 点击 `Settings` 选项卡

2. **配置 Pages**
   - 在左侧菜单中找到 `Pages`
   - 在 "Source" 部分选择 `GitHub Actions`
   - 保存设置

3. **等待首次部署**
   - 转到 `Actions` 页面
   - 观察工作流的运行状态
   - 首次部署可能需要几分钟

## 🔗 更新 README.md 链接

部署成功后，请更新 `README.md` 文件中的链接：

### 替换占位符

在 `README.md` 文件顶部，取消注释并替换以下内容：

```markdown
[![🚀 部署状态](https://github.com/您的用户名/您的仓库名/actions/workflows/deploy.yml/badge.svg)](https://github.com/您的用户名/您的仓库名/actions/workflows/deploy.yml)
[![📖 在线阅读](https://img.shields.io/badge/在线阅读-GitHub%20Pages-blue)](https://您的用户名.github.io/您的仓库名/)
[![📚 教材版本](https://img.shields.io/badge/版本-v1.0-green)](https://github.com/您的用户名/您的仓库名/releases)
```

### 更新在线访问地址

将以下部分：
```markdown
📖 **在线阅读地址**: 部署后将在GitHub Pages上提供访问链接
```

替换为：
```markdown
📖 **在线阅读地址**: [https://您的用户名.github.io/您的仓库名/](https://您的用户名.github.io/您的仓库名/)
```

### 更新其他链接

在联系方式部分，更新：
```markdown
- 🐛 问题反馈：[GitHub Issues](https://github.com/您的用户名/您的仓库名/issues)
- 💬 讨论交流：[GitHub Discussions](https://github.com/您的用户名/您的仓库名/discussions)
```

## 📊 验证部署

### 检查部署状态

1. **Actions 页面**
   - 确认工作流显示绿色 ✅
   - 查看部署日志确保无错误

2. **访问网站**
   - 打开 `https://您的用户名.github.io/您的仓库名/`
   - 确认所有功能正常工作

3. **测试功能**
   - ✅ 页面正常加载
   - ✅ 导航菜单可用
   - ✅ 搜索功能工作
   - ✅ 响应式设计（手机访问）
   - ✅ 代码高亮显示

## 🔧 自定义配置（可选）

### 自定义域名

如果您有自己的域名，可以配置：

1. **添加 CNAME 文件**
   ```bash
   echo "您的域名.com" > _book/CNAME
   ```

2. **修改工作流**
   在 `.github/workflows/deploy.yml` 中取消注释：
   ```yaml
   # echo "your-domain.com" > _book/CNAME
   ```
   并替换为您的实际域名。

3. **DNS 设置**
   - 在您的域名提供商处添加 CNAME 记录
   - 指向 `您的用户名.github.io`

### 添加谷歌分析

在 `book.json` 中添加：
```json
{
  "plugins": ["ga"],
  "pluginsConfig": {
    "ga": {
      "token": "您的谷歌分析ID"
    }
  }
}
```

### SEO 优化

在 `book.json` 中添加：
```json
{
  "title": "智慧水利平台架构与开发",
  "description": "为水利专业本科大三年级学生设计的智慧水利平台架构与开发教材",
  "author": "您的姓名",
  "language": "zh-hans"
}
```

## 🚨 常见问题解决

### 部署失败

1. **检查权限**
   - 确保仓库是公开的（或有 GitHub Pro）
   - 确认 Actions 权限已启用

2. **检查文件**
   - 确保 `pnpm-lock.yaml` 存在
   - 确保所有 Markdown 文件语法正确

3. **查看日志**
   - 在 Actions 页面点击失败的工作流
   - 查看详细错误信息

### 页面显示异常

1. **清除缓存**
   - 强制刷新浏览器 (Ctrl+F5)
   - 清除浏览器缓存

2. **检查文件**
   - 确保 `.nojekyll` 文件存在
   - 检查相对路径是否正确

## 📈 持续维护

### 内容更新流程

1. **本地修改**
   ```bash
   # 修改内容
   vim chapters/chapter01/section01-01.md
   
   # 本地预览
   pnpm exec honkit serve
   ```

2. **提交部署**
   ```bash
   git add .
   git commit -m "📝 更新第一章内容"
   git push origin main
   ```

3. **监控部署**
   - 查看 Actions 页面
   - 确认部署成功
   - 验证在线内容

### 版本管理

建议使用语义化版本：
```bash
# 创建版本标签
git tag -a v1.0.0 -m "首个正式版本"
git push origin v1.0.0

# 在 GitHub 上创建 Release
```

## 🎉 完成！

恭喜您成功部署了智慧水利教材！现在您拥有：

- 📚 **专业的在线教材**：完整的8章内容
- 🚀 **自动部署系统**：推送即更新
- 🔍 **强大的搜索功能**：全文检索
- 📱 **响应式设计**：多设备适配
- 🎨 **优雅的界面**：专业技术文档主题

## 📞 需要帮助？

如果在配置过程中遇到问题：

1. 查看 [DEPLOYMENT.md](DEPLOYMENT.md) 详细指南
2. 参考 GitHub Pages 官方文档
3. 在仓库中创建 Issue 寻求帮助

---

�� **开始分享您的智慧水利知识吧！** 