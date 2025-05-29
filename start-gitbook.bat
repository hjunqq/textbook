@echo off
echo 启动智慧水利平台架构与开发教材 GitBook
echo =====================================

echo 检查 Node.js 环境...
node --version >nul 2>&1
if errorlevel 1 (
    echo 错误：未找到 Node.js，请先安装 Node.js
    echo 下载地址：https://nodejs.org/
    pause
    exit /b 1
)

echo 检查 GitBook CLI...
gitbook --version >nul 2>&1
if errorlevel 1 (
    echo 正在安装 GitBook CLI...
    npm install -g gitbook-cli
)

echo 安装项目依赖...
call npm install

echo 安装 GitBook 插件...
call gitbook install

echo 启动 GitBook 服务...
echo 请在浏览器中访问 http://localhost:4000
call gitbook serve

pause 