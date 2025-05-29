# 🛠️ 故障排除指南

本文档记录了智慧水利教材部署过程中可能遇到的问题和解决方案。

## 🔧 已解决的问题

### 1. GitHub Actions 锁定文件兼容性错误

#### 问题描述
```
ERR_PNPM_NO_LOCKFILE  Cannot install with "frozen-lockfile" because pnpm-lock.yaml is absent
WARN  Ignoring not compatible lockfile at /home/runner/work/textbook/textbook/pnpm-lock.yaml
```

#### 根本原因
- 本地环境（Windows）和CI环境（Ubuntu）使用不同版本的pnpm
- 不同平台生成的锁定文件格式可能不兼容
- CI环境默认启用`frozen-lockfile`模式

#### 解决方案
在工作流中实现智能安装策略：
```yaml
- name: 📥 安装项目依赖
  run: |
    if [ -f "pnpm-lock.yaml" ]; then
      # 首先尝试使用锁定文件安装
      pnpm install --frozen-lockfile || {
        echo "⚠️ 锁定文件不兼容，使用灵活安装模式..."
        pnpm install --no-frozen-lockfile
      }
    else
      pnpm install
    fi
```

### 2. Node.js 18 与 GitBook 兼容性错误

#### 问题描述
```
TypeError: cb.apply is not a function
    at graceful-fs/polyfills.js:287:18
    at FSReqCallback.oncomplete (node:fs:203:5)
```

#### 根本原因
- GitBook 依赖的旧版本 `graceful-fs` 与 Node.js 18 不兼容
- `package.json` 中的 `install` 脚本仍在调用 `gitbook install`
- GitBook 项目已不再积极维护

#### 解决方案
1. **移除GitBook依赖**：
   ```json
   // 从 package.json 中移除
   "gitbook-cli": "^2.3.2"
   ```

2. **更新scripts为HonKit**：
   ```json
   {
     "scripts": {
       "serve": "honkit serve",
       "build": "honkit build",
       // 移除 "install": "honkit install" - HonKit不需要
       "pdf": "honkit pdf . ./output/智慧水利平台架构与开发.pdf"
     }
   }
   ```

3. **使用HonKit替代GitBook**：
   - HonKit 是 GitBook 的现代化替代品
   - 完全兼容 GitBook 的插件和配置
   - 支持 Node.js 18+

### 3. 工作流中的npm缓存配置错误

#### 问题描述
```
Error: Dependencies lock file is not found. Supported file patterns: package-lock.json,npm-shrinkwrap.json,yarn.lock
```

#### 根本原因
工作流配置了npm缓存但项目使用pnpm

#### 解决方案
移除npm缓存配置，使用pnpm专用缓存：
```yaml
- name: 🔧 配置 Node.js
  uses: actions/setup-node@v4
  with:
    node-version: '18'
    # 移除 cache: 'npm'
```

## 🚨 常见问题及解决方案

### 构建相关

#### Q: 构建时出现插件加载错误
```bash
error: plugin "xxx" not found
```

**解决方案：**
1. 检查 `book.json` 中的插件配置
2. 确保所有插件都在 `package.json` 中列出
3. 重新安装依赖：
   ```bash
   rm -rf node_modules pnpm-lock.yaml
   pnpm install
   ```

#### Q: 构建产物目录为空
**检查步骤：**
1. 确认构建命令执行成功
2. 检查 `_book` 目录是否生成
3. 验证 SUMMARY.md 文件格式正确

### 部署相关

#### Q: GitHub Pages 显示404
**解决方案：**
1. 确保 `.nojekyll` 文件存在于 `_book` 目录
2. 检查 GitHub Pages 设置选择了 "GitHub Actions"
3. 确认仓库是公开的或有GitHub Pro

#### Q: 页面样式丢失
**检查步骤：**
1. 确保相对路径正确
2. 检查浏览器控制台是否有资源加载错误
3. 清除浏览器缓存重试

### 本地开发

#### Q: 本地服务器启动失败
```bash
Error: listen EADDRINUSE :::4000
```

**解决方案：**
```bash
# 使用不同端口
pnpm exec honkit serve --port 3000

# 或者杀死占用进程
netstat -ano | findstr :4000  # Windows
kill -9 $(lsof -ti:4000)      # macOS/Linux
```

#### Q: 热重载不工作
**解决方案：**
1. 确保文件保存正确
2. 检查是否在正确的目录运行命令
3. 重启服务器

## 🔍 调试技巧

### 1. 本地调试流程
```bash
# 1. 清理环境
rm -rf node_modules pnpm-lock.yaml _book

# 2. 重新安装
pnpm install

# 3. 测试构建
pnpm exec honkit build

# 4. 检查产物
ls -la _book/

# 5. 本地预览
cd _book && python -m http.server 8000
```

### 2. GitHub Actions 调试
1. **查看详细日志**：点击失败的工作流查看具体错误
2. **使用 workflow_dispatch**：手动触发工作流测试
3. **添加调试输出**：在工作流中添加 `echo` 命令查看变量

### 3. 依赖问题诊断
```bash
# 检查依赖树
pnpm ls

# 审计安全问题
pnpm audit

# 检查过时依赖
pnpm outdated

# 验证锁定文件
pnpm install --frozen-lockfile
```

## 📚 预防措施

### 1. 版本固定
- 在 `package.json` 中使用精确版本号
- 定期更新依赖到最新稳定版本
- 保持 Node.js 版本与 CI 环境一致

### 2. 测试策略
- 本地构建测试后再推送
- 使用分支进行重大更改测试
- 定期检查部署状态

### 3. 文档维护
- 记录所有配置更改
- 保持故障排除文档更新
- 分享最佳实践

## 🔗 相关资源

- [HonKit 官方文档](https://github.com/honkit/honkit)
- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [pnpm 文档](https://pnpm.io/)
- [Node.js 兼容性指南](https://nodejs.org/en/about/releases/)

---

💡 **提示**：遇到新问题时，请先查看 GitHub Actions 的详细日志，然后尝试在本地复现问题。 