#!/bin/bash

echo "启动智慧水利平台架构与开发教材 GitBook"
echo "====================================="

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "错误：未找到 Node.js，请先安装 Node.js"
    echo "下载地址：https://nodejs.org/"
    exit 1
fi

echo "Node.js 版本：$(node --version)"

# 检查 GitBook CLI
if ! command -v gitbook &> /dev/null; then
    echo "正在安装 GitBook CLI..."
    npm install -g gitbook-cli
fi

echo "GitBook CLI 版本：$(gitbook --version)"

# 安装项目依赖
echo "安装项目依赖..."
npm install

# 安装 GitBook 插件
echo "安装 GitBook 插件..."
gitbook install

# 启动 GitBook 服务
echo "启动 GitBook 服务..."
echo "请在浏览器中访问 http://localhost:4000"
gitbook serve 