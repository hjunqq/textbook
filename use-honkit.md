# 使用 HonKit 替代 GitBook

## 问题说明

GitBook CLI 在新版本的 Node.js（v18+）中存在兼容性问题，主要是由于依赖的 graceful-fs 模块版本过旧。虽然我们已经修复了这些问题，但为了获得更好的稳定性和现代化的体验，推荐使用 **HonKit** 作为替代方案。

## HonKit 简介

HonKit 是 GitBook 的现代化分支，专门为解决 GitBook 的兼容性问题而创建，它：
- ✅ 完全兼容 GitBook 的配置和内容
- ✅ 支持最新版本的 Node.js
- ✅ 持续维护和更新
- ✅ 更好的性能和稳定性

## 快速切换到 HonKit

### 1. 安装 HonKit

```bash
# 全局安装 HonKit
npm install -g honkit

# 或者使用 pnpm
pnpm add -g honkit
```

### 2. 验证安装

```bash
honkit --version
```

### 3. 使用 HonKit 命令

HonKit 的命令与 GitBook 完全相同：

```bash
# 安装插件
honkit install

# 启动本地服务
honkit serve

# 构建静态网站
honkit build

# 导出 PDF
honkit pdf . output/智慧水利平台架构与开发.pdf
```

### 4. 更新 package.json 脚本

```json
{
  "scripts": {
    "serve": "honkit serve",
    "build": "honkit build",
    "install": "honkit install",
    "pdf": "honkit pdf . ./output/智慧水利平台架构与开发.pdf",
    "epub": "honkit epub . ./output/智慧水利平台架构与开发.epub",
    "dev": "npm run install && npm run serve"
  }
}
```

## 快速启动步骤

### 方法1：直接使用 HonKit

```bash
# 1. 安装 HonKit（如果还没安装）
npm install -g honkit

# 2. 安装插件
honkit install

# 3. 启动服务
honkit serve

# 访问 http://localhost:4000
```

### 方法2：使用项目已有的配置

由于您的项目 `package.json` 中已经包含了 `honkit` 依赖，可以直接使用：

```bash
# 使用项目本地的 HonKit
npx honkit serve

# 或者
pnpm exec honkit serve
```

## 优势对比

| 特性 | GitBook CLI | HonKit |
|------|-------------|---------|
| Node.js 兼容性 | 需要修复 | 原生支持 |
| 维护状态 | 停止维护 | 积极维护 |
| 性能 | 一般 | 更好 |
| 插件支持 | 完整 | 完整 |
| 配置兼容性 | - | 100% |

## 立即体验

让我们现在就用 HonKit 启动您的教材：

```bash
# 快速启动命令
npx honkit serve
```

然后访问 http://localhost:4000 查看效果！

## 配置说明

您当前的 `book.json` 配置完全兼容 HonKit，无需任何修改。所有的插件、样式、数学公式支持都会正常工作。

## 结论

HonKit 是目前最好的 GitBook 替代方案，推荐您：
1. 🔄 **立即切换**：使用 `npx honkit serve` 启动
2. 📦 **更新脚本**：将 package.json 中的 gitbook 命令改为 honkit
3. 🗑️ **卸载 GitBook CLI**：`npm uninstall -g gitbook-cli`（可选）

这样您就能享受到现代化、稳定的文档构建体验！ 