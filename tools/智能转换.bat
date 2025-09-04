@echo off
chcp 65001
echo ====================================
echo 智能教材转换器
echo 基于Claude Code分析的改进版本
echo ====================================

echo.
echo 检查Python环境...
python --version
if %errorlevel% neq 0 (
    echo ❌ Python未安装或不在PATH中
    pause
    exit /b 1
)

echo.
echo 检查pandoc...
pandoc --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Pandoc未安装，请先安装Pandoc
    echo 下载地址: https://pandoc.org/installing.html
    pause
    exit /b 1
) else (
    echo ✅ Pandoc已安装
)

echo.
echo 🚀 开始智能转换...
python 智能转换器.py

echo.
echo 转换完成！查看output目录中的结果文件。
pause
